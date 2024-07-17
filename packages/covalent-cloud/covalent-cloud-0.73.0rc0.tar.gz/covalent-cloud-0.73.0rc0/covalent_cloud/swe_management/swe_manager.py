# Copyright 2023 Agnostiq Inc.

"""Software environment management module."""

import base64
import json
import sys
import tempfile
import time
from typing import Dict, List, Optional, Tuple, Union

import requests
import yaml

from covalent_cloud import get_client
from covalent_cloud.shared.classes.helpers import check_env_is_ready
from covalent_cloud.shared.classes.settings import Settings, settings
from covalent_cloud.swe_management.models.environment import EnvironmentRuntimeConfig, BaseImageConfig, Environment

from ..shared.classes.exceptions import CovalentAPIKeyError, CovalentGenericAPIError


__all__ = [
    "create_env",
    "get_envs",
    "delete_env",
]


def get_pip_pkgs(pip: Union[str, List[str]]) -> List[str]:
    """
    Unpacks the pip packages in the requirements.txt file and combines it into a list of required pip packages.

    """

    if not isinstance(pip, list):
        pip = [pip]

    pip_pkgs = []
    for pkg in pip:
        if pkg.endswith(".txt"):
            with open(pkg, "r") as f:
                pip_pkgs += f.read().splitlines()
        else:
            pip_pkgs.append(pkg)

    return pip_pkgs


def unpack_conda_pkgs(
    conda: Union[str, List[str], Dict[str, List[str]]]
) -> Tuple[List[str], List[str]]:
    """
    Unpacks the conda packages in the environment.yml file and combines it into a dictionary of required conda packages.

    Returns:
        channels, dependencies: channels and dependencies according to the conda environment.yml file. Note that these terms are chosen according to the conda nomenclature.

    """

    channels, dependencies = [], []

    if isinstance(conda, dict):
        channels = conda.get("channels", [])
        dependencies = conda.get("dependencies", [])

    elif isinstance(conda, str):
        if conda.endswith(".yml"):
            with open(conda, "r") as f:
                parsed_conda_env_yaml = yaml.safe_load(f)

            channels = parsed_conda_env_yaml.get("channels", [])
            dependencies = parsed_conda_env_yaml.get("dependencies", [])

    elif isinstance(conda, list):
        dependencies = conda

    return channels, dependencies


def dependency_is_missing(dependency: str, dependencies: List[str], exact: bool = False) -> bool:
    """
    Checks if the dependencies list contains anything starting with the string.

    Args:
        dependency: String to check if it's in the dependencies list.
        dependencies: List of dependencies to be installed in the environment.
        exact: If True, checks if the dependency is exactly the same as the one in the dependencies list.

    Returns:
        True if string is not in the dependencies list, False otherwise.

    """

    for dep in dependencies:
        # check if any dependency starts with the string
        if (not exact and str(dep).startswith(dependency)) or (exact and str(dep).strip() == dependency.strip()):
            print(f"Dependency {dependency} is already in the dependencies list {dep}.")
            return False

    return True


def encode_secrets(variables: List) -> List:
    encoded = []
    for variable in variables:
        encoded_variable = {
            "name": variable["name"],
            "value": base64.b64encode(variable["value"].encode("utf-8")).decode("utf-8") if variable["sensitive"] else variable["value"],
            "sensitive": variable["sensitive"]
        }
        encoded.append(encoded_variable)

    return encoded


def create_env(
    name: str,
    pip: Optional[Union[str, List[str]]] = [],
    conda: Optional[Union[str, List[str], Dict[str, List[str]]]] = [],
    variables: Optional[List] = None,
    settings: Optional[Settings] = settings,
    wait: Optional[bool] = False,
    timeout: Optional[int] = 1800,
    base_image: Optional[str] = None,
) -> None:
    """
    Sends the create request to the Covalent Cloud server with the environment dependency list.

    Args:
        name: Identifier/name for the software environment.

        pip: Python packages to be installed in the environment using pip. This value can be a string `requirements.txt` and/or a list of packages. Note, that if it's a list, it's possible that one of the values is the string `requirements.txt`. In case a `requirements.txt` is passed, it will be parsed into a list of packages and combined with the list of packages passed.`

        conda: List of packages to be installed in the environment using conda. This value can either be a list of packages, a filepath to `environment.yml`. It could also be a dictionary with channels, dependencies, and (optionally) variables as keys, and a list of strings as their values. For example:

            conda={
                        "channels": ["conda-forge", "defaults"],
                        "dependencies": ["numpy=1.21.*", "xarray=0.15.1"],
                        "variables": [{'name': 'mock-variable-1', 'value': '1', 'sensitive': True}]
            }

        Whatever is passed, it will be parsed into a dictionary as shown above and sent as JSON to the Covalent Cloud server. If a list of packages is provided, they will be installed using the default conda channel.

        variables: Environment variables to be set during custom or Covalent build phase.

        settings: Settings object with the dispatcher URI.

        wait: If True, waits until the environment is ready before returning.

        timeout: Timeout in seconds for the environment to be ready.

        base_image: Base image of the runtime environment. If base_image is provided, it should be of the form <url>/<image>:<tag> (e.g. docker.io/python:3.9.6), where the
        :tag is optional and will default to latest if not specified. Only publicly accesible images are supported for now.

    Returns:
        None

    Examples:
        Create an environment with a list of packages:
            >>> create_env("test-env", ["typing"], ["numpy=1.21.*", "xarray=0.15.1"])

        Create an environment with a filepath to `environment.yml`:
            >>> create_env("test-env", "requirements.txt", "environment.yml")

        Create an environment with a dictionary of channels, dependencies, and variables:
            >>> create_env("test-env", "requirements.txt", {"channels": ["conda-forge", "defaults"], "dependencies": ["numpy=1.21.*", "xarray=0.15.1"], "variables": [{'name': 'mock-variable-1', 'value': '1', 'sensitive': True}]})

      Create an environment with a different base image:
            >>> create_env("test-env", ["typing"], ["numpy=1.21.*", "xarray=0.15.1"], base_image="docker.io/python:slim")

    Note:
        In case of a conflict of package between pip and conda, pip will take precedence and the conda one will be ignored.

    """
    pip = pip or []
    conda = conda or {}
    variables = variables or []

    notes = []
    pip_pkgs = get_pip_pkgs(pip)
    channels, dependencies = unpack_conda_pkgs(conda)

    # check dependencies contains pip and if not add pip
    if dependency_is_missing("pip", dependencies, exact=True):
        dependencies = ["pip"] + dependencies
        notes.append("pip was added to the dependencies.")

    # add pip packages to dependencies after checking if pip is explicitly in the dependencies
    dependencies.append({"pip": pip_pkgs})

    # check dependencies contains python and if not set to current python version
    if dependency_is_missing("python=", dependencies):
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        dependencies = [f"python={python_version}"] + dependencies
        notes.append(f"Python version {python_version} was added to the dependencies.")

    yaml_template = {
        "name": name,
        "channels": channels,
        "dependencies": dependencies,
    }

    response_body = None
    start_time = time.time()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as definition_file:

        yaml.dump(yaml_template, definition_file, default_flow_style=False)

        client = get_client(settings)

        # Open a separate reader in binary mode per Requests doc
        try:
            with open(definition_file.name, "rb") as def_file_reader:
                data = {
                    "name": name,
                    "variables": json.dumps(encode_secrets(variables)),
                }
                # add the runtime_config only if base_image is provided
                if base_image:
                    image_config = EnvironmentRuntimeConfig(
                        image=BaseImageConfig(base_image=base_image) if base_image else None)
                    data["runtime_config"] = image_config.model_dump_json(exclude_none=True)
                response = client.post(
                    "/api/v2/envs",
                    {
                        "files": {"definition": def_file_reader},
                        "data": data,
                    },
                )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print("Environment Already Exists.")
                return
            elif (
                e.response.status_code == 401 and e.response.json()["code"] == "auth/unauthorized"
            ):
                CovalentAPIKeyError(
                    message="A valid API key is required to create an environment.",
                    code=e.response.json()["code"],
                ).rich_print(level="error")
                return
            else:
                raise CovalentGenericAPIError(error=e) from e

        response_body = response.json()

    env_is_ready = False
    if wait:
        env_is_ready, env_response = check_env_is_ready(name, settings, wait=True, timeout=timeout)

    if env_is_ready:
        env_name = env_response["records"][0]["name"]
        env_status = env_response["records"][0]["status"]
        env_build_estimate = int(time.time() - start_time)
    else:
        env_name = response_body["name"]
        env_status = response_body["status"]
        env_build_estimate = response_body["estimated_time"]

    print(f"Name: {env_name}")
    print(f"Status: {env_status}")
    print(f"Estimated Time: {env_build_estimate} seconds")
    if notes:
        print("Notes:")
        for note in notes:
            print(f"\t{note}")

    print("Environment file contains:")
    print("==========================")
    print(yaml.dump(yaml_template, default_flow_style=False))


def _get_envs_filtered(**filters) -> Dict[str, Environment]:
    """
    Retrieves the envs from the Covalent Cloud server which match the filters.
    """

    client = get_client()

    try:

        response = client.get(
            "/api/v2/envs",
            request_options={
                "params": filters,
            }
        )

        response.raise_for_status()

        response_dict = response.json()

        envs = {}
        for env in response_dict["records"]:
            readable_env = {
                "id": env["id"],
                "name": env["name"],
                "created_at": env["created_at"],
                "status": env["status"],
                "definition_url": env["definition"],
            }
            envs[env["name"]] = Environment(**readable_env)

    except requests.exceptions.HTTPError:
        print("Error response: ", response.text)
        raise

    return envs


def get_envs(count: int = 10) -> Dict[str, Environment]:
    """
    Retrieves the last `count` created environments from the Covalent Cloud server which are ready.

    Returns:
        Dictionary of environments with their names as keys and their details as values.

    """

    envs = _get_envs_filtered(count=count, status="READY")
    return envs


def delete_env(env_name: str) -> None:
    """
    Deletes the environment with the given name from the Covalent Cloud server.

    Args:
        env_name: Name of the environment to be deleted.

    Returns:
        None

    """

    client = get_client()

    try:
        env = _get_envs_filtered(name=env_name)
        env_id = env[env_name].id

        response = client.delete(f"/api/v2/envs/{env_id}")
        response.raise_for_status()
        print(f"Environment {env_name} deleted successfully.")
    except requests.exceptions.HTTPError:
        print("Error response: ", response.text)
        raise
