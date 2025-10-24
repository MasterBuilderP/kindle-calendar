#!/bin/bash
set -euo pipefail

# --- connection details ---
USER="root"
HOST="192.168.15.244"
PASSWORD=""
DEST_DIR="/mnt/us/kcal/"
FILENAME="event_cache.json"
REMOTE_SCRIPT="kindle_script.sh"
# ---------------------------

UPDATE_INTERVAL="10m"
HASH=""
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

scp -o ControlPath="$CTRL_PATH" "$USER@$HOST:$DEST_DIR/$FILENAME" "$FILENAME"
scp -o ControlPath="$CTRL_PATH" "$REMOTE_SCRIPT" "$USER@$HOST:$DEST_DIR/"
rsync -rv -e "ssh -S $CTRL_PATH -o ControlMaster=no -o StrictHostKeyChecking=no" ./kcal "$USER@$HOST:/mnt/us/kcal/"
# shellcheck disable=SC2087
ssh -o StrictHostKeyChecking=no -o ControlPath="$CTRL_PATH" "$USER@$HOST" 'bash -s' <<EOF
if pgrep -f "$REMOTE_SCRIPT" > /dev/null; then
    pkill -f "$REMOTE_SCRIPT"
fi
cd "$DEST_DIR"
nohup bash "$REMOTE_SCRIPT" >> "render.log" 2>&1 &
EOF
ssh -o StrictHostKeyChecking=no -o ControlPath="$CTRL_PATH" "$USER@$HOST" "date -u -s @$(date -u +%s)"

while true; do
  python -m kcal calendar
  NEW_HASH=$(md5sum "$FILENAME" | awk '{print $1}')
  if [[ "$NEW_HASH" != "$HASH" ]]; then
    HASH="$NEW_HASH"
    echo Copying to kindle...
    scp -o ControlPath="$CTRL_PATH" "$FILENAME" "$USER@$HOST:$DEST_DIR/"
  fi

  sleep "$UPDATE_INTERVAL"
done
