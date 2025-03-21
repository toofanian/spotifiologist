"""Tests for the Spotify client implementation."""
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from spotify_utils.client import SpotifyClient, SpotifyTrack, SpotifyAlbum, SpotifyPlaylist, PlaylistTrack


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv('SPOTIFY_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('SPOTIFY_CLIENT_SECRET', 'test_client_secret')
    monkeypatch.setenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')


@pytest.fixture
def mock_spotify_track():
    """Create a mock Spotify track response."""
    return {
        'track': {
            'id': 'track123',
            'name': 'Test Track',
            'artists': [{'name': 'Test Artist'}],
            'album': {
                'id': 'album123',
                'name': 'Test Album'
            },
            'duration_ms': 300000,
            'uri': 'spotify:track:track123',
            'is_local': False
        },
        'added_at': '2024-03-14T12:00:00+00:00',
        'played_at': '2024-03-14T12:00:00+00:00',
        'added_by': {'id': 'user123'}
    }


@pytest.fixture
def mock_spotify_album():
    """Create a mock Spotify album response."""
    return {
        'album': {
            'id': 'album123',
            'name': 'Test Album',
            'artists': [{'name': 'Test Artist'}],
            'total_tracks': 12,
            'release_date': '2024-03-06',
            'uri': 'spotify:album:album123'
        },
        'added_at': '2024-03-06T12:00:00Z'
    }


@pytest.fixture
def mock_spotify_playlist():
    """Create a mock Spotify playlist response."""
    return {
        'id': 'playlist123',
        'name': 'Test Playlist',
        'description': 'Test Description',
        'owner': {'id': 'user123'},
        'tracks': {'total': 100},
        'public': True,
        'snapshot_id': 'snapshot123',
        'uri': 'spotify:playlist:playlist123'
    }


def test_spotify_client_initialization(mock_env_vars):
    """Test that the Spotify client can be initialized from environment variables."""
    client = SpotifyClient.from_env()
    assert client.auth_manager is not None
    assert 'user-library-read' in client.auth_manager.scope


def test_spotify_client_missing_env_vars(monkeypatch):
    """Test that client initialization fails with missing environment variables."""
    # Clear all required environment variables
    for var in ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']:
        monkeypatch.delenv(var, raising=False)
    
    with pytest.raises(ValueError) as exc_info:
        # Use ignore_creds_file to ensure we only test env vars
        SpotifyClient.from_env(ignore_creds_file=True)
    
    assert 'Missing required environment variables' in str(exc_info.value)


def test_spotify_track_from_response(mock_spotify_track):
    """Test creating a SpotifyTrack model from API response."""
    track = SpotifyTrack.from_saved_track(mock_spotify_track)
    
    assert track.id == 'track123'
    assert track.name == 'Test Track'
    assert track.artists == ['Test Artist']
    assert track.album_id == 'album123'
    assert track.album_name == 'Test Album'
    assert isinstance(track.added_at, datetime)
    assert isinstance(track.last_seen, datetime)
    assert track.uri == 'spotify:track:track123'


def test_spotify_album_from_response(mock_spotify_album):
    """Test creating a SpotifyAlbum model from API response."""
    album = SpotifyAlbum.from_saved_album(mock_spotify_album)
    
    assert album.id == 'album123'
    assert album.name == 'Test Album'
    assert album.artists == ['Test Artist']
    assert album.total_tracks == 12
    assert album.release_date == '2024-03-06'
    assert isinstance(album.added_at, datetime)
    assert album.uri == 'spotify:album:album123'


def test_spotify_playlist_from_response(mock_spotify_playlist):
    """Test creating a SpotifyPlaylist model from API response."""
    playlist = SpotifyPlaylist.from_playlist(mock_spotify_playlist)
    
    assert playlist.id == 'playlist123'
    assert playlist.name == 'Test Playlist'
    assert playlist.description == 'Test Description'
    assert playlist.owner_id == 'user123'
    assert playlist.total_tracks == 100
    assert playlist.is_public is True
    assert playlist.snapshot_id == 'snapshot123'
    assert playlist.uri == 'spotify:playlist:playlist123'


@patch('spotipy.Spotify')
def test_get_saved_tracks(mock_spotify, mock_env_vars, mock_spotify_track):
    """Test fetching saved tracks from library."""
    # Mock the Spotify API response
    mock_spotify.return_value.current_user_saved_tracks.return_value = {
        'items': [mock_spotify_track],
        'next': None
    }
    
    # Initialize client and fetch tracks
    client = SpotifyClient.from_env()
    tracks = client.get_saved_tracks()
    
    # Verify track data
    assert len(tracks) == 1
    track = tracks[0]
    assert isinstance(track, SpotifyTrack)
    assert track.id == 'track123'
    assert track.name == 'Test Track'
    assert track.artists == ['Test Artist']
    assert track.album_id == 'album123'
    assert track.album_name == 'Test Album'
    assert track.added_at == datetime.fromisoformat('2024-03-14T12:00:00+00:00')
    assert track.duration_ms == 300000
    assert track.uri == 'spotify:track:track123'
    assert isinstance(track.last_seen, datetime)
    
    # Verify API call
    mock_spotify.return_value.current_user_saved_tracks.assert_called_once_with(limit=50)


@patch('spotipy.Spotify')
def test_api_connection(mock_spotify, mock_env_vars):
    """Test that we can successfully connect to the Spotify API.
    
    This is a lightweight test that verifies our credentials work by checking
    if we can get the current user's profile.
    """
    mock_spotify.return_value.current_user.return_value = {
        'id': 'test_user',
        'display_name': 'Test User',
        'type': 'user',
    }
    
    client = SpotifyClient.from_env()
    assert client.test_connection() is True
    mock_spotify.return_value.current_user.assert_called_once()


@patch('spotipy.Spotify')
def test_api_connection_failure(mock_spotify, mock_env_vars):
    """Test that connection test fails gracefully when API errors."""
    mock_spotify.return_value.current_user.side_effect = Exception('API Error')
    
    client = SpotifyClient.from_env()
    assert client.test_connection() is False
    mock_spotify.return_value.current_user.assert_called_once()


def test_playlist_track_from_response(mock_spotify_track):
    """Test creating a PlaylistTrack model from API response."""
    track = PlaylistTrack.from_playlist_track(mock_spotify_track, position=0)
    
    assert track.id == 'track123'
    assert track.name == 'Test Track'
    assert track.artists == ['Test Artist']
    assert track.album_id == 'album123'
    assert track.album_name == 'Test Album'
    assert isinstance(track.added_at, datetime)
    assert track.uri == 'spotify:track:track123'
    assert track.position == 0
    assert track.added_by_id == 'user123'


@patch('spotipy.Spotify')
def test_get_playlist_tracks(mock_spotify, mock_env_vars, mock_spotify_track, mock_spotify_playlist):
    """Test fetching tracks from a playlist."""
    # Mock playlist details call
    mock_spotify.return_value.playlist.return_value = mock_spotify_playlist
    
    # Mock playlist items call
    mock_spotify.return_value.playlist_items.return_value = {
        'items': [mock_spotify_track],
        'next': None
    }
    
    client = SpotifyClient.from_env()
    tracks = client.get_playlist_tracks('playlist123')
    
    assert len(tracks) == 1
    assert isinstance(tracks[0], PlaylistTrack)
    assert tracks[0].id == 'track123'
    assert tracks[0].position == 0
    assert tracks[0].added_by_id == 'user123'
    
    # Verify API calls
    mock_spotify.return_value.playlist.assert_called_once_with('playlist123')
    mock_spotify.return_value.playlist_items.assert_called_once_with('playlist123', limit=5)


@patch('spotipy.Spotify')
def test_get_playlist_tracks_with_local_files(mock_spotify, mock_env_vars):
    """Test that local files and invalid tracks are properly filtered."""
    mock_spotify.return_value.playlist_items.return_value = {
        'items': [
            {
                'track': {
                    'id': None,
                    'is_local': True,
                    'name': 'Local Track'
                },
                'added_at': '2024-03-06T12:00:00Z',
                'added_by': {'id': 'user123'}
            },
            {
                'track': None,
                'added_at': '2024-03-06T12:00:00Z',
                'added_by': {'id': 'user123'}
            }
        ],
        'next': None
    }
    
    client = SpotifyClient.from_env()
    tracks = client.get_playlist_tracks('playlist123')
    
    assert len(tracks) == 0  # All tracks should be filtered out

