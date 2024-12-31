# python_spotify_player_raspberrypi
Code for controlling your spotify player.

I wanted to create a box that plays spotify on its own. And then I looked for a way to play spotify on a raspberry pi using python, and... Nothing that did what I wanted it to do.
So I went through all the spotify api docs and stuff and wrote some code. The spotify_basic_actions.py file contains basic spotify commands (think play, pause, search song, play playlist/soong/album). And then I made specialized commands that do combinations of these basic commands in the spotify_complex_actions.py file.

I'd be very happy if someone found a use in this.
It uses the authentication code flow in order to get access to a spotify accound. You'll need to set up a "spotify app" (see spotify docs) to use this, and you probably need a spotify premium account.
