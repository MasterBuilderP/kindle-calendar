#!/bin/bash

# sudo ip addr add 192.168.15.201/24 dev usb0
# sudo ip link set usb0 up
# ssh root@192.168.15.244

#!/usr/bin/env bash
set -euo pipefail

# --- connection details ---
USER="root"
HOST="192.168.15.244"
PASSWORD=""
DEST_DIR="/mnt/us/kindle/"
FILENAME="event_cache.json"
# ---------------------------

UPDATE_INTERVAL="60s"
HASH="123"
TMP_DIR="$(mktemp -d)"
CTRL_PATH="$TMP_DIR/cm-%r@%h:%p"

cleanup() {
  echo "Cleaning up..."
  sshpass -p "$PASSWORD" ssh -o ControlPath="$CTRL_PATH" -O exit "$USER@$HOST" >/dev/null 2>&1 || true
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

sshpass -p "$PASSWORD" ssh \
  -M -N -f \
  -o ControlMaster=yes \
  -o ControlPersist=600 \
  -o ControlPath="$CTRL_PATH" \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  "$USER@$HOST" > /dev/null

while true; do
  python calendar_fetch.py
  NEW_HASH=$(md5sum "$FILENAME" | awk '{print $1}')
  if [[ "$NEW_HASH" != "$HASH" ]]; then
    HASH="$NEW_HASH"
    echo Copying to kindle...
    sshpass -p "$PASSWORD" scp -o ControlPath="$CTRL_PATH" "$FILENAME" "$USER@$HOST:$DEST_DIR/"
  fi

  sleep "$UPDATE_INTERVAL"
done
