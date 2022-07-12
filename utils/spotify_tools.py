"""
tools generally related to pushing/pulling spotify data
"""

import requests
import json
from pprint import pprint


class SpotifyConn:  # TODO use attrs class setup, throughout
    def __init__(self):
        ...

    def get_auth_token(self):
        client_creds = json.load(open('spot_client.json'))
        client_id = client_creds['client_id']
        client_secret = client_creds['client_secret']

        auth_response = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })

        auth_response_data = auth_response.json()
        token = auth_response_data['access_token']
        return token

    def get_current_track(self) -> str:
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
        assert response.status_code == 200, f'Invalid Response: code {response.status_code}'
        track_info = response.json()
        output = {'track_name': track_info['item']['name']}  # TODO expand to include more track data
        return output


def main():
    spotify_conn = SpotifyConn()
    curr_track = spotify_conn.get_current_track()
    print(curr_track)


if __name__ == '__main__':
    main()
