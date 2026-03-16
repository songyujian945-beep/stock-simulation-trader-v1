# Git 快速配置指南

## 🚀 快速开始（3分钟完成）

### 第一步：配置GitHub CLI

```bash
# 1. 登录GitHub（会打开浏览器）
gh auth login

# 按提示选择：
# ✓ GitHub.com
# ✓ HTTPS
# ✓ Login with a web browser
# ✓ 输入显示的code
```

### 第二步：配置Git用户信息

```bash
# 替换成你的信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

### 第三步：验证配置

```bash
# 检查登录状态
gh auth status

# 检查Git配置
git config --global --list | grep user
```

---

## 📦 现在你可以让我做什么？

### ✅ 创建新项目

**你只需要说：**
> "帮我创建一个股票监控系统，用Python写"

**我会自动：**
1. 创建项目目录和文件
2. 初始化Git仓库
3. 创建规范的README
4. 首次提交
5. **询问你是否要推送到GitHub**

### ✅ 优化现有代码

**你只需要说：**
> "优化这个交易系统的性能"

**我会自动：**
1. 创建优化分支 `optimize/xxx`
2. 修改代码
3. 提交并注明优化内容
4. 合并到develop分支
5. 推送到GitHub

### ✅ 发布版本

**你只需要说：**
> "发布v1.1.0版本"

**我会自动：**
1. 合并develop到main
2. 创建版本标签
3. 推送到GitHub
4. 在GitHub创建Release

---

## 🎯 我会遵循的规范

### 项目命名
```
[类型]-[功能]-[版本]

示例：
- stock-simulation-trader-v1
- crypto-rsi-monitor
- video-auto-generator-v4
```

### 提交信息
```
feat(trading): 添加RSI指标监控
optimize(video-gen): 优化视频生成速度40%
fix(api): 修复连接超时问题
```

### 分支管理
```
main (生产环境)
  ↑
  └── develop (开发环境)
        ├── feature/xxx (新功能)
        ├── optimize/xxx (优化)
        └── hotfix/xxx (紧急修复)
```

---

## 🔧 常用命令（你可以直接让我执行）

| 你说... | 我会做什么 |
|---------|-----------|
| "创建xx系统" | 创建项目 + 初始化Git + 询问是否推送 |
| "优化这个功能" | 创建优化分支 + 提交 + 推送 |
| "查看xx项目状态" | 显示分支、提交、状态 |
| "发布v1.2.0" | 创建Release版本 |
| "同步到GitHub" | 推送所有变更 |

---

## 📋 示例：完整工作流

### 场景1：创建新项目

**你：** "创建一个股票监控系统"

**我：**
```
1. 创建项目 stock-simulation-monitor-v1
2. 初始化Git
3. 编写代码
4. 提交: "feat: 初始化股票监控系统"
5. 询问：是否推送到GitHub？
```

**你：** "推送"

**我：**
```
1. 创建GitHub仓库
2. 推送代码
3. 返回仓库地址: https://github.com/xxx/stock-simulation-monitor-v1
```

### 场景2：优化现有功能

**你：** "优化交易系统的性能"

**我：**
```
1. 创建分支: optimize/improve-performance
2. 修改代码（多线程、缓存等）
3. 提交: "optimize: 性能提升40%"
4. 合并到develop
5. 推送到GitHub
6. 显示: "✅ 优化已完成并推送"
```

### 场景3：发布版本

**你：** "发布v1.1.0版本"

**我：**
```
1. 合并develop到main
2. 创建标签: v1.1.0
3. 推送标签到GitHub
4. 创建GitHub Release
5. 返回: Release地址
```

---

## 🛠️ 辅助脚本

我已经为你创建了自动化脚本：

```bash
# 查看帮助
~/.openclaw/workspace/scripts/git_helper.sh

# 创建项目
~/.openclaw/workspace/scripts/git_helper.sh create my-project

# 关联GitHub
~/.openclaw/workspace/scripts/git_helper.sh link my-project

# 提交优化
~/.openclaw/workspace/scripts/git_helper.sh optimize my-project "优化说明"

# 发布版本
~/.openclaw/workspace/scripts/git_helper.sh release my-project v1.0.0

# 查看状态
~/.openclaw/workspace/scripts/git_helper.sh status my-project
```

---

## ⚠️ 注意事项

1. **敏感信息**：
   - ❌ 不要提交API Key、密码
   - ✅ 使用环境变量或config.json（已在.gitignore）

2. **提交前**：
   - 我会自动检查敏感文件
   - 使用.gitignore过滤

3. **版本标签**：
   - 遵循语义化版本（v1.0.0）
   - 只在稳定版本打标签

---

## 🎉 配置完成后

**你只需要告诉我：**
- 做什么系统
- 优化什么功能
- 发布什么版本

**剩下的全部由我自动完成！**

---

## 📞 需要帮助？

随时问我：
- "查看所有项目状态"
- "xx项目有什么更新？"
- "帮我整理一下Git提交"

---

_创建时间: 2026-03-16_
_快速开始指南 v1.0_
