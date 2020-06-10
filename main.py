from __future__ import print_function, unicode_literals
import pkg_resources
import pkg_resources.py2_warn

from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
from cli.styles import twitch_theme
import tkinter as tk
from tkinter import filedialog
from termcolor import colored
from cli.utils import _create_configuration_file, _configuration_file_exists
from cli.downloader import Downloader
import sys
import os
import pyfiglet
import pyfiglet.fonts

os.system("cls" if os.name == "nt" else "clear")


class MyFigletFont(pyfiglet.FigletFont):
    @classmethod
    def preloadFont(cls, font):
        base_path = os.path.dirname(pyfiglet.fonts.__file__)
        for extension in ("tlf", "flf"):
            fn = "%s.%s" % (font, extension)
            if os.path.isfile(os.path.join(base_path, fn)):
                with open(os.path.join(base_path, fn), "rb") as f:
                    return f.read().decode("UTF-8", "replace")
            else:
                for location in ("./", pyfiglet.SHARED_DIRECTORY):
                    full_name = os.path.join(location, fn)
                    if os.path.isfile(full_name):
                        with open(full_name, "rb") as f:
                            return f.read().decode("UTF-8", "replace")
        else:
            raise FontNotFound(font)


pyfiglet.FigletFont = MyFigletFont

print(pyfiglet.figlet_format("Twitch Toolbox"))
print(
    f"******************* Built with {colored('❤️', 'red')} by {colored('@CodeSpent', 'cyan')}. *******************".center(
        10
    )
)


def _ask_for_confirmation(message):
    confirmation_options = [{"type": "confirm", "name": "confirm", "message": message}]
    answer = prompt(confirmation_options, style=twitch_theme)
    return answer["confirm"]


main_menu_options = [
    {
        "type": "list",
        "name": "main",
        "message": "What do you want to do?",
        "choices": [
            "Download VODs",
            "Download Clips",
            Separator(),
            "Configure",
            "Exit",
        ],
    }
]

configure_options = [
    {"type": "input", "name": "client_id", "message": "Twitch Client ID:"},
    {"type": "password", "name": "client_secret", "message": "Twitch Client Secret:"},
    {"type": "input", "name": "username", "message": "Twitch Username:"},
]

main_menu = prompt(main_menu_options, style=twitch_theme)

if main_menu["main"] == "Configure":
    if _configuration_file_exists():
        overwrite = _ask_for_confirmation(
            "Configuration already exists. Overwrite existing?"
        )
        if not overwrite:
            sys.exit()

    print(colored("Create an app at https://dev.twitch.tv/ to get started.", "blue"))
    configuration = prompt(configure_options, style=twitch_theme)

    print("Choose a downloads directory.")
    root = tk.Tk()
    root.withdraw()

    downloads_directory = filedialog.askdirectory()
    _create_configuration_file(configuration, downloads_directory)

    if _configuration_file_exists():
        main_menu = prompt(main_menu_options, style=twitch_theme)

elif main_menu["main"] == "Download Clips":
    if not _configuration_file_exists():
        print(colored("You must configure the CLI first.", "red"))
        sys.exit()
    clips = Downloader().download_all_clips()
    if clips["success"]:
        print(
            colored(
                f"Downloaded {clips['count']} clips to {clips['directory']} successfully!"
            )
        )

elif main_menu["main"] == "Exit":
    sys.exit()

else:
    pass
