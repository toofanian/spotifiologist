import logging

import attr
import requests

from src.spotify_utils.spotify_item_info import SavedAlbumInfo, TrackListeningInfo, SavedSongInfo
from src.spotify_utils.spotify_authorization import SpotifyAuthorization


@attr.s(auto_attribs=True)
class ISpotify:
    authorization: SpotifyAuthorization
    _logger = logging.getLogger(__name__)

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
    ):
        """
        :return: tuple, (sorted list of TrackListeningInfo w/ most recent first, before_cursor)
        """
        self._logger.info('getting recently played tracks...')
        response_recently_played = requests.get(
            url=f'https://api.spotify.com/v1/me/player/recently-played?limit=50',
            headers={
                'Authorization': f'Bearer {self.authorization.get_token()}'
            }
        )
        recently_played_json = response_recently_played.json()
        track_listening_info_batch = [
            TrackListeningInfo.from_json_request_item(item) for item in recently_played_json['items']
        ]

        self._logger.info(f'{len(track_listening_info_batch)} tracks retrieved.')
        return track_listening_info_batch

    def get_all_saved_albums(
            self,
         ):
        saved_albums_info = []
        url = f'https://api.spotify.com/v1/me/albums?limit=50'
        self._logger.info('getting saved albums, this may take a while...')
        for iteration in range(1000):
            response_saved_albums = requests.get(
                url=url,
                headers={
                    'Authorization': f'Bearer {self.authorization.get_token()}'
                }
            )
            saved_albums_json = response_saved_albums.json()
            saved_albums_info.extend(
                [SavedAlbumInfo.from_json_request_item(item) for item in saved_albums_json['items']]
            )
            url = saved_albums_json['next']
            self._logger.debug(f'{len(saved_albums_info)} albums retrieved so far...')
            if url is None:
                break
            if iteration >= 999: self._logger.warning(f'Loop safeguard hit. Aborting at {iteration} calls.')

        self._logger.info(f'{len(saved_albums_info)} albums retrieved.')
        return saved_albums_info

    def get_all_saved_songs(
            self,
    ):
        self._logger.info('getting saved songs, this may take a while...')
        saved_songs_info = []
        url = f'https://api.spotify.com/v1/me/tracks?limit=50'
        for iteration in range(1000):
            response_saved_songs = requests.get(
                url=url,
                headers={
                    'Authorization': f'Bearer {self.authorization.get_token()}'
                }
            )
            saved_songs_json = response_saved_songs.json()
            saved_songs_info.extend(
                [SavedSongInfo.from_json_request_item(item) for item in saved_songs_json['items']]
            )
            url = saved_songs_json['next']
            self._logger.debug(f'{len(saved_songs_info)} songs retrieved so far...')
            if url is None: break
            if iteration >= 999: self._logger.warning(f'Loop safeguard hit. Aborting at {iteration} calls.')

        self._logger.info(f'{len(saved_songs_info)} songs retrieved.')
        return saved_songs_info
