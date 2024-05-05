import string
import time
import requests
import random
from library import CLIENT_ID, REDIRECT_URI
import json
from pathlib import Path


def generate_random_string(length):
    """Generates a random string of the specified length."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(length))


def request_user_authorization():
    """Builds and sends the GET request to request user authorization."""
    state = generate_random_string(16)
    scope = "playlist-modify-public playlist-modify-private streaming user-read-playback-state user-modify-playback-state user-read-private user-read-email user-top-read playlist-read-private playlist-read-collaborative user-library-read"  # Adjust scopes as needed

    url = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }

    # Encode parameters
    encoded_params = requests.compat.urlencode(params)
    auth_url = f"{url}?{encoded_params}"
    print(encoded_params)
    return auth_url, state


if __name__ == "__main__":
    auth_code_file = Path("/Users/Elliot_1/Desktop/auth_code.json")

    print("A page will open shortly, and in it you have to authorise the access to your spotify account.\nDo NOT close any tabs yet!")
    time.sleep(3)

    authorization_url, state = request_user_authorization()
    print(f"Authorization URL: {authorization_url}\nState: {state}")

    auth_code_url = input("You will have been redirected to another URL. Enter that url here!\n\n")
    auth_code = auth_code_url[auth_code_url.find("code=") + 5:auth_code_url.find("&state=")]

    print("You may close the tabs now!")

    if not auth_code_file.exists():
        auth_code_file.touch()
    with auth_code_file.open(mode="w", encoding="utf-8") as file:
        json.dump([{"authentication_code": auth_code, "refresh_token": None}], file)

    print("You now have a json file on your desktop. Place it on a usb stick that you then plug into the pi.")
