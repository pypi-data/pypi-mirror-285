import os
from typing import Any
import warnings
import pydantic
import yaml
import idac_sdk
from idac_sdk.errors import OldConfigFoundException, OldConfigFoundWarning
from idac_sdk.models.config import iDACConfig


DIR_PATH = os.path.dirname(idac_sdk.__file__)
IDAC_CONFIG_FOLDER = os.path.join(DIR_PATH, ".idac")
IDAC_CONFIG_FILE = os.path.join(IDAC_CONFIG_FOLDER, "config")
IDAC_CONFIG_VERSION = "1.0"
EMPTY_CONFIG: Any = {
    "version": IDAC_CONFIG_VERSION,
    "defaults": {
        "idac_fqdn": "",
        "idac_proto": "https",
        "auth": {"type": idac_sdk.IDACAuthType.DCLOUD_SESSION.name, "params": {}},
        "api_version": "2.0",
    },
}


def have_config() -> bool:
    """Checks if config file exists

    Returns:
        bool: True if exists
    """
    return os.path.exists(IDAC_CONFIG_FILE)


def load_config(raise_error: bool = True) -> iDACConfig:
    """Loads either existing or empty iDAC config

    Returns:
        iDACConfig: loaded config
    """
    if not os.path.exists(IDAC_CONFIG_FOLDER):
        os.mkdir(IDAC_CONFIG_FOLDER)

    if os.path.exists(IDAC_CONFIG_FILE):
        with open(IDAC_CONFIG_FILE, "r") as file:
            current_config = yaml.safe_load(file)
            if not "version" in current_config or current_config["version"] != IDAC_CONFIG_VERSION:
                if raise_error:
                    raise OldConfigFoundException(
                        "Found an old version of the config file, please run 'idac config' again."
                    )
                warnings.warn("Old iDAC config found, ignoring current file", OldConfigFoundWarning)
                return iDACConfig(**EMPTY_CONFIG)
        try:
            result = iDACConfig(**current_config)
            return result
        except pydantic.error_wrappers.ValidationError:
            if raise_error:
                raise OldConfigFoundException(
                    "Found an invalid config file, please run 'idac config' again."
                )
            warnings.warn(
                "Found an invalid config file, ignoring current file", OldConfigFoundWarning
            )
            return iDACConfig(**EMPTY_CONFIG)
    else:
        return iDACConfig(**EMPTY_CONFIG)
