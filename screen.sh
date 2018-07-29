#!/bin/bash


while true; do

    hour=$(date +"%H")
    
    # From 0AM to 9AM, reduce brightness
    if [ "$hour" -lt "9" ]; then
      echo "default=5" > "brightness.py"
    else
      echo "default=15" > "brigthness.py"
    fi
    
    sudo python pong.py &
    sleep 300
    pgrep -f "pong.py" | xargs sudo kill -9

    sudo python spotify_song.py &
    sleep 30
    pgrep -f "spotify_song.py" | xargs sudo kill -9

    sudo python weather.py &
    sleep 20
    pgrep -f "weather.py" | xargs sudo kill -9

    sudo python snake.py &
    sleep 300
    pgrep -f "snake.py" | xargs sudo kill -9

    sudo python spotify_song.py &
    sleep 30
    pgrep -f "spotify_song.py" | xargs sudo kill -9

    sudo python weather.py &
    sleep 20
    pgrep -f "weather.py" | xargs sudo kill -9
    
done