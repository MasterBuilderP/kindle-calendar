#!/bin/bash
set -euo pipefail

FILENAME="/mnt/us/screen.png"

while true; do
  python3 -m kcal render "$FILENAME" --kindle
  /usr/sbin/eips -g "$FILENAME" > /dev/null
  echo 0 > /sys/class/backlight/max77696-bl/brightness

  sleep "$((60 - $(date +%S)))"
done
