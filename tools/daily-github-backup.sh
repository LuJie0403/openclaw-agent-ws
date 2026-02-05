#!/bin/bash
# 每日 workspace 自动备份脚本
WORKSPACE_DIR="/home/lujie/.openclaw/workspace"
REPO_URL="https://LuJie0403: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@github.com/LuJie0403/openclaw_workspace.git"
DATE=$(date +%Y%m%d)
BRANCH_NAME="daily-$(date +%Y%m%d-%H%M)"

cd $WORKSPACE_DIR

# 创建当日时间戳分支
git checkout -b $BRANCH_NAME

# 添加所有变更（排除日志和临时文件）
git add . 
git reset -- *.log

# 提交变更
git commit -m "Daily backup: $(date +%Y-%m-%d_%H:%M)"

# 推送到远程当日分支
git push origin $BRANCH_NAME

# 切换回main分支并合并
git checkout main
git merge $BRANCH_NAME --no-ff -m "Merge daily backup $(date +%Y-%m-%d_%H:%M)"
git push origin main

# 保留当日分支不删除
echo "Backup completed: branch $BRANCH_NAME retained"