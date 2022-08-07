from abc import ABC, abstractmethod

import attr


@attr.s(auto_attribs=True)
class DocumentInfo(ABC):
    _uid: str

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

    @abstractmethod
    def get_uid(self):
        ...


@attr.s(auto_attribs=True)
class SavedSongInfo(DocumentInfo):
    _uid: str
    _song_name: str
    _album_name: str
    _artist_name: str
    _saved_at: str
    _uri: str

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

    def get_uid(self):
        return self._uid


@attr.s(auto_attribs=True)
class SavedAlbumInfo(DocumentInfo):
    _uid: str
    _album_name: str
    _artist_name: str
    _saved_at: str
    _uri: str

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

    def get_uid(self):
        return self._uid


@attr.s(auto_attribs=True)
class TrackListeningInfo(DocumentInfo):
    _uid: str
    _track_name: str
    _album_name: str
    _artist_name: str
    _played_at: int
    _track_uri: str

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

    def get_uid(self):
        return self._uid
