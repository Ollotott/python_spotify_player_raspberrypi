from spotify_basic_actions import *


def play_artist(artist_name):
    """Takes an artist name as input, then changes the current playback to this artists 'front page'."""

    artist_name = artist_name.lower()
    search_res = search(artist_name, "artist")

    highest_popularity = -1
    resulting_artist = None

    for artist_uri in search_res:
        if search_res[artist_uri]["name"].lower() == artist_name and search_res[artist_uri]["popularity"] > highest_popularity:
            resulting_artist = artist_uri
            highest_popularity = search_res[artist_uri]["popularity"]

    if resulting_artist:
        play_content(resulting_artist)
        return True
    else:
        print("Error, could not find Artist:", artist_name)
        return False


def play_song_album_by(content_name, content_type="album", artist=None):
    if artist:
        artist = artist.lower()
    content_name = content_name.lower()
    search_res = search(content_name, content_type, artist)

    resulting_item = None
    print(search_res)
    for uri in search_res:
        if content_name in search_res[uri]["name"].lower():
            resulting_item = uri
            play_content(resulting_item)
            return True

    print("Error, could not find:", content_name)
    return False


def search_albums_by(artist_name):
    artist_name = artist_name.lower()
    search_res = search(artist_name, "artist")

    highest_popularity = -1
    resulting_artist = None

    for artist_uri in search_res:
        if search_res[artist_uri]["name"].lower() == artist_name and search_res[artist_uri]["popularity"] > highest_popularity:
            resulting_artist = artist_uri
            highest_popularity = search_res[artist_uri]["popularity"]

    if resulting_artist:
        print("Find Artist - Success")
        artist_albums = artists_albums(resulting_artist)

        # TODO: A way to choose items. Also if the names of the items are really long. Damn musicians!
        for album in artist_albums:
            print(album)
        usr_request = input("Write the first few letters.\n").lower()

        for album in artist_albums:
            if album.lower().startswith(usr_request):
                play_content(artist_albums[album]["uri"])

    else:
        print("Find Artist - Fail")


def play(item_name, content_type="track"):
    """Searches the users library, then the saved albums, the songs, then albums, then playlists."""
    item_name = item_name.lower()

    content_name = None
    content_creator = None
    final_uri = None

    # here we check if the user has a playlist saved
    usr_playlists = user_playlists()
    for playlist in usr_playlists:
        if usr_playlists[playlist]["name"].lower() == item_name:
            final_uri = playlist
            content_name = usr_playlists[playlist]["name"]
            content_creator = None

    # here we check if the user has a saved album
    usr_albums = get_user_saved_albums()
    for album in usr_albums:
        if item_name in usr_albums[album]["name"].lower():
            final_uri = album
            content_name = usr_albums[album]["name"]
            content_creator = usr_albums[album]["artists"]

    # we search for songs
    if content_type == "track":
        search_res = search(item_name, "track")
        for uri in search_res:
            if item_name in search_res[uri]["name"].lower():
                final_uri = uri
                content_name = search_res[uri]["name"]
                content_creator = search_res[uri]["artists"]

    # searches for albums
    elif content_type == "album":
        search_res = search(item_name, "album")
        for uri in search_res:
            if item_name in search_res[uri]["name"].lower():
                final_uri = uri
                content_name = search_res[uri]["name"]
                content_creator = search_res[uri]["artists"]

    # searches for playlists
    elif content_type == "playlist":
        search_res = search(item_name, "playlist")
        for uri in search_res:
            if item_name in search_res[uri]["name"].lower():
                final_uri = uri
                content_name = search_res[uri]["name"]
                content_creator = None

    if content_name and final_uri:
        play_content(final_uri)
        print("Playing:", content_name)
        # TODO: Some way to display the info to the user.
    else:
        print("Could not find", content_type, ":", item_name)


if __name__ == "__main__":
    pass
