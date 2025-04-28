"""
Library browser for inspecting Spotify library data.
Provides simple commands to pull, view, and search through your Spotify library.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from spotify_utils.client import SpotifyClient, SpotifyTrack, SpotifyAlbum, SpotifyPlaylist, PlaylistTrack
from utils_data.firestore_storage import FirestoreStorage

class LibraryBrowser:
    """Browser for Spotify library data."""
    
    def __init__(self, client: SpotifyClient, data_dir: str = ".library"):
        """Initialize the library browser.
        
        Args:
            client: Authenticated SpotifyClient instance
            data_dir: Directory to store library data
        """
        self.client = client
        self.data_dir = Path(data_dir)
        self.data_file = self.data_dir / "library_data.json"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
    def pull_library_from_spotify(self, include_playlists: bool = False) -> None:
        """
        Fetch all library data from Spotify and save it locally as JSON. Does NOT push to Firestore.
        Args:
            include_playlists (bool): If True, also fetch playlists and playlist tracks.
        """
        logger.info("Pulling library data from Spotify...")
        # Fetch tracks
        logger.info("Fetching saved tracks from Spotify...")
        tracks = self.client.get_saved_tracks(limit=None)
        logger.info(f"Fetched {len(tracks)} tracks.")
        # Fetch albums
        logger.info("Fetching saved albums from Spotify...")
        albums = self.client.get_saved_albums(limit=None)
        logger.info(f"Fetched {len(albums)} albums.")
        playlists = []
        playlist_tracks = {}
        if include_playlists:
            logger.info("Fetching playlists from Spotify...")
            playlists = self.client.get_playlists(limit=None)
            logger.info(f"Fetched {len(playlists)} playlists.")
            for playlist in playlists:
                logger.info(f"Fetching tracks for playlist: {playlist.name} ({playlist.id})...")
                playlist_tracks[playlist.id] = self.client.get_playlist_tracks(
                    playlist.id, limit=None
                )
                logger.info(f"Fetched {len(playlist_tracks[playlist.id])} tracks for playlist: {playlist.name} ({playlist.id})")
        # Convert to dictionaries for JSON serialization
        track_dicts = [self._track_to_dict(t) for t in tracks]
        album_dicts = [self._album_to_dict(a) for a in albums]
        playlist_dicts = [self._playlist_to_dict(p) for p in playlists]
        playlist_tracks_dict = {
            pid: [self._playlist_track_to_dict(t) for t in tracks]
            for pid, tracks in playlist_tracks.items()
        }
        library_data = {
            "last_updated": datetime.now().isoformat(),
            "tracks": track_dicts,
            "albums": album_dicts,
            "playlists": playlist_dicts,
            "playlist_tracks": playlist_tracks_dict
        }
        with open(self.data_file, 'w') as f:
            json.dump(library_data, f, indent=2)
        logger.info(f"Saved library data to {self.data_file}")
        self._print_summary(library_data)

    def push_library_to_firestore(self, include_playlists: bool = False) -> None:
        """
        Load library data from JSON and push it to Firestore. Also computes and stores a diff and a snapshot.
        Args:
            include_playlists (bool): If True, also push playlists and playlist tracks.
        """
        if not os.path.exists(self.data_file):
            logger.error(f"Library data file not found: {self.data_file}. Run pull_library_from_spotify first.")
            return
        with open(self.data_file, 'r') as f:
            library_data = json.load(f)
        try:
            user_id = self.client.client.current_user()['id']
            fs = FirestoreStorage()
            # Push current library state
            fs.store_tracks(user_id, library_data["tracks"])
            fs.store_albums(user_id, library_data["albums"])
            if include_playlists:
                fs.store_playlists(user_id, library_data["playlists"])
            logger.info(f"Backed up library to Firestore for user {user_id}")
            # Fetch latest snapshot and compute diff
            prev_snapshot = fs.fetch_latest_snapshot(user_id)
            diff = fs.compute_library_diff(prev_snapshot, library_data)
            # Only store diff if not first backup
            if prev_snapshot is not None:
                fs.store_diff(user_id, diff)
            # Store new snapshot
            fs.store_snapshot(user_id, library_data)
        except Exception as e:
            logger.error(f"Failed to back up to Firestore: {e}")

    def pull_library(self, include_playlists: bool = False) -> None:
        """
        Full pipeline: fetch from Spotify, save to JSON, then push to Firestore.
        Args:
            include_playlists (bool): If True, also fetch/push playlists and playlist tracks.
        """
        self.pull_library_from_spotify(include_playlists=include_playlists)
        self.push_library_to_firestore(include_playlists=include_playlists)
        
    def _print_summary(self, data: Dict) -> None:
        """Print a summary of the library data."""
        print("\nLibrary Summary:")
        print(f"Last Updated: {data['last_updated']}")
        print(f"Saved Tracks: {len(data['tracks'])}")
        print(f"Saved Albums: {len(data['albums'])}")
        print(f"Playlists: {len(data['playlists'])}")
        
    def list_tracks(self, search: Optional[str] = None) -> None:
        """List saved tracks, optionally filtered by search term."""
        data = self._load_data()
        tracks = data["tracks"]
        
        if search:
            search = search.lower()
            tracks = [
                t for t in tracks 
                if search in t["name"].lower() or 
                any(search in artist.lower() for artist in t["artists"])
            ]
            
        print("\nSaved Tracks:")
        for track in tracks:
            print(f"- {track['name']} by {', '.join(track['artists'])}")
            
    def list_albums(self, search: Optional[str] = None) -> None:
        """List saved albums, optionally filtered by search term."""
        data = self._load_data()
        albums = data["albums"]
        
        if search:
            search = search.lower()
            albums = [
                a for a in albums
                if search in a["name"].lower() or
                any(search in artist.lower() for artist in a["artists"])
            ]
            
        print("\nSaved Albums:")
        for album in albums:
            print(f"- {album['name']} by {', '.join(album['artists'])}")
            
    def list_playlists(self, search: Optional[str] = None) -> None:
        """List playlists, optionally filtered by search term."""
        data = self._load_data()
        playlists = data["playlists"]
        
        if search:
            search = search.lower()
            playlists = [
                p for p in playlists
                if search in p["name"].lower() or
                (p["description"] and search in p["description"].lower())
            ]
            
        print("\nPlaylists:")
        for playlist in playlists:
            track_count = len(data["playlist_tracks"].get(playlist["id"], []))
            print(f"- {playlist['name']} ({track_count} tracks)")
            if playlist["description"]:
                print(f"  {playlist['description']}")
                
    def view_playlist(self, playlist_id: str) -> None:
        """View detailed information about a specific playlist."""
        data = self._load_data()
        
        # Find playlist
        playlist = next(
            (p for p in data["playlists"] if p["id"] == playlist_id), None
        )
        if not playlist:
            print(f"Playlist {playlist_id} not found")
            return
            
        # Get tracks
        tracks = data["playlist_tracks"].get(playlist_id, [])
        
        print(f"\nPlaylist: {playlist['name']}")
        if playlist["description"]:
            print(f"Description: {playlist['description']}")
        print(f"Owner: {playlist['owner_id']}")
        print(f"Total Tracks: {len(tracks)}")
        print("\nTracks:")
        for track in tracks:
            print(f"- {track['name']} by {', '.join(track['artists'])}")
            print(f"  Added by: {track['added_by_id']} on {track['added_at']}")
            
    def _load_data(self) -> Dict:
        """Load library data from file."""
        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Library data not found at {self.data_file}. "
                "Run pull_library() first."
            )
            
        with open(self.data_file) as f:
            return json.load(f)
            
    @staticmethod
    def _track_to_dict(track: SpotifyTrack) -> Dict:
        """Convert a SpotifyTrack to a dictionary."""
        return {
            "id": track.id,
            "name": track.name,
            "artists": track.artists,
            "album_id": track.album_id,
            "album_name": track.album_name,
            "added_at": track.added_at.isoformat(),
            "duration_ms": track.duration_ms,
            "uri": track.uri
        }
        
    @staticmethod
    def _album_to_dict(album: SpotifyAlbum) -> Dict:
        """Convert a SpotifyAlbum to a dictionary."""
        return {
            "id": album.id,
            "name": album.name,
            "artists": album.artists,
            "total_tracks": album.total_tracks,
            "release_date": album.release_date,
            "added_at": album.added_at.isoformat(),
            "uri": album.uri
        }
        
    @staticmethod
    def _playlist_to_dict(playlist: SpotifyPlaylist) -> Dict:
        """Convert a SpotifyPlaylist to a dictionary."""
        return {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "owner_id": playlist.owner_id,
            "total_tracks": playlist.total_tracks,
            "is_public": playlist.is_public,
            "uri": playlist.uri
        }
        
    @staticmethod
    def _playlist_track_to_dict(track: PlaylistTrack) -> Dict:
        """Convert a PlaylistTrack to a dictionary."""
        return {
            "id": track.id,
            "name": track.name,
            "artists": track.artists,
            "album_id": track.album_id,
            "album_name": track.album_name,
            "added_at": track.added_at.isoformat(),
            "duration_ms": track.duration_ms,
            "uri": track.uri,
            "position": track.position,
            "added_by_id": track.added_by_id
        }
