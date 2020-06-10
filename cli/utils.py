import os
import ctypes
import sys
from termcolor import colored
from cli.constants import CONFIGURATION_FILE
from pathlib import Path
import json


def _configuration_file_exists():
    try:
        open(CONFIGURATION_FILE, "r")
        return True
    except FileNotFoundError:
        return False


def _create_configuration_file(configuration, downloads_directory):
    config_path = Path(CONFIGURATION_FILE)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIGURATION_FILE, "w+") as config:
        config_data = {
            "client_id": configuration["client_id"],
            "client_secret": configuration["client_secret"],
            "username": configuration["username"],
            "downloads_directory": downloads_directory,
        }
        config.write(json.dumps(config_data))
        return True
