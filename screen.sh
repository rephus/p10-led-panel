#!/bin/bash


while true; do 
    sudo python pong.py &
    sleep 300
    pgrep -f "pong.py" | xargs sudo kill -9

    sudo python spotify_song.py &
    sleep 10
    pgrep -f "spotify_song.py" | xargs sudo kill -9

    sudo python weather.py &
    sleep 20
    pgrep -f "weather.py" | xargs sudo kill -9

    sudo python snake.py &
    sleep 300
    pgrep -f "snake.py" | xargs sudo kill -9

    sudo python spotify_song.py &
    sleep 10
    pgrep -f "spotify_song.py" | xargs sudo kill -9

    sudo python weather.py &
    sleep 20
    pgrep -f "weather.py" | xargs sudo kill -9

done