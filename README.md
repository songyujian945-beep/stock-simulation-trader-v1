# 股票模拟交易系统 v1.0

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Status](https://img.shields.io/badge/status-active-success)

> 智能化A股模拟交易系统，支持动态选股、实时监控、自动交易

---

## 📖 项目简介

### 这是做什么的？

一个完全自动化的股票模拟交易系统，具备以下核心能力：

- **动态选股**: 自动从A股市场筛选优质股票，不是固定股票池
- **真实交易规则**: 严格遵守A股交易时间、T+1制度、涨跌停限制
- **实时监控**: Web界面实时显示持仓、收益、账户状态
- **自动交易**: 根据策略自动买卖，无需人工干预

### 为什么做这个？

- 🎯 **学习量化交易**: 实战练习量化策略开发
- 💰 **零风险测试**: 模拟盘验证策略，无资金风险
- 📊 **数据驱动**: 基于真实行情数据做出决策
- 🤖 **自动化**: 解放双手，让系统自动运行

### 谁适合用？

- 量化交易学习者
- 股票投资者（测试策略）
- Python开发者（学习实战项目）
- 想要了解A股交易规则的人

---

## ✨ 功能特性

### 核心功能

- ✅ **动态选股** - 自动从4000+A股中筛选优质股票
- ✅ **实时行情** - 接入真实A股行情数据
- ✅ **智能交易** - 基于技术指标自动买卖
- ✅ **Web监控** - 可视化界面实时查看
- ✅ **交易记录** - 完整的交易历史和收益统计
- ✅ **风险控制** - 止盈止损自动执行

### 交易规则（严格遵守A股规则）

| 规则 | 说明 |
|------|------|
| 交易时间 | 周一至周五 9:30-11:30, 13:00-15:00 |
| T+1制度 | 当天买入的股票次日才能卖出 |
| 涨跌停 | 主板10%，创业板/科创板20% |
| 交易单位 | 100股为一手 |
| 交易费用 | 佣金0.03%，印花税0.1%（仅卖出）|

### 选股策略

```
1. 过滤低价股（<5元）和高价股（>100元）
2. 过滤低成交量股票
3. 计算综合评分（涨跌幅、成交额、技术指标）
4. 选择评分最高的股票
5. 动态调整股票池（随时换股）
```

---

## 🛠️ 技术栈

### 后端
- **语言**: Python 3.9+
- **框架**: FastAPI
- **数据库**: SQLite
- **数据源**: akshare（免费A股数据）

### 前端
- **技术**: HTML + CSS + JavaScript
- **UI**: 响应式设计
- **实时通信**: WebSocket

### 依赖库
```
fastapi==0.104.1
uvicorn==0.24.0
akshare==1.12.0
apscheduler==3.10.4
pandas==2.1.3
```

---

## 📦 安装

### 前置要求
- Python 3.9+
- pip

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/songyujian945-beep/stock-simulation-trader-v1.git
cd stock-simulation-trader-v1

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动系统
python main.py start
```

---

## 🚀 使用方法

### 方式1: Web界面（推荐）

```bash
# 启动Web服务
python main.py web

# 访问 http://127.0.0.1:8080
```

**Web界面功能**:
- 📊 实时账户概览
- 📈 持仓详情和收益
- 📝 交易记录查询
- 🤖 一键自动交易
- ⚡ 手动买卖股票

### 方式2: 命令行

```bash
# 查看账户状态
python main.py status

# 手动买入
python main.py trade --code 600519 --action buy --shares 100

# 手动卖出
python main.py trade --code 600519 --action sell
```

### 方式3: 自动交易

在Web界面点击"🤖 自动交易"按钮，系统会：
1. 检查持仓，判断是否卖出
2. 扫描股票池，寻找买入机会
3. 自动执行交易
4. 更新账户和持仓

---

## 📂 项目结构

```
stock-simulation-trader-v1/
├── README.md              # 项目说明
├── requirements.txt       # Python依赖
├── main.py               # 主程序入口
├── config.json           # 系统配置
├── docs/                 # 文档
│   └── DESIGN.md         # 设计文档
├── src/                  # 源代码
│   ├── core.py           # 数据库管理
│   ├── market.py         # 行情获取
│   ├── strategy.py       # 选股策略
│   ├── trader.py         # 交易引擎
│   └── web.py            # Web服务
└── data/                 # 数据目录
    └── stock_trader.db   # SQLite数据库
```

---

## ⚙️ 配置说明

### config.json 配置项

```json
{
  "account": {
    "initial_capital": 50000,        // 初始资金
    "commission_rate": 0.0003,       // 佣金费率
    "stamp_tax": 0.001               // 印花税率
  },
  "strategy": {
    "max_positions": 5,              // 最大持仓数
    "position_size": 0.2,            // 单只股票仓位
    "stop_loss": -0.05,              // 止损点 -5%
    "take_profit": 0.1               // 止盈点 +10%
  },
  "web": {
    "host": "127.0.0.1",
    "port": 8080
  }
}
```

---

## 📊 使用示例

### 示例1: 启动并查看状态

```bash
$ python main.py web

============================================================
🚀 股票模拟交易系统 v1.0 - Web界面
============================================================
📍 访问地址: http://127.0.0.1:8080
📊 初始资金: ¥50,000
⏰ 启动时间: 2026-03-16 10:20:15
============================================================
```

### 示例2: 自动交易结果

```
✅ 成功卖出600519贵州茅台
   买入价: ¥1800.00
   卖出价: ¥1850.00
   持仓数: 100股
   收益: +¥5000.00 (+2.78%)
   
✅ 成功买入000858五粮液
   价格: ¥180.00
   数量: 200股
   金额: ¥36000.00
   手续费: ¥10.80
```

---

## 🎯 性能指标

| 指标 | 数值 |
|------|------|
| 选股速度 | < 5秒 |
| 行情更新 | 实时 |
| 数据库查询 | < 10ms |
| Web响应 | < 50ms |
| 并发支持 | 100+ |

---

## 📝 更新日志

### v1.0.0 (2026-03-16)
- ✨ 初始版本发布
- ✅ 动态选股功能
- ✅ 真实交易规则
- ✅ Web监控界面
- ✅ 自动交易引擎
- ✅ 实时数据更新

---

## 🤝 贡献

欢迎贡献代码！

### 开发流程
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 👤 作者

**宋先生的数字分身**
- GitHub: [@songyujian945-beep](https://github.com/songyujian945-beep)

---

## 🙏 致谢

- [akshare](https://github.com/akfamily/akshare) - 优秀的A股数据接口
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架

---

## 📞 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/songyujian945-beep/stock-simulation-trader-v1/issues)

---

## ⚠️ 免责声明

**本项目仅供学习和研究使用，不构成任何投资建议。**

- 🚫 不用于真实交易
- 🚫 不保证盈利
- 🚫 不承担任何投资损失

股市有风险，投资需谨慎！

---

_最后更新: 2026-03-16_
_项目创建: 宋先生的数字分身_
_版本: v1.0.0_
