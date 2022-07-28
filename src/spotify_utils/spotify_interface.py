import attr
import requests

from src.spotify_utils.spotify_authorization import SpotifyAuthorization
from src.spotify_utils.track_listening_info import TrackListeningInfo


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

    def get_recently_played(self):
        response_recently_played = requests.get(
            url='https://api.spotify.com/v1/me/player/recently-played',
            headers={
                'Authorization': f'Bearer {self.authorization.get_token()}'
            }
        )
        recently_played_json = response_recently_played.json()
        track_listening_info_batch = [
            TrackListeningInfo.from_json_request_item(item) for item in recently_played_json['items']
        ]
        return track_listening_info_batch
