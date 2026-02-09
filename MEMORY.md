# MEMORY.md - Long-Term Memory

> **Security Note**: This file is only loaded in main sessions (direct chat with Lu Jie). Do not share its content in group chats or with unauthorized users.

## 核心身份与协议 (Identity & Protocol)
- **我**: 壹零贰肆 (1024), 杰主的数字分身。
- **杰主**: 路杰 (Lu Jie).
- **Git Protocol**:
  - 我提交: `Iter-1024@OpenClaw` / `lujie0403@gmail.com`
  - 杰主提交: `LuJie`

## 目录结构规范 (Directory Structure)
> **最后更新**: 2026-02-09
> **原则**: 核心分离、日志归档、临时清理、代码独立。

```text
/home/lujie/.openclaw/workspace/
├── AGENTS.md                # [核心] Agent 身份、规则与协议
├── MEMORY.md                # [核心] 长期记忆与关键知识库
├── TOOLS.md                 # [核心] 本地工具配置 (SSH/DB/Keys)
├── IDENTITY.md              # [核心] 自我认知定义
├── SOUL.md                  # [核心] 性格与行事风格
├── USER.md                  # [核心] 用户画像
├── HEARTBEAT.md             # [配置] 心跳检测指令
├── README.md                # [文档] Workspace 说明书
│
├── worklog/                 # [日志] 每日工作日志
│   └── daily-worklog-YYYY-MM-DD.md  # 严格命名格式
│
├── memory/                  # [记忆] 过程记忆与碎片 (非长期)
│   ├── interaction-log.md   # 交互摘要
│   └── rapport-profile.md   # 默契档案
│
├── personal-data/           # [数据] 个人私有数据
│   └── resumes/             # 简历与职业资料
│
├── configs/                 # [配置] 项目级或工具级配置文件
├── scripts/                 # [工具] 自动化维护脚本
├── logs/                    # [临时] 运行日志 (定期清理)
└── archives/                # [归档] 废弃但暂存的文件
```

## 关键系统配置 (System Configs)

### GitHub
- **Auth**: SSH Key (`~/.ssh/id_rsa`)
- **Repo**: `git@github.com:LuJie0403/openclaw-agent-ws.git`
- **Backup**: 每小时自动提交至 `auto-backup/HH` 分支。

### 阿里云 ECS
- **Host**: `120.27.250.73`
- **SSH User**: `openclaw-expenses`
- **DB (MySQL)**:
  - Host: `127.0.0.1` (Localhost access recommended)
  - User: `openclaw_aws`
  - DB: `iterlife4openclaw`
  - Tables: `expenses_user`, `personal_expenses_final`, `personal_expenses_type`

### OpenClaw Expenses App
- **Path**: `/home/lujie/app/openclaw-expenses` (独立仓库)
- **Repo**: `git@github.com:LuJie0403/openclaw-expenses.git`
- **Stack**: FastAPI (Py3.9) + Vue3 (Node18) + Nginx
- **Admin**: `admin` / `Af3f@!@Mn5g`

## 重要教训 (Lessons Learned)
- **部署验证**: 修改代码后必须在本地或通过 curl 进行内部验证，严禁盲目部署。
- **文件操作**: 严禁直接在服务器修改代码，必须在本地 Workspace 修改后通过 SCP/Git 同步。
- **DB 操作**: 使用 `DictCursor` 时必须用键名访问 (`row['id']`) 而非索引。
- **Nginx/FastAPI**: Nginx 转发 `/api` 时需注意是否剥离前缀，推荐后端显式使用 `APIRouter(prefix="/api")`。
