import logging

import attr
import requests

from src.spotify_utils.spotify_item_info import SavedAlbumInfo, TrackListeningInfo, SavedSongInfo
from src.spotify_utils.spotify_authorization import SpotifyAuthorization


@attr.s(auto_attribs=True)
class ISpotify:
    authorization: SpotifyAuthorization

    @classmethod
    def from_preauthorization(
            cls,
            preauthorization: SpotifyAuthorization
    ):
        return cls(
            authorization=preauthorization
        )

    def get_currently_playing(self):
        response_currently_playing = requests.get(
            url='https://api.spotify.com/v1/me/player/currently-playing',
            headers={
                'Authorization': f'Bearer {self.authorization.get_token()}'
            }
        )
        currently_playing_json = response_currently_playing.json()
        return currently_playing_json

    def get_recently_played(
            self,
            limit: int = 50
    ):
        """
        :return: tuple, (sorted list of TrackListeningInfo w/ most recent first, before_cursor)
        """

        response_recently_played = requests.get(
            url=f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}',
            headers={
                'Authorization': f'Bearer {self.authorization.get_token()}'
            }
        )
        recently_played_json = response_recently_played.json()

        track_listening_info_batch = [
            TrackListeningInfo.from_json_request_item(item) for item in recently_played_json['items']
        ]

        # this sort shouldn't be necessary, but better safe than sorry
        track_listening_info_batch.sort(key=lambda x: x.played_at, reverse=True)

        return track_listening_info_batch

    def get_saved_albums(
            self,
            limit: int = 50,
            offset: int = 50
         ):
        count: int = 0
        saved_albums_info = []
        logging.warning('getting saved albums, this may take a while...')
        for _ in range(1000):
            response_saved_albums = requests.get(
                url=f'https://api.spotify.com/v1/me/albums?offset={offset}&limit={limit}',
                headers={
                    'Authorization': f'Bearer {self.authorization.get_token()}'
                }
            )
            saved_albums_json = response_saved_albums.json()
            saved_albums_info.extend(
                [SavedAlbumInfo.from_json_request_item(item) for item in saved_albums_json['items']]
            )
            offset += limit
            count += 1
            logging.warning(f'{len(saved_albums_info)} albums retrieved so far...')
            if len(saved_albums_json['items']) < limit: break
        return saved_albums_info

    def get_saved_songs(
            self,
            limit: int = 50,
            offset: int = 50
    ):
        count = 0
        saved_songs_info = []
        logging.warning('getting saved songs, this may take a while...')
        for _ in range(1000):
            response_saved_songs = requests.get(
                url=f'https://api.spotify.com/v1/me/tracks?offset={offset}&limit={limit}',
                headers={
                    'Authorization': f'Bearer {self.authorization.get_token()}'
                }
            )
            saved_songs_json = response_saved_songs.json()
            saved_songs_info.extend(
                [SavedSongInfo.from_json_request_item(item) for item in saved_songs_json['items']]
            )
            offset += limit
            count += 1
            logging.warning(f'{len(saved_songs_info)} songs retrieved so far...')
            if len(saved_songs_json['items']) < limit: break
        return saved_songs_info
