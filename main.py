import argparse

from src.database_utils.nosql_database_interface import IMongodb
from src.integration.Spotifiologist import Spotifiologist
from src.spotify_utils.spotify_authorization import SpotifyAuthorization
from src.spotify_utils.spotify_interface import ISpotify


if __name__ == '__main__':
    spotify_tool = Spotifiologist.from_interfaces(
        spotify_interface=ISpotify.from_preauthorization(
            preauthorization=SpotifyAuthorization.from_alex_json(
                auth_json_path='.creds/credentials_spot.json'
            )
        ),
        database_interface=IMongodb()
    )

    spotify_tool.log_recently_played()
