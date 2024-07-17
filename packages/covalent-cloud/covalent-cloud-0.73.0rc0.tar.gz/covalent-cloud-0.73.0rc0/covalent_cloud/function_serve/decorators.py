# Copyright 2024 Agnostiq Inc.

import inspect

from covalent_cloud.function_serve.common import SupportedMethods
from covalent_cloud.function_serve.service_class import FunctionService
from covalent_cloud.shared.classes.exceptions import InsufficientMemoryError
from covalent_cloud.shared.classes.settings import settings

__all__ = [
    "service",
]


def service(
    executor=None, name="", description="", auth=None, tags=[], compute_share=1, volume=None
):
    if (
        executor is not None
        and executor.memory < settings.function_serve.min_executor_memory_gb * 1024
    ):
        raise InsufficientMemoryError(int(executor.memory / 1024))

    def service_decorator(func):
        def internal_wrapper(executor, name, description, auth, tags, compute_share, volume):
            return FunctionService(
                func,
                executor,
                name,
                description,
                auth,
                tags,
                compute_share,
                volume,
                _main_func=func,
            )

        return internal_wrapper(executor, name, description, auth, tags, compute_share, volume)

    return service_decorator


def op_internal_wrapper_generator(
    route,
    executor,
    name,
    streaming,
    description,
    auth,
    tags,
    compute_share,
    op,
):
    fs_instance = service(executor, name, description, auth, tags, compute_share)(None)

    # Get the correct method from the FunctionService class, e.g. _get, _post, _put, etc.
    op_func = getattr(fs_instance, "_" + op.value.lower())

    def internal_wrapper(func):

        # Set the function service instance attributes since there is no init_func function
        fs_instance.func_name = func.__name__
        fs_instance.name = fs_instance.name or func.__name__
        fs_instance.func_source = inspect.getsource(func)
        fs_instance.func_description = description or func.__doc__ or ""
        fs_instance._main_func = func

        # Register the route and the method function and return the FunctionService instance
        return op_func(route, name, description, streaming)(func)

    return internal_wrapper


def get_decorator(
    route,
    executor=None,
    name=None,
    streaming=False,
    description=None,
    auth=None,
    tags=None,
    compute_share=None,
):
    return op_internal_wrapper_generator(
        route,
        executor,
        name,
        streaming,
        description,
        auth,
        tags,
        compute_share,
        SupportedMethods.GET,
    )


def post_decorator(
    route,
    executor=None,
    name=None,
    streaming=False,
    description=None,
    auth=None,
    tags=None,
    compute_share=None,
):

    return op_internal_wrapper_generator(
        route,
        executor,
        name,
        streaming,
        description,
        auth,
        tags,
        compute_share,
        SupportedMethods.POST,
    )


def put_decorator(
    route,
    executor=None,
    name=None,
    streaming=False,
    description=None,
    auth=None,
    tags=None,
    compute_share=None,
):

    return op_internal_wrapper_generator(
        route,
        executor,
        name,
        streaming,
        description,
        auth,
        tags,
        compute_share,
        SupportedMethods.PUT,
    )


def delete_decorator(
    route,
    executor=None,
    name=None,
    streaming=False,
    description=None,
    auth=None,
    tags=None,
    compute_share=None,
):

    return op_internal_wrapper_generator(
        route,
        executor,
        name,
        streaming,
        description,
        auth,
        tags,
        compute_share,
        SupportedMethods.DELETE,
    )


def patch_decorator(
    route,
    executor=None,
    name=None,
    streaming=False,
    description=None,
    auth=None,
    tags=None,
    compute_share=None,
):

    return op_internal_wrapper_generator(
        route,
        executor,
        name,
        streaming,
        description,
        auth,
        tags,
        compute_share,
        SupportedMethods.PATCH,
    )


# Assigning the decorators to the service function

# We still do this instead of directly using `op_internal_wrapper_generator`
# so that the correct supported arguments are shown when something like autocompletion is used
service._get = get_decorator
service._post = post_decorator
service._put = put_decorator
service._delete = delete_decorator

# This is the one that will be used by the user
service.endpoint = post_decorator
