#!/bin/bash
# Kimi API使用量追踪脚本
# 作者：路杰的数字化身

# 获取当前时间（北京时间）
CURRENT_TIME=$(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S')
CURRENT_DATE=$(TZ='Asia/Shanghai' date '+%Y-%m-%d')
CURRENT_MONTH=$(TZ='Asia/Shanghai' date '+%Y-%m')

# 配置文件
USAGE_FILE="/home/lujie/.openclaw/workspace/kimi-usage-${CURRENT_MONTH}.md"
SESSION_STATS_FILE="/home/lujie/.openclaw/agents/main/sessions/session-stats.json"

# 函数：初始化月度使用记录
init_monthly_usage() {
    if [ ! -f "$USAGE_FILE" ]; then
        cat > "$USAGE_FILE" << EOF
# Kimi API使用记录
# 用户：路杰
# 创建时间：${CURRENT_TIME}
# 月份：${CURRENT_MONTH}

## 使用统计
- 本月输入Token：0
- 本月输出Token：0
- 总调用次数：0
- 常用模型：无

## 详细记录
| 日期 | 时间 | 模型 | 输入Token | 输出Token | 用途 |
|------|------|------|-----------|-----------|------|

## 费用估算
- 输入费用：¥0.00
- 输出费用：¥0.00
- 总计：¥0.00

---
*最后更新：${CURRENT_TIME}*
EOF
        echo "✅ 创建新的月度使用记录：$USAGE_FILE"
    fi
}

# 函数：记录API调用
record_api_usage() {
    local model="$1"
    local input_tokens="$2"
    local output_tokens="$3"
    local purpose="$4"
    
    # 确保月度记录文件存在
    init_monthly_usage
    
    # 添加到详细记录表格
    sed -i "/^|------|------|------|-----------|-----------|------|/a | ${CURRENT_DATE} | ${CURRENT_TIME:11:5} | ${model} | ${input_tokens} | ${output_tokens} | ${purpose} |" "$USAGE_FILE"
    
    echo "✅ 记录API调用：${model} - 输入：${input_tokens} tokens，输出：${output_tokens} tokens"
}

# 函数：更新月度统计
update_monthly_stats() {
    local usage_file="$1"
    
    # 统计本月数据
    local total_input=$(grep -E "^\| [0-9-]+ \| [0-9:]+ \|" "$usage_file" | awk -F'|' '{sum += $5} END {print sum+0}')
    local total_output=$(grep -E "^\| [0-9-]+ \| [0-9:]+ \|" "$usage_file" | awk -F'|' '{sum += $6} END {print sum+0}')
    local total_calls=$(grep -E "^\| [0-9-]+ \| [0-9:]+ \|" "$usage_file" | wc -l)
    local popular_model=$(grep -E "^\| [0-9-]+ \| [0-9:]+ \|" "$usage_file" | awk -F'|' '{print $4}' | sed 's/^ *//;s/ *$//' | sort | uniq -c | sort -nr | head -1 | awk '{print $2}')
    
    # 更新统计信息
    sed -i "s/- 本月输入Token：[0-9,]*/- 本月输入Token：${total_input}/" "$usage_file"
    sed -i "s/- 本月输出Token：[0-9,]*/- 本月输出Token：${total_output}/" "$usage_file"
    sed -i "s/- 总调用次数：[0-9]*/- 总调用次数：${total_calls}/" "$usage_file"
    sed -i "s/- 常用模型：.*/- 常用模型：${popular_model}/" "$usage_file"
    sed -i "s/*最后更新：.*/*最后更新：${CURRENT_TIME}*/" "$usage_file"
    
    echo "📊 月度统计已更新：输入${total_input} tokens，输出${total_output} tokens，共${total_calls}次调用"
}

# 函数：生成月度账单报告
generate_monthly_report() {
    local month="$1"
    local usage_file="/home/lujie/.openclaw/workspace/kimi-usage-${month}.md"
    local report_file="/home/lujie/.openclaw/workspace/kimi-bill-${month}.md"
    
    if [ ! -f "$usage_file" ]; then
        echo "❌ 未找到${month}的使用记录"
        return 1
    fi
    
    # 读取统计数据
    local input_tokens=$(grep "本月输入Token：" "$usage_file" | awk -F'：' '{print $2}')
    local output_tokens=$(grep "本月输出Token：" "$usage_file" | awk -F'：' '{print $2}')
    local total_calls=$(grep "总调用次数：" "$usage_file" | awk -F'：' '{print $2}')
    local popular_model=$(grep "常用模型：" "$usage_file" | awk -F'：' '{print $2}')
    
    # 费用计算（需要官方定价）
    local input_cost="0.00"
    local output_cost="0.00"
    local total_cost="0.00"
    
    cat > "$report_file" << EOF
# 🧾 Kimi API 月度账单报告
# 月份：${month}
# 生成时间：${CURRENT_TIME}
# 用户：路杰

## 📊 使用概览
- **账单月份：** ${month}
- **总调用次数：** ${total_calls} 次
- **输入Token：** ${input_tokens} tokens
- **输出Token：** ${output_tokens} tokens
- **常用模型：** ${popular_model}

## 💰 费用明细
- **输入费用：** ¥${input_cost} (${input_tokens} tokens)
- **输出费用：** ¥${output_cost} (${output_tokens} tokens)
- **总计：** ¥${total_cost}

## 📈 使用详情
详见使用记录：\`kimi-usage-${month}.md\`

## 🔔 下月提醒
将在下个月账单日自动发送新的使用报告。

---
*报告生成时间：${CURRENT_TIME}*
*你的数字化身 敬上*
EOF
    
    echo "✅ 月度账单报告已生成：$report_file"
    return 0
}

# 主函数
main() {
    case "$1" in
        "init")
            init_monthly_usage
            ;;
        "record")
            record_api_usage "$2" "$3" "$4" "$5"
            update_monthly_stats "$USAGE_FILE"
            ;;
        "report")
            generate_monthly_report "$2"
            ;;
        "test")
            echo "🧪 测试Kimi账单系统..."
            init_monthly_usage
            record_api_usage "kimi-k2-0905-preview" "38000" "99" "账单功能测试"
            generate_monthly_report "$CURRENT_MONTH"
            echo "✅ 测试完成！"
            ;;
        *)
            echo "使用方法："
            echo "  $0 init                    - 初始化月度记录"
            echo "  $0 record <模型> <输入tokens> <输出tokens> <用途> - 记录API调用"
            echo "  $0 report <年月>           - 生成月度报告"
            echo "  $0 test                    - 测试系统"
            ;;
    esac
}

# 执行主函数
main "$@"
EOF

chmod +x /home/lujie/.openclaw/workspace/kimi-billing-tracker.sh

echo "✅ Kimi账单追踪脚本已创建！"
echo "📍 位置：/home/lujie/.openclaw/workspace/kimi-billing-tracker.sh"
echo "🧪 运行测试：bash /home/lujie/.openclaw/workspace/kimi-billing-tracker.sh test"