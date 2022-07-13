"""
tools generally related to pushing/pulling spotify data
"""
import os.path
import sqlite3

import attr
import requests
import json
from attrs import define


@attr.s(auto_attribs=True)
class ListeningLogTalker:
    log_conn: sqlite3.Connection

    @classmethod
    def from_filepath(cls,
                      filepath: str):
        assert filepath[-2:] == 'db', f'{filepath} does not have .db extension'
        assert os.path.isfile(filepath), f'{filepath} does not exist'
        conn = sqlite3.connect(filepath)
        return cls(log_conn=conn)

    def add_tracks_to_timeline(self,
                               track_list: list[str]):
        ...



@attr.s(auto_attribs=True)
class SpotifyToken:
    token: str

    @classmethod
    def from_user_input(cls,
                        token: str):
        return cls(token=token)

    def provide_token(self):
        return self.token

    def refresh_token(self):
        ...


@attr.s(auto_attribs=True)
class SpotifyTalker:
    token: SpotifyToken

    @classmethod
    def from_client_flow(cls,
                         client_id: str,
                         client_secret: str):
        token_string = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }).json()['access_token']

        token = SpotifyToken.from_user_input(token=token_string)
        return cls(token=token)

    @classmethod
    def from_token(cls,
                   token_string: str):
        token = SpotifyToken.from_user_input(token=token_string)
        return cls(token=token)

    def _refresh_token(self):
        ...

    def get_current_track(self):
        token_string = self.token.provide_token()

        headers = {'Authorization': f'Bearer {token_string}'}
        response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
        assert response.status_code in [200,204], f'Invalid Response: code {response.status_code}'
        if response.status_code == 204: return None
        curr_track_json = response.json()
        curr_track_info = {'track_name': curr_track_json['item']['name']}  # TODO expand to include more track data
        return curr_track_info

    def get_playlist_tracks(self,
                            playlist_name: str):
        ...

    def remove_tracks_from_playlist(self,
                                    playlist_name: str,
                                    track_list: list[str]):
        ...

    def add_tracks_to_playlist(self,
                               playlist_name: str,
                               track_list: list[str]):
        ...

    def get_liked_tracks(self):
        ...

    def like_tracks(self,
                    track_list: list[str]):
        ...

    def unlike_tracks(self,
                      track_list: list[str]):
        ...

    def dislike_tracks(self,
                       track_list: list[str]):
        ...

    def like_albums(self,
                    album_list: list[str]):
        ...

    def unlike_albums(self,
                      album_list: list[str]):
        ...

    def dislike_albums(self,
                       album_list: list[str]):
        ...

    def like_artists(self,
                     artist_list: list[str]):
        ...

    def unlike_artists(self,
                       artist_list: list[str]):
        ...

    def dislike_artists(self,
                        artist_list: list[str]):
        ...

def main():
    # client_creds = json.load(open('credentials_spot.json'))
    token_string = 'BQBFenSnCvvXyqoZm3s3rxX5efERAULYhVKoWR9oH54pl7m5jAoHs5zZ1mjKW_Hp34pdC3dH_5gfKnzeooTPo4UdqjitcseRlhVdJLw1mAA2XzVYTUTYkPUjb7ahYuF5om4DpukE1X8uHNeNztwuFtPShRTku3IXRlAzCge_-KCVVg5fYg'
    spotify_conn = SpotifyTalker.from_token(token_string=token_string)
    curr_track = spotify_conn.get_current_track()
    print(curr_track)


if __name__ == '__main__':
    main()
