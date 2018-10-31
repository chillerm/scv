#!/bin/sh

./halite --replay-directory replays/ -vvv --width 32 --height 32 --results-as-json "python3 MyBot.py" "python3 MyBot.py"
