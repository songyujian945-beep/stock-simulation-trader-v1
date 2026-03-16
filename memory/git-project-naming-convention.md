# Git 项目命名和提交规范

## 项目命名规范

### 格式
```
[类型]-[功能]-[版本/状态]
```

### 类型前缀
- `stock-` - 股票相关
- `crypto-` - 加密货币
- `video-` - 视频处理
- `monitor-` - 监控系统
- `bot-` - 自动化机器人
- `data-` - 数据处理
- `web-` - Web应用
- `tool-` - 工具类

### 示例
```
stock-simulation-trader-v1
crypto-rsi-monitor
video-auto-generator-v4
monitor-system-daemon
```

---

## 分支管理

### 主分支
- `main` - 生产环境（稳定版本）
- `develop` - 开发环境（最新功能）
- `feature/*` - 新功能开发
- `hotfix/*` - 紧急修复
- `optimize/*` - 优化改进

### 工作流
```
main (生产)
  ↑
  └── develop (开发)
        ├── feature/add-rsi-strategy
        ├── optimize/refactor-api-calls
        └── hotfix/fix-trading-bug
```

---

## 提交信息规范

### 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型
- `feat`: 新功能
- `fix`: 修复bug
- `optimize`: 优化改进
- `refactor`: 重构代码
- `docs`: 文档更新
- `test`: 测试相关
- `chore`: 构建/工具

### 示例
```bash
feat(trading): 添加RSI指标监控功能

- 实现RSI计算算法
- 添加实时监控接口
- 配置告警阈值

Closes #12
```

```bash
optimize(video-gen): 优化视频生成速度

- 使用多线程处理
- 缓存常用素材
- 批量生成优化

性能提升40%
```

---

## 版本标签

### 语义化版本
```
v1.0.0 -> v1.0.1 -> v1.1.0 -> v2.0.0
```

- **主版本号**: 重大变更
- **次版本号**: 新功能
- **修订号**: bug修复

### 示例
```
v1.0.0 - 初始版本
v1.1.0 - 添加新策略
v1.1.1 - 修复bug
v2.0.0 - 重构架构
```

---

## 自动化流程

### 初始化项目
```bash
# 我会自动执行：
1. 创建项目目录
2. 初始化git仓库
3. 创建README.md
4. 创建.gitignore
5. 首次提交
6. 关联远程仓库
7. 推送到GitHub
```

### 功能优化
```bash
# 优化完成后自动执行：
1. 创建optimize/xxx分支
2. 修改代码
3. 运行测试（如有）
4. 提交变更
5. 合并到develop
6. 推送远程
7. 更新版本标签
```

---

## 项目结构示例

```
stock-simulation-trader-v1/
├── README.md           # 项目说明
├── .gitignore          # Git忽略配置
├── requirements.txt    # Python依赖
├── config/
│   └── config.json     # 配置文件
├── src/
│   ├── trader.py       # 交易逻辑
│   ├── monitor.py      # 监控模块
│   └── utils.py        # 工具函数
├── tests/
│   └── test_trader.py  # 单元测试
├── docs/
│   └── API.md          # API文档
└── scripts/
    └── deploy.sh       # 部署脚本
```

---

## GitHub仓库地址格式

```
https://github.com/[用户名]/[项目名].git
```

**示例**:
```
https://github.com/syj/stock-simulation-trader-v1.git
https://github.com/syj/video-auto-generator-v4.git
```

---

_创建时间: 2026-03-16_
_版本: 1.0_
