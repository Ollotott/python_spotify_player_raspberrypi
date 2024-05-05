import requests
from library import SPOTIFY_TOKEN_URL, REDIRECT_URI, BASE_64, home, token_storage_file, SPOTIFY_API_URL
import json
import time
from pathlib import Path


def api_success(response):
    """Checks the api status code response for success of command."""
    response_code = response.status_code

    ok_codes = (200, 201, 202, 204)
    unauthorized_codes = (401, 403)
    server_broken_codes = (500, 502, 503)

    if response_code in ok_codes:
        return True
    elif response_code == 400:
        print("Error - Bad Request.")
    elif response_code in unauthorized_codes:
        print("Error - Unauthorized.")
    elif response_code in server_broken_codes:
        print("Error - Server Malfunction.")
    elif response_code == 404:
        print("Error - Resource not found.")
    else:
        print(f"Error - Unknown Code.")

    print(f"    Error Code: {response_code}")

    try:
        print("    " + str(response.json()))
    except requests.exceptions.JSONDecodeError:
        print("    No additional Data to be parsed.")
    return False


def check_connection():
    """We check the internet connection so that we don't get any stupid errors. Returns true or false"""
    try:
        response = requests.get("https://google.com", timeout=10)
        print("Internet - Go")
    except requests.ConnectionError:
        home("No internet connection.")


def authorisation():
    """Me being lazy."""
    refresh, access, access_time = token_read()
    if time.time() - float(access_time) > 3000:
        success, access, refresh = refresh_access_token(refresh)

        if not success:
            print(success)
            home("Could not get new access token using refresh token!")
        else:
            print("We got ourselves a new access token.")

        token_storage(refresh, access)
    headers = {
        "Authorization": "Bearer " + access
    }
    return headers


def token_storage(ref_token=None, acc_token=None):
    """Stores the given tokens in a json file containing a dict. Also stores the time at which the access token was made."""
    if not token_storage_file.exists():
        token_storage_file.touch()

    # stores only the refresh token
    if ref_token is not None and acc_token is None:
        with token_storage_file.open(mode="r", encoding="utf-8") as file:
            access_token_data = json.load(file)[0]
            time_stamp = access_token_data["time_stamp"]
            stored_access_token = access_token_data["access_token"]

        with token_storage_file.open(mode="w", encoding="utf-8") as file:
            json.dump([{"refresh_token": ref_token, "access_token": stored_access_token, "time_stamp": time_stamp}], file)

    # stores only the access token and time
    elif ref_token is None and acc_token is not None:
        with token_storage_file.open(mode="r", encoding="utf-8") as file:
            access_token_data = json.load(file)[0]
            refresh = access_token_data["refresh_token"]

        with token_storage_file.open(mode="w", encoding="utf-8") as file:
            json.dump([{"refresh_token": refresh, "access_token": acc_token, "time_stamp": str(time.time())}], file)

    elif ref_token is not None and acc_token is not None:
        with token_storage_file.open(mode="w", encoding="utf-8") as file:
            json.dump([{"refresh_token": ref_token, "access_token": acc_token, "time_stamp": str(time.time())}], file)


def token_read(to_be_read="ra"):
    """Reads the stored tokens from the json file. Spits out: refresh, access, time access was made."""
    with token_storage_file.open(mode="r", encoding="utf-8") as file:
        access_token_data = json.load(file)[0]

    if "r" in to_be_read.lower() and "a" not in to_be_read.lower():
        return access_token_data["refresh_token"]
    elif "a" in to_be_read.lower() and "r" not in to_be_read.lower():
        return access_token_data["access_token"], access_token_data["time_stamp"]
    else:
        return access_token_data["refresh_token"], access_token_data["access_token"], access_token_data["time_stamp"]


def get_access_token(access_code):
    """Uses the access code to get the access token and the refresh token."""
    # https://developer.spotify.com/documentation/web-api/tutorials/code-flow
    data = {
        "grant_type": "authorization_code",
        "code": access_code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        "Authorization": "Basic " + BASE_64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    response_data = response.json()

    if api_success(response):
        return True, response_data.get("access_token"), response_data.get("refresh_token")
    else:
        print(response_data)
        home("Getting access token from Spotify API failed.\n'Bad' response.")


def refresh_access_token(refresh):
    """Gets a new access token using the refresh token."""
    # https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens

    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + BASE_64
    }

    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=body)
    response_data = response.json()
    if response.status_code == 200:
        return True, response_data.get("access_token"), response_data.get("refresh_token")
    else:
        print(response_data)
        home("Failed refreshing the access token using the refresh token. Failed communicating with server.")


def usr_playback_state():
    """Self-explanatory, innit?"""
    # https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback

    url = SPOTIFY_API_URL + "/me/player"
    response = requests.get(url, headers=authorisation())
    print(response)
    if api_success(response):
        try:
            response_data = response.json()
            return response_data
        except requests.exceptions.JSONDecodeError:
            home("No Active Device!")
    else:
        specifics = "No known reason."
        if response.status_code == 204:
            specifics = "No active Device"
        home("Error getting user playback state!\n" + specifics)


def play_pause():
    """Wait what?! This function pauses the playback! And continues playback!!! Who would have thunk it?!"""
    # https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback
    # https://developer.spotify.com/documentation/web-api/reference/pause-a-users-playback

    # we check if it's currently paused or playing
    response_data = usr_playback_state()

    if response_data.get("is_playing"):
        action = "pause"
    else:
        action = "play"

    # we change the playback state
    url = SPOTIFY_API_URL + "/me/player/" + action

    response = requests.put(url, headers=authorisation())
    if api_success(response):
        print(action + " - Success")
    else:
        print(action + " - Fail")


def skip():
    """We skip to the next song. Odd."""
    # https://developer.spotify.com/documentation/web-api/reference/skip-users-playback-to-next-track
    url = SPOTIFY_API_URL + "/me/player/next"
    response = requests.post(url, headers=authorisation())
    if api_success(response):
        print("Skip - Success")
    else:
        print("Skip - Fail")


def previous():
    """Changes the current track being played. If we have played more than 10 seconds, we play the last track, else we rewind."""
    # https://developer.spotify.com/documentation/web-api/reference/skip-users-playback-to-previous-track
    # https://developer.spotify.com/documentation/web-api/reference/seek-to-position-in-currently-playing-track

    # we check the playback done.
    response_data = usr_playback_state()
    if response_data.get("progress_ms") < 10000:  # less than 10 seconds into the song.
        # skips to previous
        url = SPOTIFY_API_URL + "/me/player/previous"
        response = requests.post(url, headers=authorisation())
        if api_success(response):
            print("Previous - Success")
        else:
            print("Previous - Fail")
    else:
        # we play the current song from the beginning.
        url = SPOTIFY_API_URL + "/me/player/seek?position_ms=0"
        response = requests.put(url, headers=authorisation())
        if api_success(response):
            print("Set Progress to 0 - Success")
        else:
            print("Set Progress to 0 - Fail")


def change_volume(amount):
    """We change the volume by the amount specified."""
    # https://developer.spotify.com/documentation/web-api/reference/set-volume-for-users-playback

    # gets the current volume
    current_volume = int(usr_playback_state()["device"]["volume_percent"])

    # defines the new volume using the current volume
    if current_volume + amount > 100:
        final_amount = 100
    elif current_volume + amount < 0:
        final_amount = 0
    else:
        final_amount = current_volume + amount

    # sends the new volume to the api.
    url = SPOTIFY_API_URL + "/me/player/volume?volume_percent=" + str(final_amount)
    response = requests.put(url=url, headers=authorisation())

    if api_success(response):
        print("Volume Set - Success")
    else:
        print("Volume Set - Fail")


def play_content(uri):
    """Changes the currently playing song/album/playlist. URI parameter is a string. You can enter several tracks as a long string, separated by ','."""
    # https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback

    url = SPOTIFY_API_URL + "/me/player/play"
    # they
    if "track" in uri:
        data = {
            "uris": uri.split(","),
            "position_ms": 0,
            "offset": {"position": 0}
        }
    else:
        data = {
            "context_uri": uri,
        }

    response = requests.put(url, headers=authorisation(), data=json.dumps(data))
    if api_success(response):
        print("Changing Track - Success")
    else:
        print("Changing Track - Fail")


def transfer_playback(device):
    """We change the currently playing device. Can be used to keep an idling spotify connect device active."""
    # https://developer.spotify.com/documentation/web-api/reference/transfer-a-users-playback

    url = SPOTIFY_API_URL + "/me/player"
    data = {"device_ids": [device]}
    response = requests.put(url, headers=authorisation(), data=json.dumps(data))
    if api_success(response):
        print("Device Change - Success")
    else:
        print("Device Change - Fail")


def add_to_queue(uri):
    """Adds a single song to the queue."""
    # https://developer.spotify.com/documentation/web-api/reference/add-to-queue

    url = SPOTIFY_API_URL + "/me/player/queue?uri=" + uri
    response = requests.post(url, headers=authorisation())
    if api_success(response):
        print("Add to queue - Success")
    else:
        print("Add to queue - Fail")


def change_repeat_state():
    """We change the repeat state in the same order as it is done in the app."""
    # https://developer.spotify.com/documentation/web-api/reference/set-repeat-mode-on-users-playback

    url = SPOTIFY_API_URL + "/me/player/repeat?state="
    current_state = usr_playback_state()["repeat_state"]
    # we set it to track
    if current_state == "off":
        url += "context"
        action_done = "context"
    # we set it to context
    elif current_state == "context":
        url += "track"
        action_done = "track"
    # we turn it off
    else:
        url += "off"
        action_done = "off"

    response = requests.put(url, headers=authorisation())
    if api_success(response):
        print(f"Change Repeat State to {action_done} - Success")
    else:
        print(f"Change Repeat State to {action_done} - Fail")


def get_user_profile():
    """Gets info about the user. IDK why I wasted my time building this function."""
    # https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
    url = SPOTIFY_API_URL + "/me"
    header = authorisation()
    print(header)
    response = requests.get(url, headers=header)

    if api_success(response):
        print("Getting User Data - Success")
        return response.json()
    else:
        print("Getting User Data - Fail")
        return None


def get_available_devices():
    """Gets the users active devices. Not spotify connect devices, but regular old devices with spotify opened."""
    # https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices

    url = SPOTIFY_API_URL + "/me/player/devices"
    response = requests.get(url, headers=authorisation())
    if api_success(response):
        print("Get Available Devices - Success")
        return response.json()
    else:
        print("Get Available Devices - Fail")
        return None


def user_playlists():
    """Spits out da dict with the uri as key and the name as data."""
    # https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists

    url = SPOTIFY_API_URL + "/me/playlists?offset=0&limit=50"
    response = requests.get(url, headers=authorisation())
    if api_success(response):
        print("Get Playlists - Success")
        playlists = response.json()["items"]
        resulting_dict = {}
        for playlist in playlists:
            resulting_dict[playlist["uri"]] = {"name": playlist["name"]}
        return resulting_dict
    else:
        print("Get Playlists - Fail")
        return None


def get_user_saved_albums():
    """Spits out the users saved albums. 'Tis a dictionary with the album name as key and then another dictionary in there, containing 'uri' and 'artists'."""
    # https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums
    url = SPOTIFY_API_URL + "/me/albums?offset=0&limit=50"
    response = requests.get(url, headers=authorisation())
    if api_success(response):
        albums_list = response.json()["items"]
        resulting_dict = {}
        for album in albums_list:
            artists = []
            for artist in album["album"]["artists"]:
                artists.append(artist["name"])

            resulting_dict[album["album"]["uri"]] = {"name": album["album"]["name"], "artists": artists}

        print("Get Albums - Success")
        return resulting_dict
    else:
        print("Get Albums - Fail")
        return None


def current_track_to_playlist(playlist):
    """Adds the currently playing track to the specified playlist."""
    # https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist

    print(playlist[17:])
    track = "spotify:track:" + usr_playback_state()["item"]["id"]

    url = SPOTIFY_API_URL + "/playlists/" + playlist[17:] + "/tracks?uris=" + track
    print("Url:", url)

    response = requests.post(url, headers=authorisation())
    print(response)
    if api_success(response):
        print("Add Song to Playlist - Success")
        return True
    else:
        print("Add Song to Playlist - Fail")
        return False


def search(query, kind, artist=None):
    """We search. Wee!"""
    # https://developer.spotify.com/documentation/web-api/reference/search

    kind = kind.lower()
    accepted_kinds = ("album", "playlist", "track", "artist")

    if kind not in accepted_kinds:
        return None

    url = SPOTIFY_API_URL + "/search?q=" + query + "&" + "type=" + kind
    if artist and kind != "playlist" and kind != "artist":
        url += "&artist=" + artist

    response = requests.get(url, headers=authorisation())
    if api_success(response):
        print("Search - Success")
        response_data = response.json()

        res_dict = {}
        if kind == "album":
            for item in response_data["albums"]["items"]:
                artists = []
                for artist in item["artists"]:
                    artists.append(artist["name"])

                res_dict[item["uri"]] = {"artists": artists, "name": item["name"]}
        elif kind == "track":
            for item in response_data["tracks"]["items"]:
                artists = []
                for artist in item["artists"]:
                    artists.append(artist["name"])

                res_dict[item["uri"]] = {"artists": artists, "name": item["name"]}
        elif kind == "artist":
            for item in response_data["artists"]["items"]:
                res_dict[item["uri"]] = {"name": item["name"], "popularity": item["popularity"]}
        elif kind == "playlist":
            for item in response_data["playlists"]["items"]:
                res_dict[item["uri"]] = {"name": item["name"]}

        return res_dict
    else:
        print("Search - Fail")
        return False


def artists_albums(uri):
    """Gets a dictionary of an artists albums with their respective uris."""
    # https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
    url = SPOTIFY_API_URL + "/artists/" + uri[15:] + "/albums?limit=50"
    response = requests.get(url, headers=authorisation())
    if api_success(response):
        print("Get Artist Albums - Success")

        resulting_dict = {}

        response_data = response.json()
        for item in response_data["items"]:
            resulting_dict[item["name"]] = {"uri": item["uri"]}  # yes, I consciously didn't go with the normal way of doing it, as this is easier for my application.

        return resulting_dict
    else:
        print("Get Artist Albums - Fail")


def toggle_shuffle():
    if usr_playback_state()["shuffle_state"]:
        url = SPOTIFY_API_URL + "/me/player/shuffle?state=false"
    else:
        url = SPOTIFY_API_URL + "/me/player/shuffle?state=true"
    response = requests.put(url, headers=authorisation())
    if api_success(response):
        print("Toggle Shuffle - Success")
    else:
        print("Toggle Shuffle - Fail")


def check_if_code(code_storage):
    # gets the authentication code and uses it to get the access token and refresh token
    # this only has to be done once!
    code_storage = Path("/Users/Elliot_1/Desktop/auth_code.json")
    if code_storage.exists():
        print("Creating new tokens using the authentication code.")
        with code_storage.open(mode="r", encoding="utf-8") as file:
            contents = json.load(file)[0]
        auth_code = contents["authentication_code"]

        success_y_n, access, refresh = get_access_token(auth_code)

        token_storage(refresh, access)
        print("Got new access token!")
    else:
        print("Using stored tokens.")


if __name__ == "__main__":
    # gets the authentication code and uses it to get the access token and refresh token
    # this only has to be done once!
    auth_code_storage = Path("/Users/Elliot_1/Desktop/auth_code.json")
    check_if_code(auth_code_storage)


    # phone: 1134c72e6d3e7d2c4d1bedfaec82797cb8b6f3f7
    # pi: c2b648f11b8f0be20e4c5812d5ae65879003a190

# functions we want:
    # open library --> get users saved albums and get users playlists
    # repeat/shuffle button --> create the menu and stuffs with which to toggle repeat/shuffle
    # save current song --> current track to playlist

    # voice to text
