import os
import ctypes
import sys
from termcolor import colored
from cli.constants import CONFIGURATION_FILE


def _is_admin():
    if sys.platform == "win32":
        try:
            return ctypes.windll.shell32.IsUserAdmin()
        except:
            return False
    elif sys.platform == "linux":
        return os.geteuid() == 0
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")


def _configuration_file_exists():
    try:
        open(CONFIGURATION_FILE, "r")
        return True
    except FileNotFoundError:
        return False


def _create_configuration_file(configuration, downloads_directory):
    if _is_admin():
        with open(CONFIGURATION_FILE, "w") as config:
            config_data = {
                "client_id": configuration["client_id"],
                "client_secret": configuration["client_secret"],
                "username": configuration["username"],
                "downloads_directory": downloads_directory,
            }
            config.write(config_data)
            return True
    else:
        print(colored("Please launch this application as admin to configure.", "red"))
        return False
