"""Tests for the library sync service."""
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from spotify_utils.client import SpotifyTrack, SpotifyAlbum, SpotifyPlaylist, PlaylistTrack
from utils_data.storage import LibraryStorage
from core.sync_service import LibrarySyncService


@pytest.fixture
def mock_spotify():
    """Create a mock SpotifyClient."""
    return Mock()


@pytest.fixture
def mock_storage():
    """Create a mock LibraryStorage."""
    storage = Mock(spec=LibraryStorage)
    
    # Mock Firestore document reference chain
    mock_user_ref = Mock()
    mock_tracks_collection = Mock()
    mock_playlists_collection = Mock()
    mock_track_doc = Mock(exists=False)
    mock_playlist_doc = Mock(exists=False)
    
    # Set up the _user_ref attribute
    storage._user_ref = mock_user_ref
    
    # Set up collection/document chain
    def mock_get_collection(name):
        if name == 'tracks':
            return mock_tracks_collection
        elif name == 'playlists':
            return mock_playlists_collection
        return Mock()
    
    mock_user_ref.collection = mock_get_collection
    mock_tracks_collection.document.return_value = mock_track_doc
    mock_playlists_collection.document.return_value = mock_playlist_doc
    
    # Set up document methods
    mock_track_doc.get.return_value = Mock(exists=False)
    mock_playlist_doc.get.return_value = Mock(exists=False)
    mock_track_doc.to_dict.return_value = {}
    mock_playlist_doc.to_dict.return_value = {}
    
    # Set up store methods to return empty lists
    storage.store_tracks.return_value = []
    storage.store_playlist.return_value = True
    storage.update_library_stats.return_value = None
    
    return storage


@pytest.fixture
def sync_service(mock_spotify, mock_storage):
    """Create a LibrarySyncService with mocked dependencies."""
    return LibrarySyncService(mock_spotify, mock_storage)


@pytest.fixture
def mock_track():
    """Create a mock SpotifyTrack."""
    now = datetime.now(timezone.utc)
    return SpotifyTrack(
        id="track123",
        name="Test Track",
        artists=["Test Artist"],
        album_id="album123",
        album_name="Test Album",
        added_at=now,
        duration_ms=300000,
        uri="spotify:track:track123",
        last_seen=now
    )


@pytest.fixture
def mock_album():
    """Create a mock SpotifyAlbum."""
    return SpotifyAlbum(
        id="album123",
        name="Test Album",
        artists=["Test Artist"],
        total_tracks=12,
        release_date="2024-03-14",
        added_at=datetime.now(timezone.utc),
        uri="spotify:album:album123"
    )


@pytest.fixture
def mock_playlist():
    """Create a mock SpotifyPlaylist."""
    return SpotifyPlaylist(
        id="playlist123",
        name="Test Playlist",
        description="Test Description",
        owner_id="user123",
        total_tracks=1,
        is_public=True,
        snapshot_id="snap123",
        uri="spotify:playlist:playlist123"
    )


@pytest.mark.asyncio
async def test_sync_library_new_items(sync_service, mock_track, mock_album, mock_playlist):
    """Test syncing library with new items."""
    # Setup mock returns
    sync_service.spotify.get_saved_tracks.return_value = [mock_track]
    sync_service.spotify.get_saved_albums.return_value = [mock_album]
    sync_service.spotify.get_playlists.return_value = [mock_playlist]
    sync_service.spotify.get_playlist_tracks.return_value = [
        PlaylistTrack(
            **mock_track.model_dump(),
            position=0,
            added_by_id="user123"
        )
    ]
    
    # Setup storage returns
    sync_service.storage.store_tracks.return_value = {"track123"}
    sync_service.storage.store_albums.return_value = {"album123"}
    sync_service.storage.store_playlist.return_value = True
    
    # Run sync
    await sync_service.sync_library()
    
    # Verify all methods were called
    sync_service.spotify.get_saved_tracks.assert_called_once_with(limit=None)
    sync_service.spotify.get_saved_albums.assert_called_once_with(limit=None)
    sync_service.spotify.get_playlists.assert_called_once_with(limit=None)
    sync_service.spotify.get_playlist_tracks.assert_called_once_with("playlist123", limit=None)
    
    sync_service.storage.store_tracks.assert_called_once()
    sync_service.storage.store_albums.assert_called_once()
    sync_service.storage.store_playlist.assert_called_once()
    sync_service.storage.update_library_stats.assert_called_once()


@pytest.mark.asyncio
async def test_sync_library_no_changes(sync_service, mock_track, mock_album, mock_playlist):
    """Test syncing library with no changes."""
    # Setup mock returns
    sync_service.spotify.get_saved_tracks.return_value = [mock_track]
    sync_service.spotify.get_saved_albums.return_value = [mock_album]
    sync_service.spotify.get_playlists.return_value = [mock_playlist]
    sync_service.spotify.get_playlist_tracks.return_value = [
        PlaylistTrack(
            **mock_track.model_dump(),
            position=0,
            added_by_id="user123"
        )
    ]
    
    # Setup storage returns - no new items
    sync_service.storage.store_tracks.return_value = set()
    sync_service.storage.store_albums.return_value = set()
    sync_service.storage.store_playlist.return_value = False
    
    # Run sync
    await sync_service.sync_library()
    
    # Verify methods were still called
    sync_service.storage.store_tracks.assert_called_once()
    sync_service.storage.store_albums.assert_called_once()
    sync_service.storage.store_playlist.assert_called_once()
    sync_service.storage.update_library_stats.assert_called_once()


@pytest.mark.asyncio
async def test_sync_recent_changes_new_tracks(sync_service, mock_track):
    """Test syncing recent changes with new tracks."""
    # Setup mock returns
    sync_service.spotify.get_recently_played.return_value = [mock_track]
    sync_service.spotify.check_saved_tracks.return_value = [True]  # Track was saved
    
    # Mock track document reference chain
    mock_tracks_collection = Mock()
    mock_track_doc = Mock(exists=False)
    mock_track_doc.get.return_value = Mock(exists=False)
    mock_track_doc.to_dict.return_value = {}
    
    def mock_get_collection(name):
        if name == 'tracks':
            return mock_tracks_collection
        return Mock()
    
    sync_service.storage._user_ref.collection = mock_get_collection
    mock_tracks_collection.document.return_value = mock_track_doc
    sync_service.storage.store_tracks.return_value = []
    
    # Run sync
    await sync_service.sync_recent_changes(hours=24)
    
    # Verify correct methods were called
    sync_service.spotify.get_recently_played.assert_called_once_with(limit=50)
    sync_service.spotify.check_saved_tracks.assert_called_once_with(["track123"])
    sync_service.storage.store_tracks.assert_called_once_with([mock_track])
    sync_service.storage.update_library_stats.assert_called_once()


@pytest.mark.asyncio
async def test_sync_recent_changes_modified_playlist(sync_service, mock_playlist, mock_track):
    """Test syncing recent changes with modified playlist."""
    # Setup mock returns
    sync_service.spotify.get_recently_played.return_value = []
    sync_service.spotify.get_playlists.return_value = [mock_playlist]
    
    # Mock track document reference chain
    mock_tracks_collection = Mock()
    mock_track_doc = Mock(exists=False)
    mock_track_doc.get.return_value = Mock(exists=False)
    mock_track_doc.to_dict.return_value = {}
    
    # Mock playlist document reference chain
    mock_playlists_collection = Mock()
    mock_playlist_doc = Mock(exists=True)
    mock_playlist_doc.get.return_value = Mock(exists=True)
    mock_playlist_doc.to_dict.return_value = {"snapshot_id": "old_snap123"}
    
    # Set up collection/document chain
    def mock_get_collection(name):
        if name == 'tracks':
            return mock_tracks_collection
        elif name == 'playlists':
            return mock_playlists_collection
        return Mock()
    
    sync_service.storage._user_ref.collection = mock_get_collection
    mock_tracks_collection.document.return_value = mock_track_doc
    mock_playlists_collection.document.return_value = mock_playlist_doc
    
    # Mock playlist tracks
    sync_service.spotify.get_playlist_tracks.return_value = [
        PlaylistTrack(
            **mock_track.model_dump(),
            position=0,
            added_by_id="user123"
        )
    ]
    sync_service.storage.store_playlist.return_value = True
    sync_service.storage.store_tracks.return_value = []
    
    # Run sync
    await sync_service.sync_recent_changes(hours=24)
    
    # Verify playlist was checked and updated
    sync_service.spotify.get_playlist_tracks.assert_called_once_with("playlist123", limit=None)
    sync_service.storage.store_playlist.assert_called_once()
    sync_service.storage.update_library_stats.assert_called_once()


@pytest.mark.asyncio
async def test_check_playlist_modified(sync_service, mock_playlist):
    """Test checking if a playlist was modified."""
    # Test case 1: Playlist doesn't exist yet
    mock_doc = Mock(exists=False)
    sync_service.storage._user_ref.collection().document().get.return_value = mock_doc
    
    modified = await sync_service._check_playlist_modified(mock_playlist)
    assert modified is True
    
    # Test case 2: Playlist exists but was modified
    mock_doc = Mock(exists=True)
    mock_doc.to_dict.return_value = {"snapshot_id": "old_snap123"}
    sync_service.storage._user_ref.collection().document().get.return_value = mock_doc
    
    modified = await sync_service._check_playlist_modified(mock_playlist)
    assert modified is True
    
    # Test case 3: Playlist exists and wasn't modified
    mock_doc = Mock(exists=True)
    mock_doc.to_dict.return_value = {"snapshot_id": "snap123"}
    sync_service.storage._user_ref.collection().document().get.return_value = mock_doc
    
    modified = await sync_service._check_playlist_modified(mock_playlist)
    assert modified is False
