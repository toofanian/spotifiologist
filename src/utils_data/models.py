"""
Pydantic models for Firestore document types and data validation.
These models represent the structure of our Firestore documents and provide type safety.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChangeAction(str, Enum):
    """Enum for tracking different types of changes in the library."""
    ADDED = "added"
    REMOVED = "removed"
    UPDATED = "updated"


class ItemChange(BaseModel):
    """Model representing a change to a library item (track, album, etc)."""
    action: ChangeAction
    source: str = Field(description="Source of the change (e.g., 'direct_save', 'playlist_add')")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PlaylistChange(BaseModel):
    """Model representing a change to a playlist."""
    action: ChangeAction
    changes: Dict[str, List[str]] = Field(
        description="Changes made: {'added': [track_ids], 'removed': [track_ids]}"
    )
    previous_snapshot_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LibraryStats(BaseModel):
    """Daily statistics about the user's library."""
    total_tracks: int = 0
    total_albums: int = 0
    total_playlists: int = 0
    genre_distribution: Dict[str, int] = Field(default_factory=dict)
    date: datetime = Field(default_factory=datetime.utcnow)


class DailyDiff(BaseModel):
    """Model representing all changes to the library in a single day."""
    tracks_added: List[str] = Field(default_factory=list)
    tracks_removed: List[str] = Field(default_factory=list)
    albums_added: List[str] = Field(default_factory=list)
    albums_removed: List[str] = Field(default_factory=list)
    playlists_created: List[str] = Field(default_factory=list)
    playlists_deleted: List[str] = Field(default_factory=list)
    playlists_modified: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)
    date: datetime = Field(default_factory=datetime.utcnow)
