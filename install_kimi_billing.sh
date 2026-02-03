#!/bin/bash
"""
Kimi账单自动查询 - 快速安装脚本
一键安装和配置定时任务
"""

set -e  # 遇到错误立即退出

echo "🚀 Kimi账单自动查询 - 快速安装脚本"
echo "=================================="

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# 1. 检查Python环境
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3未安装"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: pip3未安装"
    exit 1
fi

echo "✅ Python环境检查通过"

# 2. 安装依赖
echo "📦 安装Python依赖..."
pip3 install requests
echo "✅ 依赖安装完成"

# 3. 检查必要文件
echo "📁 检查必要文件..."
required_files=("kimi_billing_checker.py" "run_kimi_billing_check.sh")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误: 缺少必要文件: $file"
        exit 1
    fi
done
echo "✅ 必要文件检查通过"

# 4. 给脚本添加执行权限
echo "🔐 设置脚本权限..."
chmod +x run_kimi_billing_check.sh
echo "✅ 权限设置完成"

# 5. 创建日志目录
echo "📝 创建日志目录..."
mkdir -p logs
echo "✅ 日志目录创建完成"

# 6. 配置检查
echo "⚙️  检查配置文件..."
if [ ! -f ".env" ]; then
    if [ -f "kimi_billing_checker.env.template" ]; then
        cp kimi_billing_checker.env.template .env
        echo "📝 已创建.env配置文件模板"
        echo "⚠️  请编辑 .env 文件填入实际的API密钥和配置信息"
    else
        echo "❌ 错误: 缺少配置文件模板"
        exit 1
    fi
else
    echo "✅ 配置文件已存在"
fi

# 7. 测试运行
echo "🧪 测试脚本运行..."
if python3 kimi_billing_checker.py; then
    echo "✅ 脚本测试通过"
else
    echo "❌ 脚本测试失败，请检查配置"
    exit 1
fi

echo ""
echo "🎉 快速安装完成！"
echo "==================="
echo ""
echo "📋 后续步骤:"
echo "1. 编辑 .env 文件，填入实际的API密钥和Telegram配置"
echo "2. 运行测试: ./run_kimi_billing_check.sh"
echo "3. 设置定时任务: crontab -e"
echo "4. 添加定时任务: 0 9 3 * * $SCRIPT_DIR/run_kimi_billing_check.sh >> $SCRIPT_DIR/logs/kimi_billing_cron.log 2>&1"
echo ""
echo "📖 详细说明请参考: KIMI_BILLING_SETUP_GUIDE.md"
echo "📝 日志文件位置: $SCRIPT_DIR/logs/"
echo ""

# 显示当前时间，方便用户设置合适的cron时间
echo "⏰ 当前系统时间: $(date)"
echo "🌍 建议设置cron时间为北京时间上午9点（UTC时间1点）"