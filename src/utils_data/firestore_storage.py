from typing import List, Dict, Any, Optional
from google.cloud import firestore
from google.oauth2 import service_account
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

    def store_tracks(self, user_id: str, tracks: List[Dict[str, Any]]):
        col = self.client.collection("users").document(user_id).collection("tracks")
        for track in tracks:
            col.document(track['id']).set(track)
        logger.info(f"Stored {len(tracks)} tracks to Firestore for user {user_id}")

    def store_albums(self, user_id: str, albums: List[Dict[str, Any]]):
        col = self.client.collection("users").document(user_id).collection("albums")
        for album in albums:
            col.document(album['id']).set(album)
        logger.info(f"Stored {len(albums)} albums to Firestore for user {user_id}")

    def store_playlists(self, user_id: str, playlists: List[Dict[str, Any]]):
        col = self.client.collection("users").document(user_id).collection("playlists")
        for playlist in playlists:
            col.document(playlist['id']).set(playlist)
        logger.info(f"Stored {len(playlists)} playlists to Firestore for user {user_id}")

    def fetch_tracks(self, user_id: str) -> List[Dict[str, Any]]:
        col = self.client.collection("users").document(user_id).collection("tracks")
        docs = col.stream()
        return [doc.to_dict() for doc in docs]

    def fetch_albums(self, user_id: str) -> List[Dict[str, Any]]:
        col = self.client.collection("users").document(user_id).collection("albums")
        docs = col.stream()
        return [doc.to_dict() for doc in docs]

    def fetch_playlists(self, user_id: str) -> List[Dict[str, Any]]:
        col = self.client.collection("users").document(user_id).collection("playlists")
        docs = col.stream()
        return [doc.to_dict() for doc in docs]
