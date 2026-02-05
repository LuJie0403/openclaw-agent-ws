# Kimi账单自动查询 - 安装配置指南

## 🎯 任务概述
**任务名称**: Kimi账单自动查询
**执行频率**: 每月3号自动执行
**主要功能**:
1. 查询Kimi API使用量
2. 统计本月使用数据
3. 通过Telegram发送报告给路杰

## 📋 前置要求

### 1. 系统要求
- Python 3.7+
- Linux/macOS系统（支持crontab）
- 网络连接（访问Kimi API和Telegram）

### 2. 必要的Python包
```bash
pip3 install requests
```

### 3. 获取API密钥

#### Kimi API密钥
1. 登录Kimi/Moonshot控制台
2. 进入API管理页面
3. 创建或获取API密钥
4. 复制密钥备用

#### Telegram Bot配置
1. 在Telegram中搜索 @BotFather
2. 创建新机器人: `/newbot`
3. 设置机器人名称和用户名
4. 获取机器人Token
5. 获取聊天ID:
   - 给机器人发送一条消息
   - 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - 从响应中获取chat.id

## 🔧 安装步骤

### 1. 克隆或下载脚本
确保所有文件在 `/home/lujie/.openclaw/workspace/` 目录下:
- `kimi_billing_checker.py` - 主要Python脚本
- `run_kimi_billing_check.sh` - 启动脚本
- `kimi_billing_checker.env.template` - 配置模板

### 2. 配置环境变量
```bash
# 复制配置模板
cp kimi_billing_checker.env.template .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中填入:
```
KIMI_API_KEY=your_actual_kimi_api_key_here
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here
```

### 3. 测试脚本
```bash
# 给脚本添加执行权限
chmod +x run_kimi_billing_check.sh

# 手动运行测试
./run_kimi_billing_check.sh
```

### 4. 设置定时任务
```bash
# 编辑crontab
crontab -e

# 添加以下行（每月3号上午9点执行）
0 9 3 * * /home/lujie/.openclaw/workspace/run_kimi_billing_check.sh >> /home/lujie/.openclaw/workspace/logs/kimi_billing_cron.log 2>&1
```

## 📊 报告格式

每月发送的Telegram消息格式:
```
📊 **Kimi API 2026年02月使用报告**

🔢 **基本统计**
• 总请求次数: 1,234
• 总Token消耗: 56,789
• 预估费用: 12.34 CNY

📈 **日均使用**
• 日均请求: 41 次
• 日均Token: 1,893

💡 **使用建议**
• 监控使用量趋势，合理规划API调用
• 如需更高额度，请联系服务提供商

📅 **报告生成时间**: 2026-02-03 09:00:00
```

## 🛠️ 故障排除

### 常见问题

#### 1. 脚本执行失败
```bash
# 查看详细日志
tail -f /home/lujie/.openclaw/workspace/logs/kimi_billing_cron.log

# 检查环境变量
cat .env
```

#### 2. Telegram消息未收到
- 检查机器人Token是否正确
- 确认chat_id是否有效
- 检查网络连接

#### 3. Kimi API连接失败
- 验证API密钥有效性
- 检查API endpoint是否正确
- 确认账户是否有足够权限

#### 4. Cron任务未执行
```bash
# 检查cron服务状态
systemctl status cron

# 查看cron日志
grep CRON /var/log/syslog

# 测试cron语法
crontab -l
```

### 手动测试API
```bash
# 测试Kimi API连接
curl -H "Authorization: Bearer YOUR_KIMI_API_KEY" \
     https://api.moonshot.cn/v1/models

# 测试Telegram Bot
curl https://api.telegram.org/botYOUR_BOT_TOKEN/getMe
```

## 🔒 安全建议

1. **保护API密钥**: 不要将 `.env` 文件上传到公共仓库
2. **定期轮换密钥**: 建议每3-6个月更换一次API密钥
3. **监控使用情况**: 定期检查API使用量，发现异常及时处理
4. **日志管理**: 定期清理旧的日志文件，避免占用过多磁盘空间

## 📈 监控和优化

### 添加更多监控指标
可以扩展脚本以包含:
- 响应时间统计
- 错误率监控
- 使用趋势分析
- 成本预测

### 设置告警
- 当使用量超过阈值时发送告警
- API连接失败时立即通知
- 月度费用异常增长提醒

## 📝 更新日志
- v1.0.0: 基础功能实现 - API使用量查询和Telegram报告

## 🤝 支持
如有问题，请检查日志文件或联系技术支持。