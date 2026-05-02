#!/bin/bash
set -e

Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Give Xvfb a moment to initialize before x11vnc tries to connect
sleep 1

x11vnc -display :99 -forever -shared -nopw -bg -o /tmp/x11vnc.log

exec python3 main.py
