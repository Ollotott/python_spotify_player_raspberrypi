from spotify_basic_actions import *
from spotify_complex_actions import *
import requests
from library import SPOTIFY_TOKEN_URL, REDIRECT_URI, BASE_64, home, token_storage_file, SPOTIFY_API_URL
import json
import time
from pathlib import Path


if __name__ == "__main__":
    auth_code_storage = Path("/Users/Elliot_1/Desktop/auth_code.json")
    check_if_code(auth_code_storage)

    play("new.", "playlist")
