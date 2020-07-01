import os
import sys
import json
import time
import requests
from termcolor import colored
from resources.twitch import TwitchHelix
from cli.constants import CONFIGURATION_FILE
from tqdm import tqdm
from werkzeug.utils import secure_filename


class Downloader(object):
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.username = None
        self.downloads_directory = None
        self.base_clip_url = "https://clips-media-assets2.twitch.tv/"

        self._configure()

    def _configure(self):
        config_file = open(CONFIGURATION_FILE, "r")
        config = json.load(config_file)

        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.username = config["username"]
        self.downloads_directory = config["downloads_directory"]

    def _download_clip(self, source, filename):
        if " " in filename:
            filename = filename.replace(" ", "-")
        filename = secure_filename(filename)

        downloaded_video = requests.get(source, stream=True)
        total_size = int(downloaded_video.headers.get("content-length", 0))
        block_size = 1024
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

            # Extract the source url from thumbnail url
            # by removing the -preview- from the asset
            # and changing the extension from .jpg to .mp4
            thumbnail_url = clip["thumbnail_url"]
            slice_index = thumbnail_url.index("-preview-")
            source = thumbnail_url[:slice_index] + ".mp4"

            video = self._download_clip(source, clip["title"])
        return {
            "count": len(clips),
            "success": True,
            "directory": self.downloads_directory,
        }
