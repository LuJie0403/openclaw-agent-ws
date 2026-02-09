#!/bin/bash
# 紧急备份检查器 - 防止数据丢失
WORKSPACE_DIR="/home/lujie/.openclaw/workspace"
BACKUP_INTERVAL=1800  # 30分钟
LAST_BACKUP_FILE="/tmp/last_workspace_backup"

cd $WORKSPACE_DIR

# 检查距离上次备份时间
if [[ -f $LAST_BACKUP_FILE ]]; then
    LAST_BACKUP=$(cat $LAST_BACKUP_FILE)
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_BACKUP))
    
    if [[ $TIME_DIFF -gt $BACKUP_INTERVAL ]]; then
        echo "WARNING: No backup for $(($TIME_DIFF/60)) minutes, forcing backup..."
        ./tools/daily-github-backup.sh
    fi
fi

# 检查重要文件变更
CRITICAL_FILES=("MEMORY.md" "IDENTITY.md" "USER.md" "SOUL.md")
for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$file" ]] && [[ $(git status --porcelain "$file") ]]; then
        echo "CRITICAL: $file changed, immediate backup required!"
        ./tools/daily-github-backup.sh
        break
    fi
done

# 记录当前时间
date +%s > $LAST_BACKUP_FILE