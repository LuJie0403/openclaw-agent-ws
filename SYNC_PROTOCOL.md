# 工作同步机制 - GitHub优先原则

## 🔄 每日工作同步流程

### 工作开始前 (每日第一件事)
**⏰ 执行时间**: 每次新会话开始时
**📍 执行地点**: `/home/lujie/.openclaw/workspace`

```bash
# 1. 获取远程最新更新
git fetch origin master

# 2. 检查是否有远程更新
git log HEAD..origin/master --oneline

# 3. 如果有更新，先备份当前状态
git stash push -m "会话前自动备份 $(date)"

# 4. 合并远程更新
git merge origin/master --no-edit

# 5. 解决冲突（如果有）
git status

# 6. 验证更新成功
echo "✅ 工作空间已同步到最新版本"
```

### 工作结束后 (会话关闭前)
**⏰ 执行时间**: 会话结束前
**📍 执行地点**: `/home/lujie/.openclaw/workspace`

```bash
# 1. 检查本地变更
git status --porcelain

# 2. 添加所有变更
git add .

# 3. 提交变更
git commit -m "会话更新: $(date +%Y-%m-%d_%H:%M)"

# 4. 推送到远程
git push origin master

# 5. 验证推送成功
echo "✅ 本地变更已推送到GitHub"
```

## 🎯 同步检查清单

### 开始工作前检查
- [ ] 远程仓库是否有新提交？
- [ ] 本地是否有未提交的变更？
- [ ] 是否存在合并冲突？
- [ ] 同步后功能是否正常？

### 同步异常处理
1. **冲突解决**: 优先保留远程版本，本地变更备份
2. **网络异常**: 重试3次，失败后记录待处理
3. **权限问题**: 检查GitHub token有效性
4. **数据丢失**: 使用git reflog恢复历史版本

## 📋 同步状态记录

### 同步日志格式
```
[2026-02-05 19:10:00] 同步开始
[2026-02-05 19:10:02] 远程提交: 3个新提交
[2026-02-05 19:10:03] 本地状态: 2个未提交文件
[2026-02-05 19:10:05] 自动合并: 成功
[2026-02-05 19:10:06] 同步完成: ✅
```

### 同步失败处理
- **立即通知**: 同步失败时立即告知用户
- **备份策略**: 自动创建本地备份分支
- **手动模式**: 提供手动同步指令
- **状态追踪**: 记录所有同步操作历史

## ⚙️ 自动化脚本

### 工作开始同步脚本
```bash
#!/bin/bash
# sync-start-work.sh - 工作开始前同步

echo "🔄 开始同步GitHub工作空间..."
cd /home/lujie/.openclaw/workspace

# 获取远程更新
git fetch origin master

# 检查是否有远程更新
REMOTE_COMMITS=$(git rev-list HEAD..origin/master --count)
if [ $REMOTE_COMMITS -gt 0 ]; then
    echo "📥 检测到 $REMOTE_COMMITS 个远程更新"
    
    # 备份当前状态
    if [ -n "$(git status --porcelain)" ]; then
        echo "💾 备份当前未提交变更..."
        git stash push -m "同步前自动备份 $(date)"
    fi
    
    # 合并远程更新
    echo "🔄 合并远程更新..."
    git merge origin/master --no-edit
    
    # 恢复备份（如果有冲突需要手动处理）
    if git stash list | grep -q "同步前自动备份"; then
        echo "📝 恢复本地变更..."
        git stash pop || echo "⚠️  存在冲突，需要手动处理"
    fi
    
    echo "✅ 同步完成！"
else
    echo "✅ 工作空间已是最新版本"
fi

# 记录同步状态
echo "[$(date)] 工作空间同步完成" >> sync.log
```

### 工作结束同步脚本
```bash
#!/bin/bash
# sync-end-work.sh - 工作结束后同步

echo "☁️ 开始推送本地变更到GitHub..."
cd /home/lujie/.openclaw/workspace

# 检查是否有变更
if [ -n "$(git status --porcelain)" ]; then
    echo "📤 检测到本地变更，开始推送..."
    
    # 添加所有变更
    git add .
    
    # 提交变更
    git commit -m "工作会话更新: $(date +%Y-%m-%d_%H:%M)"
    
    # 推送到远程
    if git push origin master; then
        echo "✅ 本地变更已成功推送到GitHub"
    else
        echo "❌ 推送失败，请检查网络连接和权限"
        exit 1
    fi
else
    echo "✅ 本地无变更，无需推送"
fi

# 记录同步状态
echo "[$(date)] 本地变更推送完成" >> sync.log
```

## 🔄 同步频率设置

### 定时检查 (每小时)
- **目的**: 检查是否有远程更新
- **动作**: 仅通知，不自动合并
- **时间**: 每小时的第5分钟

### 工作开始同步 (会话开始时)
- **目的**: 确保工作空间是最新版本
- **动作**: 自动拉取和合并
- **触发**: 每次新会话建立时

### 工作结束同步 (会话结束时)
- **目的**: 保存所有本地变更
- **动作**: 自动提交和推送
- **触发**: 会话正常结束时

## 🚨 异常处理机制

### 网络异常
```bash
# 重试机制
for i in {1..3}; do
    if git push origin master; then
        echo "✅ 推送成功"
        break
    else
        echo "⚠️  第$i次推送失败，3秒后重试..."
        sleep 3
    fi
done
```

### 合并冲突
```bash
# 冲突解决策略
echo "⚠️  检测到合并冲突"
echo "🔍 冲突文件:"
git diff --name-only --diff-filter=U

# 优先保留远程版本
git checkout --theirs .
git add .
git commit -m "解决冲突：优先保留远程版本"

# 本地变更另存分支
git checkout -b local-changes-$(date +%Y%m%d_%H%M)
git stash pop || echo "需要手动处理冲突"
```

## 📊 同步统计

### 每日同步报告
```
📈 今日同步统计
├── 开始同步: 19次
├── 成功同步: 18次
├── 冲突解决: 1次
├── 推送失败: 0次
└── 平均耗时: 3.2秒
```

### 长期趋势
- **同步频率**: 每日2-5次
- **成功率**: > 95%
- **冲突率**: < 2%
- **平均延迟**: < 30秒

---

**🎯 核心原则**: GitHub优先，本地与云端始终保持同步
**⚡ 执行标准**: 零数据丢失，零冲突遗漏
**📈 优化目标**: 自动化率100%，手动干预<1%