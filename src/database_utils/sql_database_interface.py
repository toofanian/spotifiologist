import sqlite3
from abc import ABC

import attr


@attr.s(auto_attribs=True)
class ISqlDatabase(ABC):
    ...


@attr.s(auto_attribs=True)
class ISql(ISqlDatabase):
    sql_conn: sqlite3.Connection

    @classmethod
    def from_database_connection(
            cls,
            sql_conn: sqlite3.Connection
    ):
        return cls(
            sql_conn=sql_conn
        )

    def add_tracks_to_timeline(self,
                               track_list: list[str]):
        for track in track_list:
            if isinstance(track, str):
                self.sql_conn.execute(f'insert into listening_log (track_name) values (\'{track}\');')
        self.sql_conn.commit()
