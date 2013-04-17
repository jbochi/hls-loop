hls-loop
========

This is a HLS server that streams a 30 minutes test video in loop with 4 bitrates.

Run:

    $ pip install flask
    $ python hls-loop.py


The resources are:

Variant playlist: http://localhost:5000/variant.m3u8
Playlists: http://localhost:5000/playlist[1-4].m3u8
