import json
import time
from pprint import pprint

import attr
import requests

from src.general_utils.file_utils import convert_to_base64


@attr.s(auto_attribs=True)
class SpotifyAuthorization:
    _access_token: str
    _expire_time: int
    _client_base64: str
    _refresh_token: str
    _token_type: str
    _scope: str
    _refresh_buffer: int = 60 * 1e9

    @classmethod
    def from_alex_json(
            cls,
            auth_json_path: str
    ):
        with open(auth_json_path, 'r') as auth_json_file:
            auth_json_data = json.load(auth_json_file)
        client_id: str = auth_json_data['client_id']
        client_secret: str = auth_json_data['client_secret']
        access_token: str = auth_json_data['access_token']
        refresh_token: str = auth_json_data['refresh_token']
        token_type: str = auth_json_data['token_type']
        expires_in: int = auth_json_data['expires_in']
        scope: str = auth_json_data['scope']
        authorized_time: int = auth_json_data['authorized_time']

        client_base64 = convert_to_base64(client_id + ':' + client_secret)
        expire_time = authorized_time + expires_in

        return cls(
            client_base64=client_base64,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expire_time=expire_time,
            scope=scope
        )

    def get_token(self):
        if time.time_ns() > self._expire_time - self._refresh_buffer:
            self._refresh()
        return self._access_token

    def _refresh(self):
        token_response = requests.post(
            url="https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token
            },
            headers={
                "Authorization": "Basic " + self._client_base64
            }
        )
        token_json = token_response.json()
        self._access_token = token_json["access_token"]
        self._expire_time = time.time_ns() + (token_json["expires_in"] * 1e9)
