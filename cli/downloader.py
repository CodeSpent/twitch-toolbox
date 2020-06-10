import os
import sys
import json
import time
import requests
from termcolor import colored
from resources.twitch import TwitchHelix
from cli.constants import CONFIGURATION_FILE, ALLOWED_CHARACTERS
from tqdm import tqdm
import datetime
from dateutil import parser
import pytz
from pathlib import Path


class Downloader(object):
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.username = None
        self.downloads_directory = None
        self.base_clip_url = "https://clips-media-assets2.twitch.tv/"

        self._configure()

    def _configure(self, username=None):
        config_file = open(CONFIGURATION_FILE, "r")
        config = json.load(config_file)

        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.downloads_directory = config["downloads_directory"]

        if username is None:
            self.username = config["username"]
        else:
            self.username = username

    def _download_clip(self, source, filename):
        if " " in filename:
            filename = filename.replace(" ", "-")
        downloaded_video = requests.get(source, stream=True)
        total_size = int(downloaded_video.headers.get("content-length", 0))
        block_size = 1024
        t = tqdm(total=total_size, unit="iB", unit_scale=True)

        # Place all files in a nested clips directory within
        # configured downloads directory to prevent flooding
        # when choosing a directory like "Desktop" or /home/.
        download_to = os.path.join(self.downloads_directory, f"{self.username}-clips")
        Path(download_to).mkdir(exist_ok=True)

        with open(download_to + "/" + filename + ".mp4", "wb") as f:
            for data in downloaded_video.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        return True

    def download_all_clips(self, username=None):
        downloaded_clips = []

        # Override username if a target user
        # is provided.
        if username is not None:
            self._configure(username=username)

        print(f"Getting clips for {self.username}.")
        print(
            "Starting date is May 1st 2016. This can take a while if you're a new streamer."
        )

        started_at = datetime.datetime(2016, 5, 1, 00, 00, tzinfo=pytz.UTC).isoformat()

        # Give check_stop a future date to start. This is hacky, but it works.
        stop_date = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        check_stop = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).replace(
            tzinfo=pytz.UTC
        )
        week_delta = datetime.timedelta(days=7)
        api = TwitchHelix(client_id=self.client_id, client_secret=self.client_secret)

        while True:
            print(started_at, check_stop, stop_date)
            clips = api.get_clips_by_user_login(self.username, started_at=started_at)
            if clips is None:
                started_at = (parser.parse(started_at) + week_delta).isoformat()
                continue

            for clip in clips:
                print(f"Downloading {colored(clip['title'], 'blue')}.")

                # Extract the source url from thumbnail url
                # by removing the -preview- from the asset
                # and changing the extension from .jpg to .mp4
                thumbnail_url = clip["thumbnail_url"]
                slice_index = thumbnail_url.index("-preview-")
                source = thumbnail_url[:slice_index] + ".mp4"

                sanitized_title = "".join(
                    c for c in clip["title"] if c.lower() in ALLOWED_CHARACTERS.lower()
                )

                created_at = parser.parse(clip["created_at"])
                readable_date = datetime.datetime.strftime(
                    created_at, "%Y-%m-%d-%H:%M:%s"
                )
                filename = "-".join([sanitized_title, readable_date])
                video = self._download_clip(source, filename)
                next_week = parser.parse(clips[-1]["created_at"]) + week_delta
                started_at = next_week.isoformat()
                check_stop = parser.parse(started_at).replace(tzinfo=pytz.UTC)
                downloaded_clips.append(clip)

            print(check_stop, stop_date)
            if check_stop > stop_date:
                print(check_stop, stop_date)
                break
            continue
        return {
            "count": len(downloaded_clips),
            "success": True,
        }
