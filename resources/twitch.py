import requests
import json
import datetime
from dateutil import parser
import pytz


class TwitchHelix(object):
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.twitch.tv/helix"
        self.authentication_url = "https://id.twitch.tv/oauth2/token"
        self.token = self._authenticate()
        self.headers = self._set_headers()

    def _set_headers(self):
        """
        Returns headers dict for _request
        """
        headers = {}
        headers["Connection"] = "keep-alive"

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.client_id is not None:
            headers["Client-id"] = self.client_id
        return headers

    def _authenticate(self):
        """
        Returns an access_token from Twitch API
        """
        if self.client_id and self.client_secret:
            params = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = requests.post(self.authentication_url, params)
            if response.status_code != 200:
                return None
            data = response.json()
            if "error" in data:
                raise Exception(f"Error in _authenticate: {data['error']}")
            else:
                return data["access_token"]

    def _request(self, method, endpoint, params={}, data={}):
        """
        Returns JSON for requests made to Twitch API
        """
        if method.lower() == "get":
            request_url = self.base_url + endpoint
            try:
                response = requests.get(
                    request_url, params=params, headers=self.headers
                )
            except ConnectionError as e:
                print(e)
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 500:
                print("Twitch API Error")
            else:
                if "error" in data:
                    print(f"Error in {endpoint} _request: {data['error']}")
                else:
                    return None

        elif method.lower() == "post":
            request_url = self.base_url + endpoint
            data = json.loads(data)
            response = requests.post(
                request_url, params=params, headers=self.headers, json=data
            )
        else:
            raise Exception(f"Unsupported method supplied to _request: {method}")

    def get_user(self, user_login=None, user_id=None):
        """
        Returns a dict of user object.
        """
        params = {}
        if user_id is not None:
            params["id"] = user_id
        if user_login is not None:
            params["login"] = user_login

        response = self._request("get", "/users", params)
        data = response["data"]

        return data

    def get_clips_by_user_login(
        self, user_login, first=100, started_at=None, ended_at=None
    ):
        """
        Returns a list of all clips for requested user.
        """
        user_response = self.get_user(user_login=user_login)
        user_id = user_response[0]["id"]
        cursor = True
        clips = []

        while cursor:
            params = {
                "broadcaster_id": user_id,
                "started_at": started_at,
                "ended_at": ended_at,
                "first": first,
            }

            if type(cursor) is not bool:
                params["after"] = cursor
            response = self._request("get", "/clips", params)

            if response is None or len(response["data"]) is 0:
                return None

            [clips.append(x) for x in response["data"]]

            pagination = response["pagination"]

            if "cursor" in pagination:
                cursor = response["pagination"]["cursor"]
            else:
                break
        return clips
