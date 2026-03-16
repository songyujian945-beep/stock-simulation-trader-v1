# 股票模拟交易系统 v1.0 - 设计文档

## 项目概述
- **名称**: stock-simulation-trader-v1
- **版本**: v1.0.0
- **初始资金**: ¥50,000
- **类型**: 模拟交易 + 实时监控

## 核心功能

### 1. 动态选股策略
- 使用实时行情数据
- 技术指标筛选（RSI、MACD、成交量）
- 板块轮动策略
- 自动调整股票池

### 2. 真实交易规则
- 开市时间：周一至周五 9:30-11:30, 13:00-15:00
- T+1 交易制度
- 涨跌停限制（10%/20%）
- 交易费用（佣金、印花税）
- 最小交易单位（100股）

### 3. 实时监控
- 买入价格
- 当前价格（实时）
- 涨跌幅
- 持仓收益
- 总资产
- 可用资金
- 持仓明细
- 交易记录

## 技术架构

### 后端
- Python 3.11+
- FastAPI (Web框架)
- akshare (行情数据)
- SQLite (数据库)
- APScheduler (定时任务)

### 前端
- HTML + CSS + JavaScript
- ECharts (图表)
- Bootstrap (UI)

### 数据库设计

#### 表: stocks_pool (股票池)
- id
- code (股票代码)
- name (股票名称)
- industry (行业)
- added_at (加入时间)
- status (active/inactive)

#### 表: positions (持仓)
- id
- code
- name
- buy_price
- current_price
- shares
- buy_time
- profit (收益)
- profit_rate (收益率)

#### 表: transactions (交易记录)
- id
- code
- type (buy/sell)
- price
- shares
- amount
- fee
- timestamp

#### 表: account (账户)
- id
- total_asset (总资产)
- available_cash (可用资金)
- market_value (市值)
- total_profit (总收益)
- updated_at

## 版本规划

### v1.0.0 (当前)
- 基础框架
- 动态选股
- 实时监控
- Web界面

### v1.1.0 (计划)
- 多策略支持
- 回测功能
- 风险控制

### v1.2.0 (计划)
- 机器学习选股
- 自动化程度更高

---
创建时间: 2026-03-16
