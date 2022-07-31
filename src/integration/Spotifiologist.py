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

    def update_recently_played(self):
        self._update(
            collection_name=SpotifiologistCollections.LISTENING_LOG,
            getter_function=self.spotify.get_recently_played
        )

    def update_saved_albums(self):
        self._update(
            collection_name=SpotifiologistCollections.SAVED_ALBUMS,
            getter_function=self.spotify.get_saved_albums
        )

    def update_saved_songs(self):
        self._update(
            collection_name=SpotifiologistCollections.SAVED_SONGS,
            getter_function=self.spotify.get_saved_songs
        )

    def _update(
            self,
            collection_name: SpotifiologistCollections,
            getter_function
    ):
        new_info_list = getter_function()
        prior_reference = self.database.read_all_data_from_collection(collection_name)
        for new_info in new_info_list:
            if new_info.uid in prior_reference:
                continue
            else:
                self.database.add_document_to_collection(
                    collection_id=collection_name,
                    document_id=new_info.uid,
                    document_dict=attr.asdict(new_info)
                )