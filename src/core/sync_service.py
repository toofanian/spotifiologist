"""
Sync service for keeping Spotify library data in sync with Firestore.
Handles periodic syncs and change tracking.
"""
from datetime import datetime, timezone
from typing import List, Optional, Set

from loguru import logger

from spotify_utils.client import SpotifyClient, SpotifyTrack, SpotifyAlbum, SpotifyPlaylist
from utils_data.storage import LibraryStorage


class LibrarySyncService:
    """Service for syncing Spotify library data with Firestore."""

    def __init__(
        self,
        spotify_client: SpotifyClient,
        storage: LibraryStorage,
    ):
        """Initialize the sync service.
        
        Args:
            spotify_client: Authenticated SpotifyClient instance
            storage: LibraryStorage instance for Firestore operations
        """
        self.spotify: SpotifyClient = spotify_client
        self.storage: LibraryStorage = storage
        
    async def sync_library(self) -> None:
        """Sync entire library with Firestore.
        
        This will:
        1. Fetch all library data from Spotify
        2. Store it in Firestore
        3. Track any changes
        4. Update library statistics
        """
        logger.info("Starting full library sync...")
        
        # Sync tracks
        tracks = self.spotify.get_saved_tracks(limit=None)
        new_tracks = await self.storage.store_tracks(tracks)
        if new_tracks:
            logger.info(f"Added {len(new_tracks)} new tracks to library")
            
        # Sync albums
        albums = self.spotify.get_saved_albums(limit=None)
        new_albums = await self.storage.store_albums(albums)
        if new_albums:
            logger.info(f"Added {len(new_albums)} new albums to library")
            
        # Sync playlists
        playlists = self.spotify.get_playlists(limit=None)
        modified_playlists = []
        
        for playlist in playlists:
            tracks = self.spotify.get_playlist_tracks(playlist.id, limit=None)
            was_modified = await self.storage.store_playlist(playlist, tracks)
            if was_modified:
                modified_playlists.append(playlist.id)
                
        if modified_playlists:
            logger.info(f"Updated {len(modified_playlists)} playlists")
            
        # Update library stats
        stats = await self.storage.update_library_stats()
        logger.info(
            f"Library stats: {stats.total_tracks} tracks, "
            f"{stats.total_albums} albums, {stats.total_playlists} playlists"
        )
        
    async def sync_recent_changes(self, hours: int = 24) -> None:
        """Sync only recent changes to the library.
        
        This is more efficient than a full sync when checking for updates
        frequently. It uses Spotify's API endpoints for recently saved/removed items.
        
        Args:
            hours: How many hours of history to check
        """
        logger.info(f"Checking for library changes in the last {hours} hours...")
        
        # Get recently played tracks
        recent_tracks = self.spotify.get_recently_played(limit=50)
        
        # Process all tracks for listening history
        for track in recent_tracks:
            # Store track in Firestore regardless of save status
            await self.storage.store_tracks([track])
            
        # Check which tracks are saved to library
        track_ids = [track.id for track in recent_tracks]
        saved_statuses = self.spotify.check_saved_tracks(track_ids)
        saved_ids = {
            track_id for track_id, is_saved in zip(track_ids, saved_statuses)
            if is_saved
        }
        
        if saved_ids:
            # Fetch full track data for newly saved tracks
            new_tracks = [
                track for track in self.spotify.get_tracks(list(saved_ids))
                if track  # Filter out None values from potentially invalid IDs
            ]
            await self.storage.store_tracks(new_tracks)
            logger.info(f"Found {len(new_tracks)} newly saved tracks")
            
        # Check playlists for recent modifications
        playlists = self.spotify.get_playlists(limit=None)
        modified_playlists = []
        
        for playlist in playlists:
            # Only fetch tracks if playlist was recently modified
            snapshot_changed = await self._check_playlist_modified(playlist)
            if snapshot_changed:
                tracks = self.spotify.get_playlist_tracks(playlist.id, limit=None)
                was_modified = await self.storage.store_playlist(playlist, tracks)
                if was_modified:
                    modified_playlists.append(playlist.id)
                    
        if modified_playlists:
            logger.info(f"Updated {len(modified_playlists)} modified playlists")
            
        # Update stats if we found any changes
        if saved_ids or modified_playlists:
            await self.storage.update_library_stats()
            
    async def _check_playlist_modified(self, playlist: SpotifyPlaylist) -> bool:
        """Check if a playlist has been modified by comparing snapshot IDs.
        
        Args:
            playlist: Playlist to check
            
        Returns:
            True if the playlist has been modified
        """
        playlist_ref = self.storage._user_ref.collection('playlists').document(playlist.id)
        doc = playlist_ref.get()
        
        if not doc.exists:
            return True
            
        old_data = doc.to_dict()
        return old_data.get('snapshot_id') != playlist.snapshot_id
