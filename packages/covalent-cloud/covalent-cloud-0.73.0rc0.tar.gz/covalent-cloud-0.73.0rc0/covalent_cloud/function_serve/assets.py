# Copyright 2024 Agnostiq Inc.

from concurrent.futures import ThreadPoolExecutor, wait
from typing import Generic, List, TypeVar

import covalent as ct
import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from covalent_cloud.function_serve.common import ServeAssetType
from covalent_cloud.function_serve.models import ServeAsset
from covalent_cloud.service_account_interface.client import get_deployment_client

_upload_executor = ThreadPoolExecutor()


ModelType = TypeVar("ModelType", bound=BaseModel)


class AssetsMediator(Generic[ModelType]):

    serve_assets: List[ServeAsset] = []

    def __init__(self) -> None:
        self.serve_assets = []

    def hydrate_assets_from_model(self, model) -> ModelType:
        """
        Add serve asset ids and pre-signed urls to any pydantic model with ServeAsset fields.

        Args:
            model: A pydantic model that has ServeAsset fields.

        Returns:
            A new instance of the model with ServeAsset fields populated with ids and pre-signed urls.
        """
        _model_dump = model.model_dump()
        deployment_client = get_deployment_client()

        def find_and_replace_serialized_assets(data):
            if isinstance(data, dict):

                if (type_ := data.get("type")) and type_ in [
                    ServeAssetType.ASSET,
                    ServeAssetType.JSON,
                ]:
                    serve_asset = ServeAsset(**data)
                    self.serve_assets.append(serve_asset)
                    return serve_asset

                return {
                    key: find_and_replace_serialized_assets(value)
                    for key, value in data.items()
                }

            if isinstance(data, list):
                return [find_and_replace_serialized_assets(item) for item in data]

            return data

        new_schema = find_and_replace_serialized_assets(_model_dump)

        res = deployment_client.post(
            "/assets", request_options={"params": {"n": len(self.serve_assets)}}
        )
        presigned_assets = res.json()

        for serve_asset in self.serve_assets:
            asset = presigned_assets.pop()
            serve_asset.url = asset.get("url")
            serve_asset.id = asset.get("id")

        return type(model)(**new_schema)

    def upload_all(self):
        """
        Upload all ServeAssets to the cloud.
        """
        _upload_futures = []

        serve_assets = self.serve_assets
        for serve_asset in serve_assets:
            fut = _upload_executor.submit(AssetsMediator.upload_asset, serve_asset)
            _upload_futures.append(fut)

        done_futures, not_done_futures = wait(_upload_futures)

        self.serve_assets = []

        # ensure all futures are done and raise any exceptions if any
        for fut in done_futures:
            try:
                fut.result()
            except Exception as e:
                raise e

        for fut in not_done_futures:
            try:
                fut.result()
            except Exception as e:
                raise e

    @staticmethod
    def upload_asset(asset: ServeAsset) -> None:
        url = asset.url

        if url is None:
            deployment_client = get_deployment_client()
            res = deployment_client.post("/assets")
            presigned_urls = res.json()
            asset.url = presigned_urls[0]["url"]
            asset.id = presigned_urls[0]["id"]

        if asset.type == ServeAssetType.ASSET:
            transportable_object: ct.TransportableObject = ct.TransportableObject.deserialize(
                asset.serialized_object
            )
            data: bytes = transportable_object.serialize()

        elif asset.type == ServeAssetType.JSON:
            # No need to pickle this.
            data: bytes = asset.serialized_object

        else:
            raise ValueError(f"Unsupported asset type: '{asset.type}'")

        retry_strategy = Retry(
            total=5,
            backoff_factor=0.1,
            allowed_methods={"PUT"},
        )
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        r = session.put(asset.url, data=data)
        r.raise_for_status()

        asset.url = None
        asset.serialized_object = None
