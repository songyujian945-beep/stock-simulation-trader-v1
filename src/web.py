"""
股票模拟交易系统 - Web服务 (优化版)
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import asyncio
from datetime import datetime
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trader import StockTrader

app = FastAPI(title="股票模拟交易系统 v1.1")

# 全局变量
trader = None
websocket_clients = []

def init_trader():
    """初始化交易引擎"""
    global trader
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path) as f:
        config = json.load(f)
    trader = StockTrader(config)

# ========== Web界面 ==========

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """主页面"""
    return generate_html()

# ========== API接口 ==========

@app.get("/api/account")
async def get_account():
    """获取账户信息"""
    if not trader:
        init_trader()
    
    overview = trader.get_account_overview()
    return {
        "success": True,
        "data": overview['account']
    }

@app.get("/api/positions")
async def get_positions():
    """获取持仓列表"""
    if not trader:
        init_trader()
    
    overview = trader.get_account_overview()
    return {
        "success": True,
        "data": overview['positions']
    }

@app.get("/api/transactions")
async def get_transactions(limit: int = 20):
    """获取交易记录"""
    if not trader:
        init_trader()
    
    transactions = trader.db.get_transactions(limit)
    return {
        "success": True,
        "data": transactions
    }

@app.post("/api/buy/{code}")
async def buy_stock(code: str, shares: int = None):
    """买入股票"""
    if not trader:
        init_trader()
    
    result = trader.buy_stock(code, shares)
    
    # 通知WebSocket客户端
    if result['success']:
        await broadcast_update()
    
    return result

@app.post("/api/sell/{code}")
async def sell_stock(code: str, shares: int = None):
    """卖出股票"""
    if not trader:
        init_trader()
    
    result = trader.sell_stock(code, shares)
    
    # 通知WebSocket客户端
    if result['success']:
        await broadcast_update()
    
    return result

@app.post("/api/auto-trade")
async def auto_trade():
    """执行自动交易"""
    if not trader:
        init_trader()
    
    result = trader.auto_trade()
    
    # 通知WebSocket客户端
    if result['success']:
        await broadcast_update()
    
    return result

@app.get("/api/overview")
async def get_overview():
    """获取账户概览"""
    if not trader:
        init_trader()
    
    overview = trader.get_account_overview()
    return {
        "success": True,
        "data": overview
    }

@app.get("/api/trading-status")
async def get_trading_status():
    """获取交易状态"""
    if not trader:
        init_trader()
    
    is_trading, msg = trader.is_trading_time()
    return {
        "success": True,
        "data": {
            "is_trading": is_trading,
            "message": msg,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

# ========== WebSocket实时推送 ==========

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接"""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        # 发送初始数据
        if trader:
            overview = trader.get_account_overview()
            await websocket.send_json({
                "type": "init",
                "data": overview
            })
        
        # 保持连接
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except Exception as e:
        print(f"WebSocket断开: {e}")
    finally:
        websocket_clients.remove(websocket)

async def broadcast_update():
    """广播更新到所有WebSocket客户端"""
    if trader:
        overview = trader.get_account_overview()
        message = {
            "type": "update",
            "data": overview,
            "timestamp": datetime.now().isoformat()
        }
        
        for client in websocket_clients:
            try:
                await client.send_json(message)
            except:
                pass

# ========== HTML界面 (优化版) ==========

def generate_html():
    """生成HTML页面 - 专业金融UI设计"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票模拟交易系统 v1.1 - 专业版</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --success: #ef4444;  /* 改为红色（中国股市：涨=红）*/
            --danger: #10b981;   /* 改为绿色（中国股市：跌=绿）*/
            --warning: #f59e0b;
            --info: #3b82f6;
            --bg-main: #f3f4f6;
            --bg-card: #ffffff;
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg-main);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 30px 20px;
            box-shadow: var(--shadow-lg);
        }

        .header-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .header h1 {
            font-size: 2em;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header-info {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-badge.trading {
            background: rgba(16, 185, 129, 0.2);
            border: 2px solid #10b981;
        }

        .status-badge.closed {
            background: rgba(239, 68, 68, 0.2);
            border: 2px solid #ef4444;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border-color);
        }

        .card-title {
            font-size: 1.3em;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* 账户概览网格 */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }

        .metric-card {
            background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
            transition: all 0.3s;
        }

        .metric-card:hover {
            transform: scale(1.02);
        }

        .metric-card.profit {
            border-left-color: var(--success);
            background: linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%);
        }

        .metric-card.loss {
            border-left-color: var(--danger);
            background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
        }

        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .metric-value {
            font-size: 2em;
            font-weight: 700;
            color: var(--text-primary);
            font-family: 'Courier New', monospace;
        }

        .metric-value.positive {
            color: var(--success);
        }

        .metric-value.negative {
            color: var(--danger);
        }

        /* 持仓表格 */
        .positions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .positions-table th,
        .positions-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .positions-table th {
            background: #f9fafb;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }

        .positions-table tbody tr {
            transition: background 0.2s;
        }

        .positions-table tbody tr:hover {
            background: #f9fafb;
        }

        .stock-code {
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: var(--primary);
        }

        .stock-name {
            font-weight: 600;
            color: var(--text-primary);
        }

        .price {
            font-family: 'Courier New', monospace;
            font-weight: 600;
        }

        .change {
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.9em;
        }

        .change.up {
            background: #ecfdf5;
            color: var(--success);
        }

        .change.down {
            background: #fef2f2;
            color: var(--danger);
        }

        /* 按钮 */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow);
        }

        .btn-primary {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
        }

        .btn-primary:hover {
            background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        }

        .btn-success {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            color: white;
        }

        .btn-danger {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
        }

        .btn-sm {
            padding: 6px 12px;
            font-size: 0.85em;
        }

        /* 图表容器 */
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }

        /* 更新时间 */
        .update-time {
            color: var(--text-secondary);
            font-size: 0.85em;
            text-align: center;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border-color);
        }

        /* 动画 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        /* 响应式 */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.5em;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }

            .positions-table {
                font-size: 0.9em;
            }

            .positions-table th,
            .positions-table td {
                padding: 10px;
            }
        }

        /* 空状态 */
        .empty-state {
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }

        .empty-state svg {
            width: 64px;
            height: 64px;
            margin-bottom: 15px;
            opacity: 0.3;
        }

        /* 交易记录时间线 */
        .transaction-item {
            padding: 15px;
            border-left: 3px solid var(--border-color);
            margin-bottom: 10px;
            background: #f9fafb;
            border-radius: 0 8px 8px 0;
        }

        .transaction-item.buy {
            border-left-color: var(--success);
        }

        .transaction-item.sell {
            border-left-color: var(--danger);
        }

        .transaction-time {
            color: var(--text-secondary);
            font-size: 0.85em;
            margin-bottom: 5px;
        }

        .transaction-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .transaction-stock {
            font-weight: 600;
        }

        .transaction-amount {
            font-family: 'Courier New', monospace;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <!-- 头部 -->
    <div class="header">
        <div class="header-content">
            <h1>📈 股票模拟交易系统 v1.1</h1>
            <div class="header-info">
                <div id="trading-status" class="status-badge closed">
                    <span>⏳</span>
                    <span>加载中...</span>
                </div>
                <button class="btn btn-primary" onclick="autoTrade()">
                    <span>🤖</span>
                    <span>自动交易</span>
                </button>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- 账户概览 -->
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-title">
                    <span>💰</span>
                    <span>账户概览</span>
                </div>
            </div>
            <div class="metrics-grid" id="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">总资产</div>
                    <div class="metric-value" id="total-asset">¥0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">可用资金</div>
                    <div class="metric-value" id="available-cash">¥0.00</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">持仓市值</div>
                    <div class="metric-value" id="market-value">¥0.00</div>
                </div>
                <div class="metric-card" id="profit-card">
                    <div class="metric-label">总收益</div>
                    <div class="metric-value" id="total-profit">¥0.00</div>
                </div>
                <div class="metric-card" id="profit-rate-card">
                    <div class="metric-label">收益率</div>
                    <div class="metric-value" id="profit-rate">0.00%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">初始资金</div>
                    <div class="metric-value" id="initial-capital">¥50,000</div>
                </div>
            </div>
            <div class="update-time" id="update-time">
                最后更新: --
            </div>
        </div>

        <!-- 持仓列表 -->
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-title">
                    <span>📊</span>
                    <span>当前持仓 (<span id="position-count">0</span>只)</span>
                </div>
            </div>
            <div id="positions-container">
                <table class="positions-table">
                    <thead>
                        <tr>
                            <th>股票代码</th>
                            <th>股票名称</th>
                            <th>买入价</th>
                            <th>现价</th>
                            <th>持仓</th>
                            <th>市值</th>
                            <th>收益</th>
                            <th>收益率</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="positions-body">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 收益图表 -->
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-title">
                    <span>📈</span>
                    <span>收益曲线</span>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="profit-chart"></canvas>
            </div>
        </div>

        <!-- 最近交易 -->
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-title">
                    <span>📝</span>
                    <span>最近交易</span>
                </div>
            </div>
            <div id="transactions-container">
            </div>
        </div>
    </div>

    <script>
        let ws;
        let profitChart;

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadAccount();
            loadPositions();
            loadTransactions();
            loadTradingStatus();
            connectWebSocket();
            initChart();
        });

        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('profit-chart').getContext('2d');
            profitChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '总资产',
                        data: [],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '¥' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            display: false
                        }
                    }
                }
            });
        }

        // WebSocket连接
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'update' || data.type === 'init') {
                    updateDisplay(data.data);
                }
            };

            ws.onclose = function() {
                setTimeout(connectWebSocket, 3000);
            };
        }

        // 加载账户信息
        async function loadAccount() {
            try {
                const res = await fetch('/api/account');
                const json = await res.json();
                if (json.success) {
                    displayAccount(json.data);
                }
            } catch (e) {
                console.error('加载账户失败:', e);
            }
        }

        // 显示账户信息
        function displayAccount(account) {
            document.getElementById('total-asset').textContent = 
                '¥' + formatNumber(account.total_asset);
            document.getElementById('available-cash').textContent = 
                '¥' + formatNumber(account.available_cash);
            document.getElementById('market-value').textContent = 
                '¥' + formatNumber(account.market_value);
            document.getElementById('initial-capital').textContent = 
                '¥' + formatNumber(account.initial_capital);

            // 收益
            const profit = account.total_profit;
            const profitRate = account.total_profit_rate;
            const profitEl = document.getElementById('total-profit');
            const profitRateEl = document.getElementById('profit-rate');
            const profitCard = document.getElementById('profit-card');
            const profitRateCard = document.getElementById('profit-rate-card');

            profitEl.textContent = (profit >= 0 ? '+' : '') + '¥' + formatNumber(profit);
            profitRateEl.textContent = (profitRate >= 0 ? '+' : '') + profitRate.toFixed(2) + '%';

            if (profit >= 0) {
                profitEl.className = 'metric-value positive';
                profitRateEl.className = 'metric-value positive';
                profitCard.className = 'metric-card profit';
                profitRateCard.className = 'metric-card profit';
            } else {
                profitEl.className = 'metric-value negative';
                profitRateEl.className = 'metric-value negative';
                profitCard.className = 'metric-card loss';
                profitRateCard.className = 'metric-card loss';
            }

            document.getElementById('update-time').textContent = 
                '最后更新: ' + new Date().toLocaleString('zh-CN');

            // 更新图表
            updateChart(account.total_asset);
        }

        // 更新图表
        function updateChart(value) {
            if (!profitChart) return;

            const now = new Date();
            const label = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');

            profitChart.data.labels.push(label);
            profitChart.data.datasets[0].data.push(value);

            // 保留最近20个点
            if (profitChart.data.labels.length > 20) {
                profitChart.data.labels.shift();
                profitChart.data.datasets[0].data.shift();
            }

            profitChart.update('none');
        }

        // 加载持仓
        async function loadPositions() {
            try {
                const res = await fetch('/api/positions');
                const json = await res.json();
                if (json.success) {
                    displayPositions(json.data);
                }
            } catch (e) {
                console.error('加载持仓失败:', e);
            }
        }

        // 显示持仓
        function displayPositions(positions) {
            const tbody = document.getElementById('positions-body');
            document.getElementById('position-count').textContent = positions.length;

            if (positions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9">
                            <div class="empty-state">
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14l-5-5 1.41-1.41L12 14.17l4.59-4.58L18 11l-6 6z"/>
                                </svg>
                                <div>暂无持仓</div>
                                <div style="font-size: 0.9em; margin-top: 5px;">点击"自动交易"开始</div>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = positions.map(p => {
                const currentPrice = p.current_price || p.buy_price;
                const profit = p.profit || 0;
                const profitRate = p.profit_rate || 0;
                const profitClass = profit >= 0 ? 'up' : 'down';

                return `
                    <tr class="fade-in">
                        <td><span class="stock-code">${p.code}</span></td>
                        <td><span class="stock-name">${p.name}</span></td>
                        <td class="price">¥${p.buy_price.toFixed(2)}</td>
                        <td class="price">¥${currentPrice.toFixed(2)}</td>
                        <td>${p.shares}股</td>
                        <td class="price">¥${formatNumber(p.market_value || p.shares * currentPrice)}</td>
                        <td class="change ${profitClass}">
                            ${profit >= 0 ? '+' : ''}¥${formatNumber(profit)}
                        </td>
                        <td class="change ${profitClass}">
                            ${profitRate >= 0 ? '+' : ''}${profitRate.toFixed(2)}%
                        </td>
                        <td>
                            <button class="btn btn-danger btn-sm" onclick="sellStock('${p.code}')">
                                卖出
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // 加载交易记录
        async function loadTransactions() {
            try {
                const res = await fetch('/api/transactions?limit=10');
                const json = await res.json();
                if (json.success) {
                    displayTransactions(json.data);
                }
            } catch (e) {
                console.error('加载交易记录失败:', e);
            }
        }

        // 显示交易记录
        function displayTransactions(transactions) {
            const container = document.getElementById('transactions-container');

            if (transactions.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                        </svg>
                        <div>暂无交易记录</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = transactions.map(t => {
                const typeClass = t.type === 'buy' ? 'buy' : 'sell';
                const typeText = t.type === 'buy' ? '买入' : '卖出';
                const typeIcon = t.type === 'buy' ? '📈' : '📉';

                return `
                    <div class="transaction-item ${typeClass} fade-in">
                        <div class="transaction-time">
                            ${new Date(t.timestamp).toLocaleString('zh-CN')}
                        </div>
                        <div class="transaction-details">
                            <div>
                                <span>${typeIcon}</span>
                                <span class="transaction-stock">${t.name} (${t.code})</span>
                                <span style="color: var(--text-secondary); margin-left: 10px;">
                                    ${typeText} ${t.shares}股 × ¥${t.price.toFixed(2)}
                                </span>
                            </div>
                            <div class="transaction-amount ${typeClass === 'buy' ? 'negative' : 'positive'}">
                                ${typeClass === 'buy' ? '-' : '+'}¥${formatNumber(t.amount)}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // 加载交易状态
        async function loadTradingStatus() {
            try {
                const res = await fetch('/api/trading-status');
                const json = await res.json();
                if (json.success) {
                    const statusBadge = document.getElementById('trading-status');
                    if (json.data.is_trading) {
                        statusBadge.className = 'status-badge trading';
                        statusBadge.innerHTML = `
                            <span>🟢</span>
                            <span>交易中</span>
                        `;
                    } else {
                        statusBadge.className = 'status-badge closed';
                        statusBadge.innerHTML = `
                            <span>🔴</span>
                            <span>休市</span>
                        `;
                    }
                }
            } catch (e) {
                console.error('加载交易状态失败:', e);
            }
        }

        // 自动交易
        async function autoTrade() {
            try {
                const res = await fetch('/api/auto-trade', { method: 'POST' });
                const json = await res.json();
                alert(JSON.stringify(json, null, 2));
                loadAccount();
                loadPositions();
                loadTransactions();
            } catch (e) {
                alert('自动交易失败: ' + e.message);
            }
        }

        // 卖出股票
        async function sellStock(code) {
            if (!confirm(`确定要卖出 ${code} 吗?`)) return;

            try {
                const res = await fetch(`/api/sell/${code}`, { method: 'POST' });
                const json = await res.json();
                alert(json.message);
                if (json.success) {
                    loadAccount();
                    loadPositions();
                    loadTransactions();
                }
            } catch (e) {
                alert('卖出失败: ' + e.message);
            }
        }

        // 更新显示
        function updateDisplay(data) {
            if (data.account) displayAccount(data.account);
            if (data.positions) displayPositions(data.positions);
            if (data.recent_transactions) displayTransactions(data.recent_transactions);
        }

        // 格式化数字
        function formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            return num.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',');
        }

        // 定时刷新
        setInterval(() => {
            loadAccount();
            loadPositions();
            loadTradingStatus();
        }, 30000);
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn

    # 初始化交易引擎
    init_trader()

    # 启动Web服务
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path) as f:
        config = json.load(f)

    web_config = config.get('web', {})
    host = web_config.get('host', '127.0.0.1')
    port = web_config.get('port', 8080)

    print(f"🚀 股票模拟交易系统 v1.1 启动")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"📊 初始资金: ¥50,000")

    uvicorn.run(app, host=host, port=port)
