#!/bin/bash
"""
Kimi账单自动查询 - 启动脚本
每月3号自动执行，查询API使用量并发送报告
"""

# 设置脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/kimi_billing_checker.py"
ENV_FILE="$SCRIPT_DIR/.env"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ 错误: Python脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi

# 检查环境变量文件
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 错误: 环境变量文件不存在: $ENV_FILE"
    echo "请复制 kimi_billing_checker.env.template 为 .env 并填入配置信息"
    exit 1
fi

# 加载环境变量
source "$ENV_FILE"

# 检查必要的配置
if [ -z "$KIMI_API_KEY" ] || [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ 错误: 缺少必要的环境变量配置"
    echo "请检查 .env 文件中的配置项"
    exit 1
fi

echo "🚀 启动Kimi账单自动查询任务..."
echo "📅 执行时间: $(date)"

# 执行Python脚本
cd "$SCRIPT_DIR"
python3 "$PYTHON_SCRIPT"

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "✅ Kimi账单查询任务执行成功"
else
    echo "❌ Kimi账单查询任务执行失败"
    exit 1
fi