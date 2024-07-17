# Copyright 2023 Agnostiq Inc.


from importlib import metadata

from . import cloud_executor
from .cloud_executor.cloud_executor import CloudExecutor
from .dispatch_management import cancel, dispatch, get_result, redispatch
from .qelectron_sdk.executors import CloudQCluster
from .service_account_interface.auth_config_manager import get_api_key, save_api_key
from .service_account_interface.client import get_client
from .shared.classes.settings import settings
from .swe_management.secrets_manager import delete_secret, list_secrets, store_secret
from .swe_management.swe_manager import create_env, get_envs, delete_env
from .volume.volume import volume
from .function_serve.deployment import deploy, get_deployment
from .function_serve.models import Deployment
from .function_serve.decorators import service

__version__ = metadata.version("covalent_cloud")

__all__ = [
    "cloud_executor",
    "CloudExecutor",
    "CloudQCluster",
    "cancel",
    "dispatch",
    "get_result",
    "redispatch",
    "get_api",
    "save_api_key",
    "get_client",
    "settings",
    "delete_secret",
    "list_secrets",
    "store_secret",
    "create_env",
    "get_envs",
    "delete_env",
    "volume",
    "deploy",
    "get_deployment",
    "Deployment",
    "service",
]
