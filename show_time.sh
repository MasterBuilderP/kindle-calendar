#!/bin/bash
set -euo pipefail

DEST_DIR="/mnt/us/"
FILENAME="screen.png"
# ---------------------------

UPDATE_INTERVAL="60"
HASH="123"

while true; do
  python3 gen_picture.py "$DEST_DIR/$FILENAME" --partial
  /usr/sbin/eips -g $DEST_DIR/$FILENAME > /dev/null

  sleep "$UPDATE_INTERVAL"
done
