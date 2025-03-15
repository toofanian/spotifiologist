"""
Spotify API client implementation for library management.
Handles authentication and communication with the Spotify API, focusing on library backup functionality.
"""
from typing import List, Optional
import os
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from pydantic import BaseModel, Field
from loguru import logger


class SpotifyTrack(BaseModel):
    """Model representing a Spotify track with essential metadata."""
    id: str
    name: str
    artists: List[str]
    album_id: str
    album_name: str
    added_at: datetime
    is_local: bool = False
    duration_ms: int
    uri: str

    @classmethod
    def from_saved_track(cls, spotify_track: dict) -> 'SpotifyTrack':
        """Create a SpotifyTrack from a Spotify saved track response."""
        track_data = spotify_track['track']
        return cls(
            id=track_data['id'],
            name=track_data['name'],
            artists=[artist['name'] for artist in track_data['artists']],
            album_id=track_data['album']['id'],
            album_name=track_data['album']['name'],
            added_at=datetime.fromisoformat(spotify_track['added_at'].replace('Z', '+00:00')),
            is_local=track_data.get('is_local', False),
            duration_ms=track_data['duration_ms'],
            uri=track_data['uri']
        )


class PlaylistTrack(SpotifyTrack):
    """Model representing a track within a playlist, including playlist-specific metadata."""
    position: int
    added_by_id: str
    is_local: bool = False

    @classmethod
    def from_playlist_track(cls, spotify_track: dict, position: int) -> 'PlaylistTrack':
        """Create a PlaylistTrack from a Spotify playlist track response."""
        track_data = spotify_track['track']
        if not track_data or not track_data.get('id'):  # Skip local files and None tracks
            return None
        
        return cls(
            id=track_data['id'],
            name=track_data['name'],
            artists=[artist['name'] for artist in track_data['artists']],
            album_id=track_data['album']['id'],
            album_name=track_data['album']['name'],
            added_at=datetime.fromisoformat(spotify_track['added_at'].replace('Z', '+00:00')),
            is_local=track_data.get('is_local', False),
            duration_ms=track_data['duration_ms'],
            uri=track_data['uri'],
            position=position,
            added_by_id=spotify_track['added_by']['id']
        )


class SpotifyAlbum(BaseModel):
    """Model representing a Spotify album with essential metadata."""
    id: str
    name: str
    artists: List[str]
    total_tracks: int
    release_date: str
    added_at: datetime
    uri: str

    @classmethod
    def from_saved_album(cls, spotify_album: dict) -> 'SpotifyAlbum':
        """Create a SpotifyAlbum from a Spotify saved album response."""
        album_data = spotify_album['album']
        return cls(
            id=album_data['id'],
            name=album_data['name'],
            artists=[artist['name'] for artist in album_data['artists']],
            total_tracks=album_data['total_tracks'],
            release_date=album_data['release_date'],
            added_at=datetime.fromisoformat(spotify_album['added_at'].replace('Z', '+00:00')),
            uri=album_data['uri']
        )


class SpotifyPlaylist(BaseModel):
    """Model representing a Spotify playlist with essential metadata."""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    total_tracks: int
    is_public: bool
    snapshot_id: str
    uri: str

    @classmethod
    def from_playlist(cls, spotify_playlist: dict) -> 'SpotifyPlaylist':
        """Create a SpotifyPlaylist from a Spotify playlist response."""
        return cls(
            id=spotify_playlist['id'],
            name=spotify_playlist['name'],
            description=spotify_playlist.get('description'),
            owner_id=spotify_playlist['owner']['id'],
            total_tracks=spotify_playlist['tracks']['total'],
            is_public=spotify_playlist['public'],
            snapshot_id=spotify_playlist['snapshot_id'],
            uri=spotify_playlist['uri']
        )


class SpotifyClient:
    """Handles authentication and communication with the Spotify API."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, access_token: str = None, refresh_token: str = None, cache_path: str = None):
        """Initialize the Spotify client with credentials."""
        scope = ' '.join([
            'user-library-read',
            'playlist-read-private',
            'playlist-read-collaborative'
        ])
        
        # Create cache handler if cache path provided
        cache_handler = CacheFileHandler(cache_path=cache_path) if cache_path else None
        
        # Create auth manager with cache handling
        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            open_browser=False,
            cache_handler=cache_handler
        )
        
        if access_token and refresh_token:
            # Use existing tokens if provided
            self.auth_manager.refresh_token = refresh_token
            self.auth_manager.token_info = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'scope': scope,
                'expires_at': 0  # Force refresh on first use
            }
            
            # Save to cache if path provided
            if cache_path:
                self.auth_manager.cache_handler.save_token_to_cache(self.auth_manager.token_info)
        
        self.client = spotipy.Spotify(auth_manager=self.auth_manager)
        logger.info('Initialized Spotify client')

    @classmethod
    def from_env(cls, ignore_creds_file: bool = False) -> 'SpotifyClient':
        """Create a SpotifyClient instance from environment variables or credentials file.
        
        Args:
            ignore_creds_file: If True, only use environment variables, ignore credentials file.
                               Useful for testing environment variable validation.
        """
        # Check environment variables first
        required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        # If any env vars are missing and we're allowed to use creds file, try that
        if missing_vars and not ignore_creds_file:
            creds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.creds')
            creds_path = os.path.join(creds_dir, 'credentials_spot.json')
            
            if os.path.exists(creds_path):
                try:
                    import json
                    with open(creds_path) as f:
                        creds = json.load(f)
                        
                        # Verify required fields in credentials file
                        if not creds.get('client_id') or not creds.get('client_secret'):
                            raise ValueError('Credentials file missing required fields')
                        
                        # Ensure cache directory exists
                        cache_path = os.path.join(creds_dir, '.spotify_cache')
                        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                        
                        return cls(
                            client_id=creds['client_id'],
                            client_secret=creds['client_secret'],
                            redirect_uri=creds.get('redirect_uri', 'http://127.0.0.1:8888/callback'),
                            access_token=creds.get('access_token'),
                            refresh_token=creds.get('refresh_token'),
                            cache_path=cache_path
                        )
                except Exception as e:
                    logger.warning(f'Failed to load credentials from {creds_path}: {e}')
            
            # If we get here, both env vars and credentials file failed
            raise ValueError(
                f'Missing required credentials. Either provide environment variables {missing_vars} '
                f'or create .creds/credentials_spot.json with client_id and client_secret'
            )
        
        # If we have missing env vars and we're ignoring creds file, fail immediately
        if missing_vars:
            raise ValueError(
                f'Missing required environment variables: {missing_vars}. '
                'Make sure all required variables are set.'
            )
        
        # All env vars are present, use them
        return cls(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI')
        )

    def get_saved_tracks(self, limit: int = 50) -> List[SpotifyTrack]:
        """Fetch saved tracks from the user's library.
        
        Args:
            limit: Maximum number of tracks to return. If None, returns all tracks.
                  Note that the Spotify API may return more items than requested in a single
                  page, so the actual number of tracks returned might need to be limited.
        """
        tracks = []
        # Use a higher per_request limit for efficiency, but still respect the total limit
        per_request = min(50, limit) if limit is not None else 50
        results = self.client.current_user_saved_tracks(limit=per_request)
        
        while results:
            tracks.extend([SpotifyTrack.from_saved_track(item) for item in results['items']])
            
            # Stop if we've reached the requested limit
            if limit is not None and len(tracks) > limit:
                logger.warning(f'Received {len(tracks)} tracks but limit was {limit}. Trimming results.')
                tracks = tracks[:limit]  # Trim to exact limit
                break
            elif limit is not None and len(tracks) == limit:
                break
                
            if not results['next']:
                break
                
            results = self.client.next(results)
        
        logger.info(f'Retrieved {len(tracks)} saved tracks')
        return tracks

    def get_saved_albums(self, limit: int = 50) -> List[SpotifyAlbum]:
        """Fetch saved albums from the user's library.
        
        Args:
            limit: Maximum number of albums to return. If None, returns all albums.
                  Note that the Spotify API may return more items than requested in a single
                  page, so the actual number of albums returned might need to be limited.
        """
        albums = []
        # Use a higher per_request limit for efficiency, but still respect the total limit
        per_request = min(50, limit) if limit is not None else 50
        results = self.client.current_user_saved_albums(limit=per_request)
        
        while results:
            albums.extend([SpotifyAlbum.from_saved_album(item) for item in results['items']])
            
            # Stop if we've reached the requested limit
            if limit is not None and len(albums) > limit:
                logger.warning(f'Received {len(albums)} albums but limit was {limit}. Trimming results.')
                albums = albums[:limit]  # Trim to exact limit
                break
            elif limit is not None and len(albums) == limit:
                break
                
            if not results['next']:
                break
                
            results = self.client.next(results)
        
        logger.info(f'Retrieved {len(albums)} saved albums')
        return albums

    def test_connection(self) -> bool:
        """Test the connection to Spotify API.
        
        Returns:
            bool: True if connection is successful, False otherwise.
            
        This is a lightweight test that verifies our credentials work
        by checking if we can get the current user's profile.
        """
        try:
            user = self.client.current_user()
            logger.info(f'Successfully connected to Spotify API as user {user["id"]}')
            return True
        except Exception as e:
            logger.error(f'Failed to connect to Spotify API: {e}')
            return False

    def get_playlists(self, limit: int = 50) -> List[SpotifyPlaylist]:
        """Fetch playlists from the user's library.
        
        Args:
            limit: Maximum number of playlists to return. If None, returns all playlists.
                  Note that the Spotify API may return more items than requested in a single
                  page, so the actual number of playlists returned might need to be limited.
        """
        playlists = []
        # Use maximum allowed per request to minimize API calls
        per_request = 50  # Maximum allowed by Spotify API
        logger.info(f'Fetching playlists with per_request={per_request}, limit={limit}')
        results = self.client.current_user_playlists(limit=per_request)
        
        while results:
            playlists.extend([SpotifyPlaylist.from_playlist(item) for item in results['items']])
            
            # If we have a limit and we've reached/exceeded it, trim and stop
            if limit is not None:
                if len(playlists) >= limit:
                    if len(playlists) > limit:
                        logger.warning(f'Received {len(playlists)} playlists but limit was {limit}. Trimming results.')
                        playlists = playlists[:limit]  # Trim to exact limit
                    break
            
            # No more pages to fetch
            if not results['next']:
                break
                
            # Get next page if we need more items (either no limit or haven't reached limit)
            results = self.client.next(results)
        
        logger.info(f'Retrieved {len(playlists)} playlists')
        return playlists

    def get_playlist_tracks(self, playlist_id: str, limit: int = 5) -> List[PlaylistTrack]:
        """Fetch tracks from a specific playlist.
        
        Args:
            playlist_id: The Spotify ID of the playlist
            limit: Maximum number of tracks to return. If None, returns all tracks.
                  Note that the Spotify API may return more items than requested in a single
                  page, so the actual number of tracks returned might need to be limited.
            
        Returns:
            List of PlaylistTrack objects, containing track data and playlist-specific metadata
            like position and who added the track.
        """
        # Get playlist details first
        playlist = self.client.playlist(playlist_id)
        playlist_name = playlist.get('name', 'Unknown Playlist')
        
        tracks = []
        position = 0
        # Use the requested limit for the initial API call
        per_request = limit if limit else 100  # Maximum allowed by Spotify API
        logger.info(f'Fetching tracks from playlist "{playlist_name}" with per_request={per_request}, limit={limit}')
        results = self.client.playlist_items(playlist_id, limit=per_request)
        
        while results:
            for item in results['items']:
                # Skip invalid tracks and local files
                if not item.get('track') or item['track'].get('is_local', False):
                    continue
                    
                track = PlaylistTrack.from_playlist_track(item, position)
                if track:  # Skip None tracks (local files)
                    tracks.append(track)
                    position += 1
                
                # If we have a limit and we've reached it, return immediately
                if limit is not None and len(tracks) >= limit:
                    if len(tracks) > limit:
                        logger.warning(f'Received {len(tracks)} tracks but limit was {limit}. Trimming results.')
                        tracks = tracks[:limit]  # Trim to exact limit
                    logger.info(f'Retrieved {len(tracks)} tracks from playlist "{playlist_name}"')
                    return tracks
            
            # No more pages to fetch
            if not results['next']:
                break
                
            # Get next page of results
            results = self.client.next(results)
        
        logger.info(f'Retrieved {len(tracks)} tracks from playlist "{playlist_name}"')
        return tracks
