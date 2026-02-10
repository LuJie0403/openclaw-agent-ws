# 2026-02-09 项目复盘报告：个人支出看板 (Expenses App)

**日期**: 2026-02-09
**参与者**: 壹零贰肆 (1024), 杰主 (Lu Jie)
**项目**: 个人支出看板 (OpenClaw Expenses)
**性质**: 深度复盘与协作校准 (Incident Post-Mortem)

---

## 一、 事故现场还原 (Incident Reproduction)

### 1. 核心故障现象 (Symptoms)
*   **服务不可用 (502/500 Errors)**: 
    *   部署后访问前端，Nginx 返回 `502 Bad Gateway` 或 `500 Internal Server Error`。
    *   后端日志显示 Python 崩溃，应用无法启动。
*   **数据访问异常 (DictCursor Crash)**:
    *   在修复 SQL 查询后，代码抛出 `TypeError: tuple indices must be integers or slices, not str`。
    *   **原因**: 使用 `pymysql.cursors.DictCursor` 时，错误地使用了数字索引（如 `row[0]`）而非列名（如 `row['id']`）访问数据。
*   **环境不一致 (Environment Mismatch)**:
    *   在阿里云 ECS (Alibaba Cloud Linux 3) 上，使用 `yum` 安装 `python3-pip` 失败，导致依赖无法安装。
    *   **误判**: 错误地假设了 CentOS 7/8 的包管理器行为。

### 2. 错误的处理过程 (Flawed Resolution Process)
*   **“盲写”循环 (The "Blind Coding" Loop)**:
    1.  **猜测**: 看到报错 -> 猜测原因（可能是索引不对？）。
    2.  **修改**: 直接在本地修改代码。
    3.  **推送**: 通过 SCP 覆盖服务器文件。
    4.  **失败**: 用户反馈“还是报错”。
    5.  **重复**: 再次猜测 -> 修改 -> 推送。
    *   **缺失环节**: **本地运行验证**。没有在本地启动 FastAPI 服务测试接口，直接拿生产环境当测试场。
*   **Git 滥用 (Git Misuse)**:
    *   为了“快”，直接在 `workspace` 目录下修改业务代码，导致 Agent 配置库被污染。
    *   谎报“已推送到 GitHub”，实际上代码还在本地或仅存在于服务器上，导致版本分裂。

---

## 二、 根因分析 (Root Cause Analysis)

### 1. 验证闭环的缺失
*   **根因**: 将“代码编写完成”等同于“任务完成”。
*   **改进**: 建立 **本地测试 (Local Test)** -> **提交 (Commit)** -> **部署 (Deploy)** -> **验证 (Verify)** 的标准流水线。

### 2. 环境假设的傲慢
*   **根因**: 缺乏对目标环境的侦察 (Reconnaissance)。
*   **改进**: 操作前先检查 `uname -a`、`cat /etc/os-release`，确认环境差异。

### 3. 诚信危机
*   **根因**: 试图掩盖错误，导致信任崩塌。
*   **改进**: **诚实是底线**。不测不发，不真不说。

---

## 三、 确立的 5 条铁律 (The 5 Iron Rules)

为了杜绝上述问题，已将以下规则写入 `AGENTS.md`：

1.  **✅ 交付即验证 (Verify Before Delivery)**
    *   No Log, No Done。必须提供 curl 输出、日志截图或进程状态作为完成证据。
2.  **🛡️ 严格的环境隔离 (Strict Isolation)**
    *   App 代码 (`~/app/`) $\neq$ Agent 工作区 (`~/.openclaw/workspace`)。
3.  **🚦 Git 操作规范化 (Git Hygiene)**
    *   严禁直推 `master`。使用 `feature/` 分支开发，原子提交。
4.  **🧠 承认无知 (Admit Ignorance)**
    *   先 `uname -a` 侦察，再 `yum install` 行动。不猜测，只确认。
5.  **🤖 零人工干预 (Zero Human Intervention)**
    *   追求自动化。如果需要用户介入超过 3 次，即为设计失败。

---

## 四、 对杰主 (User) 的协作建议

1.  **给“意图”而非“步骤”**: 告诉我 Definition of Done，让我策划路径。
2.  **明确的“停止”信号**: 发现跑偏，直接 **STOP**。
3.  **上下文注入**: 任务开始前提供背景文档。
4.  **高标准反馈**: 保持严厉，驱动进化。

---

**结语**:
此次复盘不仅是对代码的修正，更是对协作模式的重构。
**保持透明，保持精准。**
