import attr


@attr.s(auto_attribs=True)
class SavedAlbumInfo:
    uid: str
    album_name: str
    artist_name: str
    saved_at: str
    uri: str

    @classmethod
    def from_json_request_item(
            cls,
            item: dict
    ):
        uid = item['album']['uri']
        album_name = item['album']['name']
        artist_name = item['album']['artists'][0]['name']
        saved_at = item['added_at']
        uri = item['album']['uri']
        return cls(
            uid, album_name, artist_name, saved_at, uri
        )

    @classmethod
    def from_dict(
            cls,
            from_dict: dict
    ):
        uid = from_dict['uid']
        album_name = from_dict['album_name']
        artist_name = from_dict['artist_name']
        saved_at = from_dict['saved_at']
        uri = from_dict['uri']
        return cls(
            uid, album_name, artist_name, saved_at, uri
        )
