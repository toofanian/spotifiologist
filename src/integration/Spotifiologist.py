import attr

from src.database_utils.nosql_database_interface import INoSqlDatabase
from src.integration.spotifiologist_collections import SpotifiologistCollections
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
        logged_listening_dict = self.database.read_all_data_from_collection(SpotifiologistCollections.LISTENING_LOG)
        recent_track_info = self.spotify.get_recently_played()
        for track_info in recent_track_info:
            if track_info.uid in logged_listening_dict:
                return
            self.database.add_document_to_collection(
                collection_id=SpotifiologistCollections.LISTENING_LOG,
                document_id=track_info.uid,
                document_dict=attr.asdict(track_info)
            )

    def update_saved_albums(self):
        prior_saved_albums_dict = self.database.read_all_data_from_collection(SpotifiologistCollections.SAVED_ALBUMS)
        current_saved_albums_info = self.spotify.get_saved_albums()
        for saved_album_info in current_saved_albums_info:
            if saved_album_info.uid in prior_saved_albums_dict: continue
            self.database.add_document_to_collection(
                collection_id=SpotifiologistCollections.SAVED_ALBUMS,
                document_id=saved_album_info.uid,
                document_dict=attr.asdict(saved_album_info)
            )
