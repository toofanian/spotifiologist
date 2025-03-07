"""Test script to verify environment setup."""
import sys
from importlib.metadata import version
import spotipy
import pydantic
import loguru

def test_environment():
    """Print environment information."""
    print("\n=== Environment Test Results ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("\nInstalled packages:")
    print(f"spotipy: {version('spotipy')}")
    print(f"pydantic: {version('pydantic')}")
    print(f"loguru: {version('loguru')}")
    print("\nPython path:")
    for path in sys.path:
        print(f"- {path}")

if __name__ == '__main__':
    test_environment()
