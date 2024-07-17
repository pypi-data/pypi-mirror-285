from outerbounds._vendor import click
import json
import os
import requests
from os import path
from typing import Dict
import sys


def init_config(config_dir, profile) -> Dict[str, str]:
    config = read_metaflow_config_from_filesystem(config_dir, profile)

    # This is new remote-metaflow config; fetch it from the URL
    if "OBP_METAFLOW_CONFIG_URL" in config:
        remote_config = init_config_from_url(
            config_dir, profile, config["OBP_METAFLOW_CONFIG_URL"]
        )
        remote_config["OBP_METAFLOW_CONFIG_URL"] = config["OBP_METAFLOW_CONFIG_URL"]
        return remote_config
    # Legacy config, use from filesystem
    return config


def init_config_from_url(config_dir, profile, url) -> Dict[str, str]:
    config = read_metaflow_config_from_filesystem(config_dir, profile)

    if config is None or "METAFLOW_SERVICE_AUTH_KEY" not in config:
        raise Exception("METAFLOW_SERVICE_AUTH_KEY not found in config file")

    config_response = requests.get(
        url,
        headers={"x-api-key": f'{config["METAFLOW_SERVICE_AUTH_KEY"]}'},
    )
    config_response.raise_for_status()
    remote_config = config_response.json()["config"]
    return remote_config


def read_metaflow_config_from_filesystem(config_dir, profile) -> Dict[str, str]:
    config_filename = f"config_{profile}.json" if profile else "config.json"

    path_to_config = os.path.join(config_dir, config_filename)

    if os.path.exists(path_to_config):
        with open(path_to_config, encoding="utf-8") as json_file:
            config = json.load(json_file)
    else:
        raise Exception("Unable to locate metaflow config at '%s')" % (path_to_config))
    return config


def get_metaflow_token_from_config(config_dir: str, profile: str) -> str:
    """
    Return the Metaflow service auth key from the config file.

    Args:
        config_dir (str): Path to the config directory
        profile (str): The named metaflow profile
    """
    config = init_config(config_dir, profile)
    if config is None or "METAFLOW_SERVICE_AUTH_KEY" not in config:
        raise Exception("METAFLOW_SERVICE_AUTH_KEY not found in config file")
    return config["METAFLOW_SERVICE_AUTH_KEY"]


def get_sanitized_url_from_config(config_dir: str, profile: str, key: str) -> str:
    """
    Given a key, return the value from the config file, with https:// prepended if not already present.

    Args:
        config_dir (str): Path to the config directory
        profile (str): The named metaflow profile
        key (str): The key to look up in the config file
    """
    config = init_config(config_dir, profile)
    if key not in config:
        raise Exception(f"Key {key} not found in config")
    url_in_config = config[key]
    if not url_in_config.startswith("https://"):
        url_in_config = f"https://{url_in_config}"

    url_in_config = url_in_config.rstrip("/")
    return url_in_config


def get_remote_metaflow_config_for_perimeter(
    origin_token: str, perimeter: str, api_server: str
):
    try:
        response = requests.get(
            f"{api_server}/v1/perimeters/{perimeter}/metaflowconfigs/default",
            headers={"x-api-key": origin_token},
        )
        response.raise_for_status()
        config = response.json()["config"]
        config["METAFLOW_SERVICE_AUTH_KEY"] = origin_token
        return config
    except Exception as e:
        click.secho(
            f"Failed to get metaflow config from {api_server}. Error: {str(e)}",
            fg="red",
        )
        sys.exit(1)
