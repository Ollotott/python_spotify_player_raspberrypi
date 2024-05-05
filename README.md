# python_spotify_player_raspberrypi
Code for a raspberry pi based, (nearly) fully automated spotify player.

WIP

I wanted to create a box that plays spotify on its own. And then I looked for a way to play spotify on a raspberry pi using python, and... Nothing that did what I wanted it to do.
So I went through all the spotify api docs and stuff and wrote a bunch of code. The spotify_basic_actions.py file contains a bunch of basic spotify commands. And then I made specialized commands that do combinations of these basic commands in the spotify_complex_actions.py file.

I'd be very happy if someone found a use of the spotify basic actions file. 
It uses the authentication code... thing. I mean, to get access to the spotify account in order to mess around with it. You'll need to set up a spotify app to use this, and you probably need a spotify premium account? IDK.
