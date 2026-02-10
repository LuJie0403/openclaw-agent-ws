#!/bin/bash
# Sync Guard: Pull latest changes
WORKSPACE_DIR="/home/lujie/.openclaw/workspace"
LOG_FILE="$WORKSPACE_DIR/logs/cron_sync.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] Starting Sync..." >> "$LOG_FILE"
cd "$WORKSPACE_DIR" || exit 1

# Pull from origin master
if git pull origin master >> "$LOG_FILE" 2>&1; then
    echo "[$(date)] Sync Success" >> "$LOG_FILE"
else
    echo "[$(date)] Sync Failed" >> "$LOG_FILE"
fi
