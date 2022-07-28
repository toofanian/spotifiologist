import attr

from src.database_utils.nosql_database_interface import INoSqlDatabase
from src.spotify_utils.spotify_interface import ISpotify


@attr.s(auto_attribs=True)
class Spotifiologist:
    spotify: ISpotify
    database: INoSqlDatabase

    @classmethod
    def from_interfaces(
            cls,
            spotify_interface: ISpotify,
            database_interface: INoSqlDatabase
    ):
        return cls(
            spotify=spotify_interface,
            database=database_interface
        )

    def log_recently_played(self):
        recent_track_info = self.spotify.get_recently_played()
        for track_info in recent_track_info:
            self.database.add_document(
                collection_id='tracks',
                document_id='1',
                document_dict=attr.asdict(track_info)
            )
