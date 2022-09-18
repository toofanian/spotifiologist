import logging

from src.utils_data.firestore_interface import IFirestoreDb
from src.integration.spotifiologist import Spotifiologist
from src.spotify_utils.spotify_authorization import SpotifyAuthorization
from src.spotify_utils.spotify_interface import ISpotify

logging.basicConfig(level=logging.INFO)


def main():
    spotify_tool = Spotifiologist.from_interfaces(
        spotify_interface=ISpotify.from_preauthorization(
            preauthorization=SpotifyAuthorization.from_alex_json(
                auth_json_path='.creds/credentials_spot.json'
            )
        ),
        database_interface=IFirestoreDb.with_env_variable(
            env_var_path='.creds/gcp_credentials_alex-toofanian-main.json'
        )
    )

    spotify_tool.update_recently_played()
    spotify_tool.update_saved_albums()
    spotify_tool.update_saved_songs()


if __name__ == '__main__':
    main()
