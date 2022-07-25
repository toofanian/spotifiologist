"""
tools generally related to pushing/pulling spotify data
"""
import time
from pprint import pprint
import attr
import requests
import json


@attr.s(auto_attribs=True)
class SpotifyTalker:
    client_id: str
    client_secret: str
    client_base64: str
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    authorized_time: int
    _buffer_time: int = 60

    @classmethod
    def from_preauthorization(
            cls,
            cred_json_path: str
    ):
        with open(cred_json_path, 'r') as creds_file:
            creds_json = json.load(creds_file)
            client_id = creds_json['client_id']
            client_secret = creds_json['client_secret']
            client_base64 = creds_json['client_base64']
            access_token = creds_json['access_token']
            token_type = creds_json['token_type']
            expires_in = creds_json['expires_in']
            refresh_token = creds_json['refresh_token']
            scope = creds_json['scope']
            authorized_time = creds_json['authorized_time']
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            client_base64=client_base64,
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            refresh_token=refresh_token,
            scope=scope,
            authorized_time=authorized_time
        )

    def _refresh_token_if_expired(self):
        if time.time_ns() - self.authorized_time > self.expires_in - self._buffer_time:
            refresh_token = self.refresh_token
            client_base64 = self.client_base64
            query = "https://accounts.spotify.com/api/token"
            response = requests.post(query,
                                     data={"grant_type": "refresh_token",
                                           "refresh_token": refresh_token},
                                     headers={"Authorization": "Basic " + client_base64})
            response_json = response.json()
            self.access_token = response_json["access_token"]
            self.authorized_time = time.time_ns()

    def get_current_track(self):
        self._refresh_token_if_expired()
        access_token = self.access_token

        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
        assert response.status_code in [200, 204], f'Invalid Response: code {response.status_code}'
        if response.status_code == 204: return None
        curr_track_json = response.json()
        curr_track_info = {'track_name': curr_track_json['item']['name']}  # TODO expand to include more track data
        return curr_track_info

    def get_recent_tracks(self):
        self._refresh_token_if_expired()
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get('https://api.spotify.com/v1/me/player/recently-played', headers=headers)
        response_json = response.json()
        pprint(response_json)

    def get_playlist_tracks(self,
                            playlist_name: str):
        self._refresh_token_if_expired()
        ...

    def remove_tracks_from_playlist(self,
                                    playlist_name: str,
                                    track_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def add_tracks_to_playlist(self,
                               playlist_name: str,
                               track_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def get_liked_tracks(self):
        self._refresh_token_if_expired()
        ...

    def like_tracks(self,
                    track_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def unlike_tracks(self,
                      track_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def dislike_tracks(self,
                       track_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def like_albums(self,
                    album_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def unlike_albums(self,
                      album_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def dislike_albums(self,
                       album_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def like_artists(self,
                     artist_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def unlike_artists(self,
                       artist_list: list[str]):
        self._refresh_token_if_expired()
        ...

    def dislike_artists(self,
                        artist_list: list[str]):
        self._refresh_token_if_expired()
        ...


def main():
    cred_json_path = '/Volumes/GoogleDrive/My Drive/code/spotify_tools/.creds/credentials_spot.json'
    spotify_conn = SpotifyTalker.from_preauthorization(cred_json_path=cred_json_path)
    curr_track = spotify_conn.get_current_track()
    print(curr_track)


if __name__ == '__main__':
    main()
