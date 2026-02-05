#!/bin/bash
# 智能 workspace 自动备份脚本 - 零丢失策略
WORKSPACE_DIR="/home/lujie/.openclaw/workspace"
REPO_URL="https://LuJie0403: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@github.com/LuJie0403/openclaw_workspace.git"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BRANCH_NAME="auto-$(date +%Y%m%d-%H%M)"

cd $WORKSPACE_DIR

# 检查是否有变更
if [[ -z $(git status --porcelain) ]]; then
    echo "$(date): No changes detected, skipping backup"
    exit 0
fi

# 创建自动备份分支
git checkout -b $BRANCH_NAME

# 智能添加变更（排除日志、临时文件、敏感信息）
git add . 
git reset -- *.log *.tmp *.cache

# 提交并推送
git commit -m "Auto backup: $(date +%Y-%m-%d_%H:%M:%S)"
git push origin $BRANCH_NAME

# 快速合并到master
git checkout master
git merge $BRANCH_NAME --no-ff -m "Merge auto backup $(date +%Y-%m-%d_%H:%M:%S)"
git push origin master

# 保留所有历史分支用于追溯
echo "$(date): Auto backup completed - branch $BRANCH_NAME retained"
echo "Changes backed up: $(git diff --stat HEAD~1)"