"""Main entry point for Spotifiologist."""
from pathlib import Path
import json
from datetime import datetime
import argparse
from loguru import logger
import sys
sys.path.append('src')
from spotify_utils.client import SpotifyClient
from core.utils import json_converter
from core.library_browser import LibraryBrowser


def backup_playlists(client: SpotifyClient, backup_dir: Path, limit: int | None = None) -> bool:
    """Backup all user playlists and their tracks.
    
    Args:
        client: Authenticated SpotifyClient instance
        backup_dir: Directory to store backup files
        limit: Optional limit on number of playlists/tracks to backup
        
    Returns:
        bool: True if backup was successful, False otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        playlists_dir = backup_dir / 'playlists'
        playlists_dir.mkdir(parents=True, exist_ok=True)
        
        # Get user playlists
        playlists = client.get_playlists(limit=limit)
        logger.info(f"Found {len(playlists)} playlists to backup{' (limited)' if limit else ''}")
        
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
                json.dump(playlist.dict(), f, indent=2, default=json_converter)
            
            # Get and save playlist tracks
            tracks = client.get_playlist_tracks(playlist.id, limit=limit)
            tracks_file = playlist_dir / f'tracks_{timestamp}.json'
            with open(tracks_file, 'w') as f:
                json.dump([track.dict() for track in tracks], f, indent=2, default=json_converter)
            
            logger.info(f"Backed up playlist '{playlist.name}' with {len(tracks)} tracks")
        
        return True
        
    except Exception as e:
        logger.error(f"Error backing up playlists: {e}")
        return False





def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Spotify Library Management Tool')
    parser.add_argument('command', choices=['backup', 'browse'], help='Command to execute')
    parser.add_argument('--action', choices=['pull', 'tracks', 'albums', 'playlists', 'view-playlist'],
                        help='Action for browse command')
    parser.add_argument('--search', help='Search term for listing items')
    parser.add_argument('--playlist-id', help='Playlist ID for viewing specific playlist')
    parser.add_argument('--limit', type=int, help='Limit number of items to process')
    
    args = parser.parse_args()
    
    try:
        # Initialize Spotify client
        client = SpotifyClient.from_env()
        
        # Verify API connection
        logger.info("Verifying Spotify API connection...")
        if not client.test_connection():
            logger.error("\n❌ Spotify API connection failed!")
            return
        logger.info("\n✅ Spotify API connection successful!")
        
        if args.command == 'backup':
            # Backup playlists
            logger.info("\nStarting playlist backup...")
            backup_dir = Path('.backup')
            if backup_playlists(client, backup_dir, limit=args.limit):
                logger.info("\n✅ Playlist backup successful!")
                logger.info(f"Backup files saved to: {backup_dir.absolute()}")
            else:
                logger.error("\n❌ Playlist backup failed!")
        
        elif args.command == 'browse':
            browser = LibraryBrowser(client)
            
            if args.action == 'pull':
                browser.pull_library()
            elif args.action == 'tracks':
                browser.list_tracks(args.search)
            elif args.action == 'albums':
                browser.list_albums(args.search)
            elif args.action == 'playlists':
                browser.list_playlists(args.search)
            elif args.action == 'view-playlist' and args.playlist_id:
                browser.view_playlist(args.playlist_id)
            else:
                parser.error("--action is required for browse command")
    
    except Exception as e:
        logger.error(f"\n❌ Error in main: {e}")


if __name__ == '__main__':
    main()
