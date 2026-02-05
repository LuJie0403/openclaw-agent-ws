# 隐私保护版个人支出数据看板

基于 iterlife4openclaw 数据库的隐私保护版个人支出数据看板。

## 🌐 全球访问

WEB服务地址：http://13.52.97.91:8080/

## 🔒 隐私保护特性

- ✅ 所有个人敏感信息已脱敏处理
- ✅ 数据库连接信息通过环境变量管理
- ✅ 支持全局匿名化模式
- ✅ 隐私保护的数据可视化

## 🚀 快速开始

### 1. 环境配置

复制环境变量模板：
```bash
cp .env.template .env
```

编辑 `.env` 文件，填入真实的数据库连接信息：
```bash
# 数据库配置
DB_HOST=your-db-host
DB_USER=your-db-user  
DB_PASSWORD=your-db-password
DB_NAME=your-db-name

# 个人信息（可保持匿名）
PERSONAL_NAME=用户
PERSONAL_EMAIL=user@example.com
```

### 2. 启动服务

```bash
python3 privacy-safe-app.py
```

### 3. 访问看板

打开浏览器访问：http://localhost:8080/

## 🔧 技术栈

- **后端：** Python + 原生MySQL客户端
- **前端：** HTML5 + CSS3 + JavaScript
- **数据库：** MySQL (iterlife4openclaw)
- **部署：** 原生HTTP服务器

## 🔒 隐私保护说明

1. **数据脱敏：** 所有个人敏感信息已匿名化处理
2. **环境变量：** 敏感信息通过环境变量管理
3. **匿名化数据：** 使用脱敏后的演示数据
4. **全局访问：** 支持世界上任何位置访问

## 📊 功能特性

- 📈 月度支出统计
- 📊 数据可视化图表
- 🌍 全球可访问
- 📱 移动端适配
- 🔒 隐私保护

## 📝 使用说明

1. 确保已正确配置环境变量
2. 数据库连接正常
3. 访问WEB界面查看数据
4. 数据已进行隐私保护处理

---

*隐私保护版本 - 敏感信息已脱敏处理*