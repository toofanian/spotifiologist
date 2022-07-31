from abc import ABC, abstractmethod

import attr


@attr.s(auto_attribs=True)
class DocumentInfo(ABC):
    uid: str

    @classmethod
    @abstractmethod
    def from_json_request_item(
            cls,
            item: dict
    ):
        ...

    @classmethod
    @abstractmethod
    def from_dict(
            cls,
            from_dict: dict
    ):
        ...


@attr.s(auto_attribs=True)
class SavedSongInfo(DocumentInfo):
    uid: str
    song_name: str
    album_name: str
    artist_name: str
    saved_at: str
    uri: str

    @classmethod
    def from_json_request_item(cls, item: dict):
        uid = item['track']['uri']
        song_name = item['track']['name']
        album_name = item['track']['album']['name']
        artist_name = item['track']['artists'][0]['name']
        saved_at = item['added_at']
        uri = item['track']['uri']
        return cls(uid, song_name, album_name, artist_name, saved_at, uri)

    @classmethod
    def from_dict(cls, from_dict: dict):
        uid = from_dict['uid']
        song_name = from_dict['song_name']
        album_name = from_dict['album_name']
        artist_name = from_dict['artist_name']
        saved_at = from_dict['saved_at']
        uri = from_dict['uri']
        return cls(uid, song_name, album_name, artist_name, saved_at, uri)


@attr.s(auto_attribs=True)
class SavedAlbumInfo(DocumentInfo):
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
        return cls(uid, album_name, artist_name, saved_at, uri)

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
        return cls(uid, album_name, artist_name, saved_at, uri)


@attr.s(auto_attribs=True)
class TrackListeningInfo(DocumentInfo):
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
        return cls(uid, track_name, album_name, artist_name, played_at, track_uri)

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
        return cls(uid, track_name, album_name, artist_name, played_at, track_uri)
