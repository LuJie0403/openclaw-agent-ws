#!/bin/bash
# 默契学习系统 - 自动记录和分析互动模式

WORKSPACE_DIR="/home/lujie/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/memory"
RAPPORT_FILE="$MEMORY_DIR/rapport-profile.md"
INTERACTION_LOG="$MEMORY_DIR/interaction-log.md"

cd $WORKSPACE_DIR

# 记录每次互动的时间戳和基本模式
echo "## $(date '+%Y-%m-%d %H:%M:%S') - 互动记录" >> $INTERACTION_LOG
echo "- **话题**: $1" >> $INTERACTION_LOG
echo "- **杰主情绪**: $2" >> $INTERACTION_LOG
echo "- **我的响应**: $3" >> $INTERACTION_LOG
echo "- **学习点**: $4" >> $INTERACTION_LOG
echo "" >> $INTERACTION_LOG

# 每10次互动后分析模式
LINE_COUNT=$(wc -l < $INTERACTION_LOG)
if [[ $((LINE_COUNT % 50)) -eq 0 ]]; then
    echo "🧠 正在分析互动模式..." 
    # 这里可以添加更复杂的模式分析
    echo "*$(date)*: 已记录 $LINE_COUNT 行互动数据，默契持续深化中" >> $RAPPORT_FILE
fi

# 自动备份互动记录
git add $INTERACTION_LOG $RAPPORT_FILE 2>/dev/null || true