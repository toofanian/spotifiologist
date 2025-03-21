"""Tests for Firestore storage implementation."""
from datetime import datetime, timezone
from unittest.mock import Mock, patch, ANY

import pytest
from google.cloud import firestore
from spotify_utils.client import SpotifyTrack, SpotifyAlbum, SpotifyPlaylist, PlaylistTrack

from utils_data.storage import LibraryStorage
from utils_data.models import ChangeAction, ItemChange, PlaylistChange


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


@pytest.fixture
def mock_playlist_track(mock_track):
    """Create a mock PlaylistTrack."""
    return PlaylistTrack(
        **mock_track.model_dump(),
        position=0,
        added_by_id="user123"
    )


@pytest.fixture
def storage():
    """Create a LibraryStorage instance with mocked Firestore client."""
    with patch('google.cloud.firestore.Client') as mock_client:
        # Mock the user document reference
        mock_user_ref = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        
        # Setup collection/document chain
        mock_client.return_value.collection.return_value.document.return_value = mock_user_ref
        mock_user_ref.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        
        storage = LibraryStorage("test_user")
        storage._user_ref = mock_user_ref
        return storage


@pytest.mark.asyncio
async def test_store_tracks_new(storage, mock_track):
    """Test storing new tracks."""
    # Mock collection references
    tracks_collection = Mock()
    storage._user_ref.collection.return_value = tracks_collection
    tracks_collection.list_documents.return_value = []
    
    # Mock document references
    track_doc = Mock()
    history_collection = Mock()
    history_doc = Mock()
    tracks_collection.document.return_value = track_doc
    track_doc.collection.return_value = history_collection
    history_collection.document.return_value = history_doc
    
    # Create mock batch
    mock_batch = Mock()
    storage.db.batch.return_value = mock_batch
    
    # Store track
    new_tracks = await storage.store_tracks([mock_track])
    
    assert len(new_tracks) == 1
    assert "track123" in new_tracks
    
    # Verify batch operations
    assert mock_batch.set.call_count >= 2  # Track data and history
    mock_batch.commit.assert_called_once()


@pytest.mark.asyncio
async def test_store_tracks_existing(storage, mock_track):
    """Test storing existing tracks."""
    # Mock existing document
    mock_doc = Mock()
    mock_doc.id = "track123"
    storage._user_ref.collection.return_value.list_documents.return_value = [mock_doc]
    
    # Create mock batch
    mock_batch = Mock()
    storage.db.batch.return_value = mock_batch
    
    # Store track
    new_tracks = await storage.store_tracks([mock_track])
    
    assert len(new_tracks) == 0
    
    # Verify batch operations
    mock_batch.set.assert_called_once()  # Only track data, no history
    mock_batch.commit.assert_called_once()


@pytest.mark.asyncio
async def test_store_albums_new(storage, mock_album):
    """Test storing new albums."""
    # Mock no existing documents
    storage._user_ref.collection.return_value.list_documents.return_value = []
    
    # Create mock batch
    mock_batch = Mock()
    storage.db.batch.return_value = mock_batch
    
    # Store album
    new_albums = await storage.store_albums([mock_album])
    
    assert len(new_albums) == 1
    assert "album123" in new_albums
    
    # Verify batch operations
    mock_batch.set.assert_called()
    mock_batch.commit.assert_called_once()


@pytest.mark.asyncio
async def test_store_playlist_new(storage, mock_playlist, mock_playlist_track):
    """Test storing a new playlist."""
    # Mock playlist document and collections
    playlists_collection = Mock()
    playlist_doc = Mock()
    tracks_collection = Mock()
    history_collection = Mock()
    
    storage._user_ref.collection.return_value = playlists_collection
    playlists_collection.document.return_value = playlist_doc
    playlist_doc.collection.side_effect = lambda name: tracks_collection if name == 'tracks' else history_collection
    
    # Mock document methods
    mock_doc = Mock(exists=False)
    playlist_doc.get.return_value = mock_doc
    tracks_collection.stream.return_value = []
    
    # Create mock batch
    mock_batch = Mock()
    storage.db.batch.return_value = mock_batch
    
    # Store playlist
    modified = await storage.store_playlist(mock_playlist, [mock_playlist_track])
    
    assert modified is True
    
    # Verify batch operations
    assert mock_batch.set.call_count >= 2  # Playlist data and track data
    mock_batch.commit.assert_called_once()


@pytest.mark.asyncio
async def test_store_playlist_modified(storage, mock_playlist, mock_playlist_track):
    """Test storing a modified playlist."""
    # Mock existing playlist with different snapshot
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        'snapshot_id': 'old_snap123',
        'name': 'Test Playlist'
    }
    storage._user_ref.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock existing tracks
    mock_tracks_stream = [
        Mock(id='0', to_dict=lambda: {'track_id': 'old_track123'})
    ]
    storage._user_ref.collection.return_value.document.return_value \
        .collection.return_value.stream.return_value = mock_tracks_stream
    
    # Create mock batch
    mock_batch = Mock()
    storage.db.batch.return_value = mock_batch
    
    # Store playlist
    modified = await storage.store_playlist(mock_playlist, [mock_playlist_track])
    
    assert modified is True
    
    # Verify batch operations and change history
    assert mock_batch.set.call_count >= 3  # Playlist data, track data, and history
    mock_batch.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_library_stats(storage):
    """Test updating library statistics."""
    # Mock collection queries
    mock_tracks = [Mock(), Mock()]  # 2 tracks
    mock_albums = [Mock()]  # 1 album
    mock_playlists = [Mock(), Mock(), Mock()]  # 3 playlists
    
    storage._user_ref.collection.return_value.list_documents.side_effect = [
        mock_tracks,
        mock_albums,
        mock_playlists
    ]
    
    # Mock track documents for genre counting
    mock_track_docs = [
        Mock(to_dict=lambda: {'genres': ['rock', 'indie']}),
        Mock(to_dict=lambda: {'genres': ['rock', 'pop']})
    ]
    storage._user_ref.collection.return_value.stream.return_value = mock_track_docs
    
    # Update stats
    stats = await storage.update_library_stats()
    
    assert stats.total_tracks == 2
    assert stats.total_albums == 1
    assert stats.total_playlists == 3
    assert stats.genre_distribution == {'rock': 2, 'indie': 1, 'pop': 1}
    
    # Verify stats were stored
    storage._user_ref.collection.assert_called_with('metadata')


def test_get_today_ref(storage):
    """Test getting today's diff reference."""
    today_ref = storage._get_today_ref()
    
    # Verify the correct collections/documents were accessed
    storage._user_ref.collection.assert_called_with('diffs')
    storage._user_ref.collection.return_value.document.assert_called_once()
