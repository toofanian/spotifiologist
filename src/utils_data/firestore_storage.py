from typing import Dict, Any, Optional
from google.cloud import firestore
from loguru import logger
import os

class FirestoreStorage:
    """
    Handles Firestore operations for Spotify library backup.
    """
    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        creds_path = '/Users/alextoofanian/Code/spotifiologist/.creds/gcp_credentials_alex-toofanian-main.json'
        if credentials_path is not None:
            creds_path = credentials_path
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Firestore credentials not found at {creds_path}. Please ensure the file exists.")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        if project_id is None:
            project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            project_id = "alex-toofanian-main"
        if not project_id:
            raise ValueError("Firestore project_id must be set via argument, environment variable, or code default.")
        logger.info(f"Using Firestore project_id: {project_id}")
        self.client = firestore.Client(project=project_id)
        logger.info(f"Initialized Firestore client for project {project_id}")


    def store_snapshot(self, user_id: str, library_data: Dict[str, Any], timestamp: Optional[str] = None):
        """
        Store a full snapshot of the library under users/{user_id}/snapshots/{timestamp}.
        If timestamp is None, use current UTC ISO timestamp.
        """
        from datetime import datetime, timezone
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
        snapshot_ref = self.client.collection("users").document(user_id).collection("snapshots").document(timestamp)
        snapshot_data = {
            "tracks": library_data.get("tracks", []),
            "albums": library_data.get("albums", []),
            "playlists": library_data.get("playlists", []),
            "created_at": timestamp
        }
        snapshot_ref.set(snapshot_data)
        logger.info(f"Stored snapshot for user {user_id} at {timestamp} with {len(snapshot_data['tracks'])} tracks, {len(snapshot_data['albums'])} albums, {len(snapshot_data['playlists'])} playlists.")

    def fetch_latest_snapshot(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the most recent snapshot for a user, or None if none exist.
        """
        snapshots = self.client.collection("users").document(user_id).collection("snapshots")
        query = snapshots.order_by("created_at", direction=firestore.Query.DESCENDING).limit(1)
        docs = list(query.stream())
        if docs:
            logger.info(f"Fetched latest snapshot for user {user_id} at {docs[0].id}")
            return docs[0].to_dict()
        logger.info(f"No snapshot found for user {user_id}")
        return None

    def store_diff(self, user_id: str, diff: Dict[str, Any], timestamp: Optional[str] = None):
        """
        Store a diff document under users/{user_id}/diffs/{timestamp}.
        """
        from datetime import datetime, timezone
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
        diff_ref = self.client.collection("users").document(user_id).collection("diffs").document(timestamp)
        diff_data = dict(diff)
        diff_data["created_at"] = timestamp
        diff_ref.set(diff_data)
        logger.info(f"Stored diff for user {user_id} at {timestamp}: +{len(diff.get('added_tracks', []))} tracks, -{len(diff.get('removed_tracks', []))} tracks, +{len(diff.get('added_albums', []))} albums, -{len(diff.get('removed_albums', []))} albums, +{len(diff.get('added_playlists', []))} playlists, -{len(diff.get('removed_playlists', []))} playlists.")

    @staticmethod
    def compute_library_diff(prev: Optional[Dict[str, Any]], curr: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute the diff between two library snapshots. Returns dict with added/removed for tracks, albums, playlists.
        """
        def id_set(items):
            return set(item['id'] for item in items)
        prev_tracks = prev.get('tracks', []) if prev else []
        curr_tracks = curr.get('tracks', [])
        prev_albums = prev.get('albums', []) if prev else []
        curr_albums = curr.get('albums', [])
        prev_playlists = prev.get('playlists', []) if prev else []
        curr_playlists = curr.get('playlists', [])
        prev_track_ids = id_set(prev_tracks)
        curr_track_ids = id_set(curr_tracks)
        prev_album_ids = id_set(prev_albums)
        curr_album_ids = id_set(curr_albums)
        prev_playlist_ids = id_set(prev_playlists)
        curr_playlist_ids = id_set(curr_playlists)
        added_tracks = [t for t in curr_tracks if t['id'] not in prev_track_ids]
        removed_tracks = [t for t in prev_tracks if t['id'] not in curr_track_ids]
        added_albums = [a for a in curr_albums if a['id'] not in prev_album_ids]
        removed_albums = [a for a in prev_albums if a['id'] not in curr_album_ids]
        added_playlists = [p for p in curr_playlists if p['id'] not in prev_playlist_ids]
        removed_playlists = [p for p in prev_playlists if p['id'] not in curr_playlist_ids]
        return {
            "added_tracks": added_tracks,
            "removed_tracks": removed_tracks,
            "added_albums": added_albums,
            "removed_albums": removed_albums,
            "added_playlists": added_playlists,
            "removed_playlists": removed_playlists,
        }

