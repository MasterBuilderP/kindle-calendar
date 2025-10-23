#!/bin/bash
set -euo pipefail

DEST_DIR="/mnt/us/"
FILENAME="screen.png"

while true; do
  python3 -m kcal render "$DEST_DIR/$FILENAME" --kindle
  /usr/sbin/eips -g $DEST_DIR/$FILENAME > /dev/null
  echo 0 > /sys/class/backlight/max77696-bl/brightness

  sleep "$((60 - $(date +%S)))"
done
