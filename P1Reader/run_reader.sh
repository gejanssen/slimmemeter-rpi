#!/usr/bin/env bash

# call this from crontab

# we try a few times as the serial output can be crappy.
for i in 1 2 3 4 5 6; do
    python3.9 P1_reader_dsmr50.py
    if [ $?  -eq 0 ]; then
        break
    fi
done
