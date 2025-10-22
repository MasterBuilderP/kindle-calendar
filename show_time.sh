#!/bin/bash
set -euo pipefail

DEST_DIR="/mnt/us/"
FILENAME="screen.png"
# ---------------------------

UPDATE_INTERVAL="60"

while true; do
  python3 gen_picture.py "$DEST_DIR/$FILENAME" --kindle
  /usr/sbin/eips -g $DEST_DIR/$FILENAME > /dev/null
  echo 0 > /sys/class/backlight/max77696-bl/brightness

  sleep "$UPDATE_INTERVAL"
done
