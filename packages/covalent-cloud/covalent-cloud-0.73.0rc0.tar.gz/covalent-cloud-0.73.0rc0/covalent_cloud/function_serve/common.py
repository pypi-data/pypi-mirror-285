# Copyright 2024 Agnostiq Inc.

import time
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from covalent_cloud.function_serve.models import Deployment

__all__ = [
    "DEPLOY_ELECTRON_PREFIX",
    "SupportedMethods",
    "ServiceStatus",
    "rename",
    "wait_for_deployment_to_be_active",
]


DEPLOY_ELECTRON_PREFIX = "#__deploy_electron__#"

# 180 retries * 20 seconds = 3600 seconds = 60 minutes
ACTIVE_DEPLOYMENT_RETRIES = 180
ACTIVE_DEPLOYMENT_POLL_INTERVAL = 20


class SupportedMethods(str, Enum):
    """Supported HTTP methods for a function service."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ServiceStatus(str, Enum):
    """Possible statuses for a function service."""

    NEW_OBJECT = "NEW_OBJECT"
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"


class ServeAssetType(str, Enum):
    """Possible types for the ServeAsset `type` field."""

    ASSET = "Asset"
    JSON = "JSON"


def rename(name):
    def decorator(fn):
        fn.__name__ = name
        return fn

    return decorator


def wait_for_deployment_to_be_active(
    deployment: "Deployment", verbose=False
) -> "Deployment":
    """Repeatedly reload the deployment and handle status updates."""

    retries_done = 0
    waiting_statuses = [ServiceStatus.NEW_OBJECT, ServiceStatus.CREATING]
    deployment.reload()

    while deployment.status in waiting_statuses:

        if retries_done == ACTIVE_DEPLOYMENT_RETRIES:
            elapsed = ACTIVE_DEPLOYMENT_RETRIES * ACTIVE_DEPLOYMENT_POLL_INTERVAL / 60
            raise TimeoutError(
                f"Timed out after {elapsed} minutes while waiting for the "
                "deployment to become active"
            )

        if verbose:
            print(f"Deployment status: {deployment.status!s}")

        time.sleep(ACTIVE_DEPLOYMENT_POLL_INTERVAL)

        deployment.reload()
        retries_done += 1

    # Reload to ensure any error logs are included.
    deployment.reload()

    return deployment
