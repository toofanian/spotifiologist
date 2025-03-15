"""
Firestore storage implementation for library management.
Handles all interactions with Firestore, including storing library data and tracking changes.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from google.cloud import firestore
from loguru import logger
from spotify_utils.client import SpotifyTrack, SpotifyAlbum, SpotifyPlaylist, PlaylistTrack

from .models import ChangeAction, ItemChange, PlaylistChange, LibraryStats, DailyDiff


class LibraryStorage:
    """Handles storage and retrieval of library data in Firestore."""

    def __init__(self, user_id: str, credentials_path: Optional[str] = None):
        """Initialize the storage client.
        
        Args:
            user_id: Spotify user ID to store data for
            credentials_path: Optional path to service account credentials
        """
        if credentials_path:
            self.db = firestore.Client.from_service_account_json(credentials_path)
        else:
            self.db = firestore.Client()
            
        self.user_id = user_id
        self._user_ref = self.db.collection('users').document(user_id)
        logger.info(f'Initialized Firestore storage for user {user_id}')

    def _get_today_ref(self) -> firestore.DocumentReference:
        """Get reference to today's diff document."""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        return self._user_ref.collection('diffs').document(today)

    async def store_tracks(self, tracks: List[SpotifyTrack]) -> Set[str]:
        """Store tracks in Firestore and track changes.
        
        Args:
            tracks: List of tracks to store
            
        Returns:
            Set of track IDs that were newly added (not previously in library)
        """
        batch = self.db.batch()
        tracks_ref = self._user_ref.collection('tracks')
        new_tracks = set()
        
        # Get existing track IDs for change detection
        existing_docs = {doc.id for doc in tracks_ref.list_documents()}
        
        for track in tracks:
            doc_ref = tracks_ref.document(track.id)
            track_data = track.model_dump()
            
            if track.id not in existing_docs:
                new_tracks.add(track.id)
                # Add change history for new track
                history_ref = doc_ref.collection('history').document()
                change = ItemChange(
                    action=ChangeAction.ADDED,
                    source='library_sync'
                )
                batch.set(history_ref, change.model_dump())
            
            batch.set(doc_ref, track_data, merge=True)
        
        # Commit all changes
        batch.commit()
        
        if new_tracks:
            logger.info(f'Added {len(new_tracks)} new tracks to library')
            # Update today's diff
            diff_ref = self._get_today_ref()
            diff_ref.set({
                'tracks_added': firestore.ArrayUnion(list(new_tracks))
            }, merge=True)
        
        return new_tracks

    async def store_albums(self, albums: List[SpotifyAlbum]) -> Set[str]:
        """Store albums in Firestore and track changes.
        
        Args:
            albums: List of albums to store
            
        Returns:
            Set of album IDs that were newly added
        """
        batch = self.db.batch()
        albums_ref = self._user_ref.collection('albums')
        new_albums = set()
        
        # Get existing album IDs for change detection
        existing_docs = {doc.id for doc in albums_ref.list_documents()}
        
        for album in albums:
            doc_ref = albums_ref.document(album.id)
            album_data = album.model_dump()
            
            if album.id not in existing_docs:
                new_albums.add(album.id)
                # Add change history for new album
                history_ref = doc_ref.collection('history').document()
                change = ItemChange(
                    action=ChangeAction.ADDED,
                    source='library_sync'
                )
                batch.set(history_ref, change.model_dump())
            
            batch.set(doc_ref, album_data, merge=True)
        
        # Commit all changes
        batch.commit()
        
        if new_albums:
            logger.info(f'Added {len(new_albums)} new albums to library')
            # Update today's diff
            diff_ref = self._get_today_ref()
            diff_ref.set({
                'albums_added': firestore.ArrayUnion(list(new_albums))
            }, merge=True)
        
        return new_albums

    async def store_playlist(self, playlist: SpotifyPlaylist, tracks: List[PlaylistTrack]) -> bool:
        """Store a playlist and its tracks, tracking any changes.
        
        Args:
            playlist: Playlist metadata
            tracks: List of tracks in the playlist
            
        Returns:
            True if the playlist was modified
        """
        playlist_ref = self._user_ref.collection('playlists').document(playlist.id)
        old_snapshot = None
        was_modified = False
        
        # Get existing playlist data if it exists
        doc = playlist_ref.get()
        if doc.exists:
            old_data = doc.to_dict()
            old_snapshot = old_data.get('snapshot_id')
        
        # Check if playlist has changed
        if old_snapshot != playlist.snapshot_id:
            was_modified = True
            # Get existing tracks for change detection
            old_tracks = {
                doc.id: doc.to_dict()
                for doc in playlist_ref.collection('tracks').stream()
            }
            
            # Prepare change tracking
            added_tracks = []
            removed_tracks = []
            current_track_ids = set()
            
            # Update tracks
            batch = self.db.batch()
            for track in tracks:
                current_track_ids.add(track.id)
                track_ref = playlist_ref.collection('tracks').document(str(track.position))
                track_data = track.model_dump()
                
                # Check if track is new to this position
                if str(track.position) not in old_tracks or old_tracks[str(track.position)]['track_id'] != track.id:
                    added_tracks.append(track.id)
                
                batch.set(track_ref, track_data)
            
            # Find removed tracks
            for pos, old_track in old_tracks.items():
                if old_track['track_id'] not in current_track_ids:
                    removed_tracks.append(old_track['track_id'])
            
            # Store playlist metadata
            playlist_data = playlist.model_dump()
            batch.set(playlist_ref, playlist_data)
            
            # Record change history
            if added_tracks or removed_tracks:
                history_ref = playlist_ref.collection('history').document()
                change = PlaylistChange(
                    action=ChangeAction.UPDATED,
                    changes={
                        'added': added_tracks,
                        'removed': removed_tracks
                    },
                    previous_snapshot_id=old_snapshot or ''
                )
                batch.set(history_ref, change.model_dump())
                
                # Update today's diff
                diff_ref = self._get_today_ref()
                diff_ref.set({
                    f'playlists_modified.{playlist.id}': {
                        'tracks_added': added_tracks,
                        'tracks_removed': removed_tracks
                    }
                }, merge=True)
            
            # Commit all changes
            batch.commit()
            
            if added_tracks or removed_tracks:
                logger.info(
                    f'Updated playlist {playlist.name}: '
                    f'added {len(added_tracks)} tracks, removed {len(removed_tracks)} tracks'
                )
        
        return was_modified

    async def update_library_stats(self) -> LibraryStats:
        """Update daily library statistics.
        
        Calculates and stores:
        - Total tracks, albums, playlists
        - Genre distribution
        """
        # Get current counts
        tracks_ref = self._user_ref.collection('tracks')
        albums_ref = self._user_ref.collection('albums')
        playlists_ref = self._user_ref.collection('playlists')
        
        total_tracks = len(list(tracks_ref.list_documents()))
        total_albums = len(list(albums_ref.list_documents()))
        total_playlists = len(list(playlists_ref.list_documents()))
        
        # Calculate genre distribution
        genre_dist = {}
        for doc in tracks_ref.stream():
            track_data = doc.to_dict()
            for genre in track_data.get('genres', []):
                genre_dist[genre] = genre_dist.get(genre, 0) + 1
        
        # Create stats object
        stats = LibraryStats(
            total_tracks=total_tracks,
            total_albums=total_albums,
            total_playlists=total_playlists,
            genre_distribution=genre_dist
        )
        
        # Store stats
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        stats_ref = self._user_ref.collection('metadata').document('library_stats')
        stats_ref.collection('daily').document(today).set(stats.model_dump())
        
        logger.info(
            f'Updated library stats: '
            f'{total_tracks} tracks, {total_albums} albums, {total_playlists} playlists'
        )
        
        return stats
