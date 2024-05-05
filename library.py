import base64
from pathlib import Path

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret_id"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://localhost"
PORT = 5000
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = "playlist-modify-public playlist-modify-private streaming user-read-playback-state"

BASE_64 = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode("ascii")).decode("ascii")

token_storage_file = Path("insert your token storage file here. JSON.")


def home(message):
    exit(message)
