import attr


@attr.s(auto_attribs=True)
class TrackListeningInfo:
    uid: str
    track_name: str
    album_name: str
    artist_name: str
    played_at: int
    track_uri: str

    @classmethod
    def from_json_request_item(
            cls,
            json_item: dict
    ):
        uid = json_item['played_at']
        track_name = json_item['track']['name']
        album_name = json_item['track']['album']['name']
        artist_name = json_item['track']['artists'][0]['name']
        played_at = json_item['played_at']
        track_uri = json_item['track']['uri']
        return cls(
            uid, track_name, album_name, artist_name, played_at, track_uri
        )

    @classmethod
    def from_dict(
            cls,
            from_dict: dict
    ):
        uid = from_dict['uid']
        track_name = from_dict['track_name']
        album_name = from_dict['album_name']
        artist_name = from_dict['artist_name']
        played_at = from_dict['played_at']
        track_uri = from_dict['track_uri']
        return cls(
            uid, track_name, album_name, artist_name, played_at, track_uri
        )
