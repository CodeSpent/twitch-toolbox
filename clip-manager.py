import os
import sys
import fire
import json
import time
import requests
from pathlib import Path
from termcolor import colored
from selenium import webdriver
from resources.twitch import TwitchHelix
from selenium.webdriver.firefox.options import Options


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class Manager(object):
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.username = None
        self.config = os.path.join(Path.home(), "twitch-clip-manage.json")
        self.download_dir = os.path.join(os.getcwd(), "downloads")

    def _read_config(self):
        try:
            config_file = open(self.config, "r")
            config_data = json.load(config_file)

            self.client_id = config_data["client_id"]
            self.client_secret = config_data["client_secret"]
            self.username = config_data["username"]
            self.download_dir = config_data["download_dir"]
            return config_data

        except FileNotFoundError:
            with open(self.config, "w") as config_file:
                base_config = {
                    "client_id": None,
                    "client_secret": None,
                    "username": None,
                    "download_dir": str(self.download_dir)
                }
                json.dump(base_config, config_file)
            return json.load(config_file)

    def _get_clip_source(self, url):
        options = Options()
        options.headless = True

        if sys.platform == "linux":
            driver = resource_path("drivers/geckodriver")
        elif sys.platform == "darwin":
            print(colored("Mac not yet supported.", "red"))
            sys.exit()
        elif sys.platform == "win32":
            driver = resource_path("drivers/geckodriver.exe")

        browser = webdriver.Firefox(executable_path=driver, options=options)
        browser.get(url)
        time.sleep(2)
        video_element = browser.find_element_by_css_selector("video")
        source = video_element.get_attribute("src")
        browser.quit()
        return source

    def _download_clip(self, source, filename):
        if " " in filename:
            filename = filename.replace(" ", "-")
        downloaded_video = requests.get(source, stream=True)
        with open(self.download_dir + "/" + filename + ".mp4", "wb") as f:
            f.write(downloaded_video.content)
        return True

    def setup(self, client_id=None, client_secret=None, username=None):
        if client_id is None or client_secret is None:
            print(
                "Please create an application at https://dev.twitch.tv/console/apps/create and provide your Client ID & Client Secret."
            )

            config = self._read_config()

            while True:
                if config["client_id"]:
                    overwrite = input("Overwrite existing Client ID? (y/N): ")
                    if overwrite.lower() == "n":
                        break
                client_id = input("Client ID: ")
                if client_id is not None and client_id is not "":
                    break
                print(colored("You must provide a Client ID.", "red"))
            self.client_id = client_id

            while True:
                if config["client_secret"]:
                    overwrite = input("Overwrite existing Client Secret? (y/N): ")
                    if overwrite.lower() == "n":
                        break
                client_secret = input("Client Secret: ")
                if client_secret is not None and client_secret is not "":
                    break
                print(colored("You must provide a Client Secret.", "red"))
            self.client_secret = client_secret

            while True:
                if config["download_dir"]:
                    overwrite = input("Overwrite existing Downloads directory? (y/N): ")
                    if overwrite.lower() == "n":
                        break
                download_dir = input(f"Downloads directory (default: {str(os.path.join(os.getcwd(), 'downloads'))}): ")
                if download_dir is "" or download_dir is None:
                    break
                else:
                    self.download_dir = download_dir

        if username is None:
            while True:
                if config["username"]:
                    overwrite = input("Overwrite existing Twitch username? (y/N): ")
                    if overwrite.lower() == "n":
                        break
                username = input("Twitch username: ")
                if username is not None and username is not "":
                    break
                print(colored("You must specifiy a Twitch username.", "red"))
            self.username = username

        with open(self.config, "w") as config_file:
            config_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "download_dir": self.download_dir
            }
            json.dump(config_data, config_file)

        print(
            colored(
                "You're all set! You can now run 'download' to download your clips.",
                "green",
            )
        )

    def download(self):
        self._read_config()
        if self.client_id is None or self.client_secret is None or self.username is None:
            print(colored("Something went wrong during configuration."), "red")
            self.setup()

        print(f"Looking for all clips for {self.username}.")

        api = TwitchHelix(client_id=self.client_id, client_secret=self.client_secret)
        clips = api.get_clips_by_user_login(self.username)

        print(colored(f"Collected {len(clips)} clips for {self.username}.", "green",))

        for clip in clips:
            print(f"Downloading {colored(clip['title'], 'blue')}")
            clip_url = clip["url"]
            clip_source = self._get_clip_source(clip_url)

            video = self._download_clip(clip_source, clip["title"])
            if video:
                print(colored("Clip downloaded successfully!", "green"))
        print(colored(f"Downloaded {len(clips)} successfully! Files in {self.download_dir}."))

if __name__ == "__main__":
    fire.Fire(Manager)
