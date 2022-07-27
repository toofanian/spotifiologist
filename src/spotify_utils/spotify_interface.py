import attr
import requests

from src.spotify_utils.spotify_authorization import SpotifyAuthorization


@attr.s(auto_attribs=True)
class TrackListeningInfo:
    track_name: str
    album_name: str
    artist_name: str
    played_at: int
    track_uri: str

    @classmethod
    def from_json_item(
            cls,
            json_item: dict
    ):
        track_name = json_item['track']['name']
        album_name = json_item['track']['album']['name']
        artist_name = json_item['track']['artists'][0]['name']
        played_at = json_item['played_at']
        track_uri = json_item['track']['uri']
        return cls(
            track_name, album_name, artist_name, played_at, track_uri
        )


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
        request_headers_currently_playing = {
            'Authorization': f'Bearer {self.authorization.get_token()}'
        }
        response_currently_playing = requests.get(
            url='https://api.spotify.com/v1/me/player/currently-playing',
            headers=request_headers_currently_playing
        )
        currently_playing_json = response_currently_playing.json()
        return currently_playing_json

    def get_recently_played(self):
        request_headers_recently_played = {
            'Authorization': f'Bearer {self.authorization.get_token()}'
        }
        response_recently_played = requests.get(
            'https://api.spotify.com/v1/me/player/recently-played',
            headers=request_headers_recently_played
        )
        recently_played_json = response_recently_played.json()
        return [TrackListeningInfo.from_json_item(item) for item in recently_played_json['items']]
