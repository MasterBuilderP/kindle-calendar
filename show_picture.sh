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
DEST_DIR="/mnt/us/"
FILENAME="screen.png"
# ---------------------------

UPDATE_INTERVAL="10s"
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
  python gen_picture.py "$TMP_DIR/$FILENAME"
  NEW_HASH=$(md5sum "$TMP_DIR/$FILENAME" | awk '{print $1}')
  if [[ "$NEW_HASH" != "$HASH" ]]; then
    HASH="$NEW_HASH"
    sshpass -p "$PASSWORD" scp -o ControlPath="$CTRL_PATH" "$TMP_DIR/$FILENAME" "$USER@$HOST:$DEST_DIR/"

    sshpass -p "$PASSWORD" ssh -o ControlPath="$CTRL_PATH" "$USER@$HOST" \
    "/usr/sbin/eips -g $DEST_DIR/$FILENAME > /dev/null"
  fi

  sleep "$UPDATE_INTERVAL"
done
