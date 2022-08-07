import attr

from src.utils_data.firestore_interface import IFirestoreDb
from src.integration.spotifiologist_collections import SpotifiologistCollections
from src.spotify_utils.spotify_interface import ISpotify


@attr.s(auto_attribs=True)
class Spotifiologist:
    spotify: ISpotify
    database: IFirestoreDb

    @classmethod
    def from_interfaces(
            cls,
            spotify_interface: ISpotify,
            database_interface: IFirestoreDb
    ):
        return cls(
            spotify=spotify_interface,
            database=database_interface
        )

    def update_recently_played(self):
        recently_played_list = self.spotify.get_recently_played()
        current_listening_log_dict = self.database.read_all_data_from_collection(
            collection_id=SpotifiologistCollections.LISTENING_LOG
        )
        for recently_played_item in recently_played_list:
            if recently_played_item.uid not in current_listening_log_dict:
                self.database.add_document_to_collection(
                    collection_id=SpotifiologistCollections.LISTENING_LOG,
                    document_id=recently_played_item.uid,
                    document_dict=attr.asdict(recently_played_item)
                )

    def update_saved_albums(self):
        saved_albums_list = self.spotify.get_saved_albums()
        current_saved_albums_dict = self.database.read_all_data_from_collection(
            collection_id=SpotifiologistCollections.SAVED_ALBUMS
        )
        for saved_album in saved_albums_list:
            if saved_album.uid not in current_saved_albums_dict:
                self.database.add_document_to_collection(
                    collection_id=SpotifiologistCollections.SAVED_ALBUMS,
                    document_id=saved_album.uid,
                    document_dict=attr.asdict(saved_album)
                )

    def update_saved_songs(self):
        saved_songs_list = self.spotify.get_saved_songs()
        current_saved_songs_dict = self.database.read_all_data_from_collection(
            collection_id=SpotifiologistCollections.SAVED_SONGS
        )
        for saved_song in saved_songs_list:
            if saved_song.uid not in current_saved_songs_dict:
                self.database.add_document_to_collection(
                    collection_id=SpotifiologistCollections.SAVED_SONGS,
                    document_id=saved_song.uid,
                    document_dict=attr.asdict(saved_song)
                )
