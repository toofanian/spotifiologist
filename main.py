"""Main entry point for Spotifiologist."""
from datetime import datetime
from pathlib import Path
import json
from loguru import logger
import sys
sys.path.append('src')
from spotify_utils.client import SpotifyClient


def backup_playlists(client: SpotifyClient, backup_dir: Path) -> bool:
    """Backup all user playlists and their tracks.
    
    Args:
        client: Authenticated SpotifyClient instance
        backup_dir: Directory to store backup files
        
    Returns:
        bool: True if backup was successful, False otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        playlists_dir = backup_dir / 'playlists'
        playlists_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all user playlists
        playlists = client.get_playlists()
        logger.info(f"Found {len(playlists)} playlists to backup")
        
        # Generate backup timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Save playlist metadata and tracks
        for playlist in playlists:
            # Create playlist-specific directory
            playlist_dir = playlists_dir / playlist.id
            playlist_dir.mkdir(exist_ok=True)
            
            # Save playlist metadata
            metadata_file = playlist_dir / f'metadata_{timestamp}.json'
            with open(metadata_file, 'w') as f:
                json.dump(playlist.dict(), f, indent=2)
            
            # Get and save playlist tracks
            tracks = client.get_playlist_tracks(playlist.id)
            tracks_file = playlist_dir / f'tracks_{timestamp}.json'
            with open(tracks_file, 'w') as f:
                json.dump([track.dict() for track in tracks], f, indent=2)
            
            logger.info(f"Backed up playlist '{playlist.name}' with {len(tracks)} tracks")
        
        return True
        
    except Exception as e:
        logger.error(f"Error backing up playlists: {e}")
        return False


def test_spotify_connection(client: SpotifyClient) -> bool:
    """Test the Spotify API connection by fetching some library data.
    
    Args:
        client: Authenticated SpotifyClient instance
        
    Returns:
        bool: True if connection test was successful, False otherwise
    """
    try:
        # Test fetching saved tracks
        tracks = client.get_saved_tracks(limit=5)
        logger.info(f"Successfully fetched {len(tracks)} tracks:")
        for track in tracks:
            logger.info(f"- {track.name} by {', '.join(track.artists)}")
        
        # Test fetching saved albums
        albums = client.get_saved_albums(limit=5)
        logger.info(f"\nSuccessfully fetched {len(albums)} albums:")
        for album in albums:
            logger.info(f"- {album.name} by {', '.join(album.artists)}")
        
        # Test fetching playlists
        playlists = client.get_playlists(limit=5)
        logger.info(f"\nSuccessfully fetched {len(playlists)} playlists:")
        for playlist in playlists:
            logger.info(f"- {playlist.name} ({playlist.total_tracks} tracks)")
            
            # Test fetching tracks from the first playlist
            if playlist == playlists[0]:
                playlist_tracks = client.get_playlist_tracks(playlist.id, limit=3)
                logger.info(f"  Sample tracks from {playlist.name}:")
                for track in playlist_tracks:
                    logger.info(f"  - {track.name} by {', '.join(track.artists)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing Spotify connection: {e}")
        return False


def main():
    """Main entry point."""
    try:
        # Initialize Spotify client
        client = SpotifyClient.from_env()
        
        # Test API connection
        logger.info("Testing Spotify API connection...")
        if not test_spotify_connection(client):
            logger.error("\n❌ Spotify API connection test failed!")
            return
        logger.info("\n✅ Spotify API connection test successful!")
        
        # Backup playlists
        logger.info("\nStarting playlist backup...")
        backup_dir = Path('.backup')
        if backup_playlists(client, backup_dir):
            logger.info("\n✅ Playlist backup successful!")
            logger.info(f"Backup files saved to: {backup_dir.absolute()}")
        else:
            logger.error("\n❌ Playlist backup failed!")
    
    except Exception as e:
        logger.error(f"\n❌ Error in main: {e}")


if __name__ == '__main__':
    main()
