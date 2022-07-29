import logging

from src.database_utils.nosql_database_interface import IFirebaseDb
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
        database_interface=IFirebaseDb.with_env_variable(
            env_var_path='.creds/gcp_credentials_alex-toofanian-main.json'
        )
    )

    spotify_tool.log_recently_played()
    spotify_tool.update_saved_albums()
