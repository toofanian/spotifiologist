"""Main entry point for Spotifiologist."""
from loguru import logger
import sys
sys.path.append('src')
from spotify_utils.client import SpotifyClient


def test_spotify_connection():
    """Test the Spotify API connection by fetching some library data."""
    try:
        client = SpotifyClient.from_env()
        
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
    logger.info("Testing Spotify API connection...")
    success = test_spotify_connection()
    
    if success:
        logger.info("\n✅ Spotify API connection test successful!")
    else:
        logger.error("\n❌ Spotify API connection test failed!")


if __name__ == '__main__':
    main()
