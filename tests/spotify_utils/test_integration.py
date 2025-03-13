"""Integration tests for Spotify API functionality."""
from pathlib import Path
import pytest
import time
from unittest.mock import patch
from loguru import logger

from spotify_utils.client import SpotifyClient


@pytest.fixture
def spotify_client():
    """Create a SpotifyClient instance for testing."""
    print("\nInitializing Spotify client for testing...")
    client = SpotifyClient.from_env()
    print("Spotify client initialized successfully!")
    return client


@pytest.mark.timeout(30)
def test_saved_tracks(spotify_client):
    """Test fetching saved tracks from Spotify."""
    print("\nTesting saved tracks API...")
    start_time = time.time()
    
    # Use a very small limit to speed up the test
    tracks = spotify_client.get_saved_tracks(limit=2)
    
    # The API might return more than the limit, so we'll just check structure
    assert len(tracks) > 0
    assert all(hasattr(track, 'name') for track in tracks)
    assert all(hasattr(track, 'artists') for track in tracks)
    assert len(tracks) <= 2, f"Expected at most 2 tracks, got {len(tracks)}"
    
    print(f"✅ Saved tracks test passed! Retrieved {len(tracks)} tracks in {time.time() - start_time:.2f}s")


@pytest.mark.timeout(30)
def test_saved_albums(spotify_client):
    """Test fetching saved albums from Spotify."""
    print("\nTesting saved albums API...")
    start_time = time.time()
    
    # Use a very small limit to speed up the test
    albums = spotify_client.get_saved_albums(limit=2)
    
    # The API might return more than the limit, so we'll just check structure
    assert len(albums) > 0
    assert all(hasattr(album, 'name') for album in albums)
    assert all(hasattr(album, 'artists') for album in albums)
    assert len(albums) <= 2, f"Expected at most 2 albums, got {len(albums)}"
    
    print(f"✅ Saved albums test passed! Retrieved {len(albums)} albums in {time.time() - start_time:.2f}s")


@pytest.mark.timeout(30)
def test_playlists(spotify_client: SpotifyClient):
    """Test fetching playlists from Spotify."""
    print("\nTesting playlists API...")
    start_time = time.time()
    
    # Use a small limit since we just need to verify functionality
    playlists = spotify_client.get_playlists(limit=1)
    
    # Basic structure validation
    assert len(playlists) > 0, "No playlists found"
    playlist = playlists[0]
    assert hasattr(playlist, 'name'), "Playlist missing name"
    assert hasattr(playlist, 'total_tracks'), "Playlist missing total_tracks"
    assert hasattr(playlist, 'id'), "Playlist missing id"
    
    print(f"✅ Playlists test passed! Retrieved playlist '{playlist.name}' in {time.time() - start_time:.2f}s")


@pytest.mark.timeout(30)
def test_playlist_tracks(spotify_client: SpotifyClient):
    """Test fetching tracks from a playlist."""
    print("\nTesting playlist tracks API...")
    start_time = time.time()
    
    # Get a single playlist
    playlists = spotify_client.get_playlists(limit=1)
    assert len(playlists) > 0, "No playlists found"
    
    playlist = playlists[0]
    print(f"  Getting tracks from playlist: {playlist.name}")
    
    # Get just one track to verify functionality
    playlist_tracks = spotify_client.get_playlist_tracks(playlist.id, limit=1)
    assert len(playlist_tracks) > 0, "No tracks found in playlist"
    
    # Basic structure validation
    track = playlist_tracks[0]
    assert track is not None, "Track is None"
    assert hasattr(track, 'name'), "Track missing name"
    assert hasattr(track, 'artists'), "Track missing artists"
    assert hasattr(track, 'position'), "Track missing position"
    assert hasattr(track, 'added_by_id'), "Track missing added_by_id"
    
    print(f"✅ Playlist tracks test passed! Retrieved track '{track.name}' in {time.time() - start_time:.2f}s")


def test_spotify_connection(spotify_client):
    """Test the Spotify API connection by running all test functions."""
    print("\nTesting Spotify API connection...")
    start_time = time.time()
    
    # Just test that the connection works
    result = spotify_client.test_connection()
    assert result is True
    
    print(f"✅ Connection test passed in {time.time() - start_time:.2f}s")


@pytest.mark.skip(reason="Playlist backup feature is still TODO")
@pytest.mark.timeout(60)
def test_backup_playlists(spotify_client: SpotifyClient, tmp_path):
    """Test backing up playlists to a directory.
    This test is skipped as playlist backup is still a TODO feature.
    """
    pytest.skip("Playlist backup feature is still TODO")
