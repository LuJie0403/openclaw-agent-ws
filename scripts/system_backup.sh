#!/bin/bash
# Daily Backup: Branch -> Commit -> Push
WORKSPACE_DIR="/home/lujie/.openclaw/workspace"
LOG_FILE="$WORKSPACE_DIR/logs/cron_backup.log"
BRANCH_NAME="auto-backup/$(date +%Y%m%d-%H%M)"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] Starting Backup..." >> "$LOG_FILE"
cd "$WORKSPACE_DIR" || exit 1

# Check for changes
if [[ -z $(git status -s) ]]; then
    echo "[$(date)] No changes to backup." >> "$LOG_FILE"
    exit 0
fi

# Create branch and push
{
    git checkout -b "$BRANCH_NAME"
    git add .
    git commit -m "chore(auto): daily backup $(date +%Y-%m-%d)"
    git push origin "$BRANCH_NAME"
    
    echo "[$(date)] Backup Pushed: $BRANCH_NAME"
    
    # Return to master for next sync
    git checkout master
} >> "$LOG_FILE" 2>&1
