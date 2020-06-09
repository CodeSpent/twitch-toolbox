import os
import sys
import json
import time
import requests
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from resources.twitch import TwitchHelix
from cli.constants import CONFIGURATION_FILE
from tqdm import tqdm


class Downloader(object):
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.username = None
        self.downloads_directory = None

        self._configure()

    def _configure(self):
        config_file = open(CONFIGURATION_FILE, "r")
        config = json.load(config_file)

        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.username = config["username"]
        self.downloads_directory = config["downloads_directory"]

    def _get_clip_source(self, url):
        options = Options()
        options.headless = True

        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)

        if sys.platform == "linux":
            driver = os.path.join(base_path, "../drivers/geckodriver")
        elif sys.platform == "darwin":
            print(colored("Mac not yet supported.", "red"))
            sys.exit()
        elif sys.platform == "win32":
            driver = os.path.join(base_path, "../drivers/geckodriver")

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
        total_size = int(downloaded_video.headers.get("content-length", 0))
        block_size = 1024  # 1 Kibibyte
        t = tqdm(total=total_size, unit="iB", unit_scale=True)

        with open(self.downloads_directory + "/" + filename + ".mp4", "wb") as f:
            for data in downloaded_video.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        return True

    def download_all_clips(self):
        print(f"Getting all clips for {self.username}.")

        api = TwitchHelix(client_id=self.client_id, client_secret=self.client_secret)
        clips = api.get_clips_by_user_login(self.username)

        print(colored(f"Got {len(clips)} clips for {self.username}.", "green"))

        for clip in clips:
            print(f"Downloading {colored(clip['title'], 'blue')}.")
            source = self._get_clip_source(clip["url"])
            video = self._download_clip(source, clip["title"])
        return {
            "count": len(clips),
            "success": True,
            "directory": self.downloads_directory,
        }
