import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict

import requests
from metaflow.exception import MetaflowException
from requests.models import HTTPError
from metaflow_extensions.outerbounds.plugins.perimeters import (
    get_perimeter_config_url_if_set_in_ob_config,
)

OBP_REMOTE_CONFIG_KEY = "OBP_METAFLOW_CONFIG_URL"
HOSTNAME_KEY = "OBP_API_SERVER"
AUTH_KEY = "METAFLOW_SERVICE_AUTH_KEY"
PERIMETER_KEY = "OBP_PERIMETER"
CONFIG_READ_ONCE_KEY = "__REMOTE_CONFIG_HAS_BEEN_RESOLVED__"


def read_config_from_local() -> Optional[Path]:
    default_path = Path.home() / ".metaflowconfig"
    home = Path(os.environ.get("METAFLOW_HOME", default_path))

    profile = os.environ.get("METAFLOW_PROFILE")
    config_path = home / f"config_{profile}.json" if profile else home / "config.json"

    if config_path.exists() and config_path.is_file():
        _init_debug(f"using config from {config_path}")
        return config_path

    # we should error because the user wants a specific config
    if profile:
        raise MetaflowException(
            f"Unable to locate METAFLOW_PROFILE {profile} in {config_path}"
        )

    # there's no config and that's ok. Metaflow uses environment variables as its primary way to set values
    # and will fallback to local settings if no config is present
    _init_debug(f"no config present at path {config_path}")
    return None


def resolve_config_from_remote(remote_url: str, auth_token: str) -> Dict[str, str]:
    _init_debug(f"retrieving config from {remote_url}")

    headers = {"x-api-key": auth_token}
    try:
        response = requests.get(remote_url, headers=headers)
        _init_debug(
            f"response\nstatus code: {response.status_code}\nbody: {response.text}"
        )

        response.raise_for_status()
        data = response.json()
        return data["config"]
    except HTTPError:
        raise MetaflowException(
            "Error fetching resolving configuration. Make sure you have run \
                                `outerbounds configure` with the correct value"
        )


def init_config() -> Dict[str, str]:
    """
    OSS Metaflow reads the config file on every step initialization. This is because OSS assumes config files change
    relatively infrequently. We want to avoid config values changing between flow steps. Our solution to prevent this
    is to read a config once and cache it on an environment variable. Environment variables carry over between steps
    because steps are executed in subprocesses (local) or environments which expect environment variables to be set.
    """
    _init_debug("starting initialization")
    config_json = os.environ.get(CONFIG_READ_ONCE_KEY)
    if config_json:
        _init_debug("reading config from environment")
        return json.loads(config_json)

    config_path = read_config_from_local()
    if not config_path:
        return {}

    try:
        remote_config = json.loads(config_path.read_text())
    except ValueError:
        raise MetaflowException(
            "Error decoding your metaflow config. Please run the `outerbounds configure` \
                                 command with the string provided in the Outerbounds dashboard"
        )

    perimeter_config_url = get_perimeter_config_url_if_set_in_ob_config()
    if perimeter_config_url:
        remote_config[OBP_REMOTE_CONFIG_KEY] = perimeter_config_url

    # users still have a legacy format and that's ok.
    if OBP_REMOTE_CONFIG_KEY not in remote_config:
        return remote_config

    metaflow_config = resolve_config_from_remote(
        remote_url=remote_config[OBP_REMOTE_CONFIG_KEY],
        auth_token=remote_config[AUTH_KEY],
    )

    # set cache
    os.environ[CONFIG_READ_ONCE_KEY] = json.dumps(metaflow_config)
    return metaflow_config


DEBUG_CONFIG = os.environ.get("METAFLOW_DEBUG_CONFIG")


def _init_debug(*args, **kwargs):
    if DEBUG_CONFIG:
        init_str = "ob_extension_init:"
        kwargs["file"] = sys.stderr
        print(init_str, *args, **kwargs)
