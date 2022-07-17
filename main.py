import os.path
import sqlite3

from utils.spotify_interface import SpotifyTalker
from utils.sql_interface import SqlTalker
import attr


@attr.s(auto_attribs=True)
class SpotifyTool:
    spotify_interface: SpotifyTalker
    sql_interface: SqlTalker

    @classmethod
    def from_interfaces(
            cls,
            spotify_interface: SpotifyTalker,
            sql_interface: SqlTalker
    ):
        return cls(
            spotify_interface=spotify_interface,
            sql_interface=sql_interface
        )

    def track_current_track(self):
        current_track_info = self.spotify_interface.get_current_track()
        self.sql_interface.add_tracks_to_timeline([current_track_info['track_name']])


def main():
    if not os.path.isdir('databases'): os.mkdir('databases')
    database_path = 'databases/database.db'
    with sqlite3.connect(database_path) as sql_conn:
        sql_interface = SqlTalker.from_database_connection(sql_conn=sql_conn)

        cred_json_path = '.creds/credentials_spot.json'
        spotify_interface = SpotifyTalker.from_preauthorization(cred_json_path=cred_json_path)

        spotify_tool = SpotifyTool.from_interfaces(spotify_interface=spotify_interface, sql_interface=sql_interface)

        spotify_tool.track_current_track()




if __name__ == '__main__':
    main()
