import fire
import json
from termcolor import colored
import requests
from resources.twitch import TwitchHelix
import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time


class Downloader(object):
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.username = None

    def _read_config(self):
        try:
            config_file = open("config.json", "r")
        except FileNotFoundError:
            print(
                colored(
                    "Unable to find config.json. Would you like to reconfigure now?",
                    "red",
                )
            )
            while True:
                reconfigure = input("y/n: ")
                if reconfigure.lower() == "y":
                    self.setup()
                    break
                elif reconfigure.lower() == "n":
                    exit
                    break
                else:
                    print(colored("Invalid response.", "red"))

        config_data = json.load(config_file)
        if all(
            key in config_data for key in ("client_id", "client_secret", "username")
        ):
            self.client_id = config_data["client_id"]
            self.client_secret = config_data["client_secret"]
            self.username = config_data["username"]
            return True

    def _get_clip_source(self, url):
        options = Options()
        options.headless = True

        if sys.platform == "linux":
            driver = os.getcwd() + "/drivers/geckodriver"
        elif sys.platform == "darwin":
            print(colored("Mac not yet supported.", "red"))
            sys.exit()
        elif sys.platform == "win32":
            driver = os.getcwd() + "/drivers/geckodriver.exe"
        browser = webdriver.Firefox(executable_path=driver, options=options)
        browser.get(url)
        time.sleep(2)
        video_element = driver.find_element_by_css_selector("video")
        source = video_element.get_attribute("src")
        return source

    def _download_clip(self, source, filename):
        if " " in filename:
            filename = filename.replace(" ", "-")
        downloaded_video = requests.get(source, stream=True)
        with open("clips/" + filename + ".mp4", "wb") as f:
            f.write(downloaded_video.content)
        return True

    def setup(self, client_id=None, client_secret=None, username=None):
        if client_id is None or client_secret is None:
            print(
                "Please create an application at https://dev.twitch.tv/console/apps/create and provide your Client ID & Client Secret."
            )

            while True:
                client_id = input("Client ID: ")
                if client_id is not None and client_id is not "":
                    break
                print(colored("You must provide a Client ID.", "red"))

            while True:
                client_secret = input("Client Secret: ")
                if client_secret is not None and client_secret is not "":
                    break
                print(colored("You must provide a Client Secret.", "red"))

        if username is None:
            while True:
                username = input("Twitch username: ")
                if username is not None and username is not "":
                    break
                print(colored("You must specifiy a Twitch username.", "red"))

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username

        with open("config.json", "w") as config_file:
            config_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
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
        if not self.client_id or not self.client_secret or not self.username:
            print(colored("Something went wrong during configuration."), "red")
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


if __name__ == "__main__":
    fire.Fire(Downloader)
