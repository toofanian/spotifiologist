import argparse
from spotify_utils.client import SpotifyClient
from core.library_browser import LibraryBrowser
from utils_data.firestore_storage import FirestoreStorage
import sys
from google.cloud import firestore


def cmd_sync(args):
    client = SpotifyClient.from_env()
    browser = LibraryBrowser(client)
    browser.pull_library_from_spotify(include_playlists=args.include_playlists)
    browser.push_library_to_firestore(include_playlists=args.include_playlists)
    print("Sync complete!")

def cmd_show_diffs(args):
    fs = FirestoreStorage()
    client = SpotifyClient.from_env()
    user_id = client.client.me()['id']
    diffs_col = fs.client.collection("users").document(user_id).collection("diffs")
    docs = list(diffs_col.order_by("created_at", direction=firestore.Query.DESCENDING).limit(args.n).stream())
    if not docs:
        print("No diffs found.")
        return
    for doc in docs:
        diff = doc.to_dict()
        print(f"\n=== Diff at {diff['created_at']} ===")
        print(f"+{len(diff.get('added_tracks', []))} tracks, -{len(diff.get('removed_tracks', []))} tracks")
        print(f"+{len(diff.get('added_albums', []))} albums, -{len(diff.get('removed_albums', []))} albums")
        print(f"+{len(diff.get('added_playlists', []))} playlists, -{len(diff.get('removed_playlists', []))} playlists")
        if args.verbose:
            for k in ['added_tracks', 'removed_tracks', 'added_albums', 'removed_albums', 'added_playlists', 'removed_playlists']:
                if diff.get(k):
                    print(f"  {k}:")
                    for item in diff[k]:
                        print(f"    - {item.get('name', item.get('album_name', item.get('id')))}")

def cmd_show_snapshots(args):
    fs = FirestoreStorage()
    client = SpotifyClient.from_env()
    user_id = client.client.me()['id']
    snaps_col = fs.client.collection("users").document(user_id).collection("snapshots")
    docs = list(snaps_col.order_by("created_at", direction=firestore.Query.DESCENDING).limit(args.n).stream())
    if not docs:
        print("No snapshots found.")
        return
    for doc in docs:
        snap = doc.to_dict()
        print(f"Snapshot: {snap['created_at']} | Tracks: {len(snap['tracks'])} | Albums: {len(snap['albums'])} | Playlists: {len(snap['playlists'])}")

def main():
    parser = argparse.ArgumentParser(description="Spotifiologist CLI - Sync and browse your Spotify library backups and diffs.")
    subparsers = parser.add_subparsers(dest='command')

    sync_parser = subparsers.add_parser('sync', help='Sync your Spotify library and store snapshot/diff in Firestore')
    sync_parser.add_argument('--include-playlists', action='store_true', help='Include playlists in the sync')
    sync_parser.set_defaults(func=cmd_sync)

    diffs_parser = subparsers.add_parser('show-diffs', help='Show recent diffs (changes between backups)')
    diffs_parser.add_argument('-n', type=int, default=5, help='Number of diffs to show')
    diffs_parser.add_argument('--verbose', action='store_true', help='Show detailed lists of changes')
    diffs_parser.set_defaults(func=cmd_show_diffs)

    snaps_parser = subparsers.add_parser('show-snapshots', help='Show recent backup snapshots')
    snaps_parser.add_argument('-n', type=int, default=5, help='Number of snapshots to show')
    snaps_parser.set_defaults(func=cmd_show_snapshots)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
