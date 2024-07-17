# Copyright 2024 Agnostiq Inc.

import typing

from covalent_cloud.function_serve.assets import AssetsMediator
from covalent_cloud.function_serve.common import wait_for_deployment_to_be_active
from covalent_cloud.function_serve.models import Deployment
from covalent_cloud.service_account_interface.client import get_deployment_client
from covalent_cloud.shared.schemas.volume import Volume
from typing import Union, Callable

if typing.TYPE_CHECKING:
    from covalent_cloud.function_serve.service_class import FunctionService

__all__ = [
    "deploy",
    "get_deployment",
]


def deploy(function_service: "FunctionService", volume: Volume = None) -> Callable:
    """
    Deploy a function service to the cloud.
    """

    def deploy_wrapper(*args, **kwargs) -> Deployment:

        if volume is not None:
            # Override the volume for the function service
            function_service.volume = volume

        fn_service_model = function_service.get_model(*args, **kwargs)

        assets_mediator = AssetsMediator()
        fn_service_model = assets_mediator.hydrate_assets_from_model(fn_service_model)

        assets_mediator.upload_all()

        dumped_model = fn_service_model.model_dump()

        deployment_client = get_deployment_client()
        response = deployment_client.post(
            "/functions",
            request_options={
                "json": dumped_model,
            },
        )

        deployment = Deployment.from_function_record(response.json())

        # Attach route methods for ease of use
        deployment.attach_route_methods()

        return deployment

    return deploy_wrapper


def get_deployment(function_id: Union[str, Deployment], wait=False) -> Deployment:
    """
    Get the deployment info for a function service.
    """

    if isinstance(function_id, Deployment):
        function_id = function_id.function_id

    deployment_client = get_deployment_client()
    response = deployment_client.get(f"/functions/{function_id}")
    deployment = Deployment.from_function_record(response.json())

    # Attach route methods for ease of use
    deployment.attach_route_methods()

    if wait:
        return wait_for_deployment_to_be_active(deployment)
    return deployment
