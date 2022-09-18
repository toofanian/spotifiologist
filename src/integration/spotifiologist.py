import logging

import attr

from src.utils_data.firestore_interface import IFirestoreDb
from src.integration.spotifiologist_collections import SpotifiologistCollections
from src.spotify_utils.spotify_interface import ISpotify


@attr.s(auto_attribs=True)
class Spotifiologist:
    _spotify: ISpotify
    _database: IFirestoreDb
    _logger = logging.getLogger(__name__)

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
        recently_played_list = self._spotify.get_recently_played()
        current_listening_log_dict = self._database.read_all_data_from_collection(
            collection_id=SpotifiologistCollections.LISTENING_LOG
        )
        count_added = 0
        for recently_played_item in recently_played_list:
            if recently_played_item.get_uid() not in current_listening_log_dict:
                self._database.add_document_to_collection(
                    collection_id=SpotifiologistCollections.LISTENING_LOG,
                    document_id=recently_played_item.get_uid(),
                    document_dict=attr.asdict(recently_played_item)
                )
                count_added += 1
        self._logger.info(f'Added {count_added} items to the listening log.')

    def update_saved_albums(self):
        saved_albums_list = self._spotify.get_all_saved_albums()
        current_saved_albums_dict = self._database.read_all_data_from_collection(
            collection_id=SpotifiologistCollections.SAVED_ALBUMS
        )
        count_added = 0
        for saved_album in saved_albums_list:
            if saved_album.get_uid() not in current_saved_albums_dict:
                self._database.add_document_to_collection(
                    collection_id=SpotifiologistCollections.SAVED_ALBUMS,
                    document_id=saved_album.get_uid(),
                    document_dict=attr.asdict(saved_album)
                )
                count_added += 1
        self._logger.info(f'Added {count_added} albums to the database.')

    def update_saved_songs(self):
        saved_songs_list = self._spotify.get_all_saved_songs()
        current_saved_songs_dict = self._database.read_all_data_from_collection(
            collection_id=SpotifiologistCollections.SAVED_SONGS
        )
        count_added = 0
        for saved_song in saved_songs_list:
            if saved_song.get_uid() not in current_saved_songs_dict:
                self._database.add_document_to_collection(
                    collection_id=SpotifiologistCollections.SAVED_SONGS,
                    document_id=saved_song.get_uid(),
                    document_dict=attr.asdict(saved_song)
                )
                count_added += 1
        self._logger.info(f'Added {count_added} songs to the database.')