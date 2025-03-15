"""Tests for Firestore data models."""
from datetime import datetime, timezone
import pytest

from utils_data.models import (
    ChangeAction,
    ItemChange,
    PlaylistChange,
    LibraryStats,
    DailyDiff
)


def test_change_action_enum():
    """Test ChangeAction enum values."""
    assert ChangeAction.ADDED == "added"
    assert ChangeAction.REMOVED == "removed"
    assert ChangeAction.UPDATED == "updated"
    
    # Test enum validation
    with pytest.raises(ValueError):
        ItemChange(action="invalid", source="test")


def test_item_change():
    """Test ItemChange model."""
    timestamp = datetime.now(timezone.utc)
    change = ItemChange(
        action=ChangeAction.ADDED,
        source="test",
        timestamp=timestamp
    )
    
    assert change.action == ChangeAction.ADDED
    assert change.source == "test"
    assert change.timestamp == timestamp
    
    # Test default timestamp
    change = ItemChange(action=ChangeAction.ADDED, source="test")
    assert isinstance(change.timestamp, datetime)


def test_playlist_change():
    """Test PlaylistChange model."""
    changes = {
        "added": ["track1", "track2"],
        "removed": ["track3"]
    }
    
    change = PlaylistChange(
        action=ChangeAction.UPDATED,
        changes=changes,
        previous_snapshot_id="abc123"
    )
    
    assert change.action == ChangeAction.UPDATED
    assert change.changes == changes
    assert change.previous_snapshot_id == "abc123"
    assert isinstance(change.timestamp, datetime)


def test_library_stats():
    """Test LibraryStats model."""
    genre_dist = {"rock": 10, "jazz": 5}
    stats = LibraryStats(
        total_tracks=100,
        total_albums=20,
        total_playlists=5,
        genre_distribution=genre_dist
    )
    
    assert stats.total_tracks == 100
    assert stats.total_albums == 20
    assert stats.total_playlists == 5
    assert stats.genre_distribution == genre_dist
    assert isinstance(stats.date, datetime)
    
    # Test default values
    stats = LibraryStats()
    assert stats.total_tracks == 0
    assert stats.total_albums == 0
    assert stats.total_playlists == 0
    assert stats.genre_distribution == {}


def test_daily_diff():
    """Test DailyDiff model."""
    diff = DailyDiff(
        tracks_added=["track1", "track2"],
        tracks_removed=["track3"],
        albums_added=["album1"],
        albums_removed=[],
        playlists_created=["playlist1"],
        playlists_deleted=[],
        playlists_modified={
            "playlist2": {
                "tracks_added": ["track4"],
                "tracks_removed": ["track5"]
            }
        }
    )
    
    assert len(diff.tracks_added) == 2
    assert len(diff.tracks_removed) == 1
    assert len(diff.albums_added) == 1
    assert len(diff.albums_removed) == 0
    assert len(diff.playlists_created) == 1
    assert len(diff.playlists_deleted) == 0
    assert "playlist2" in diff.playlists_modified
    assert isinstance(diff.date, datetime)
    
    # Test default values
    diff = DailyDiff()
    assert diff.tracks_added == []
    assert diff.tracks_removed == []
    assert diff.albums_added == []
    assert diff.albums_removed == []
    assert diff.playlists_created == []
    assert diff.playlists_deleted == []
    assert diff.playlists_modified == {}
