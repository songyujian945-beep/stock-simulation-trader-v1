#!/usr/bin/env python3
"""
股票模拟交易系统 - Web服务
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from datetime import datetime
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trader import StockTrader

app = FastAPI(title="股票模拟交易系统")

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
    return result

@app.post("/api/sell/{code}")
async def sell_stock(code: str, shares: int = None):
    """卖出股票"""
    if not trader:
        init_trader()
    
    result = trader.sell_stock(code, shares)
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

# ========== HTML界面 ==========

def generate_html():
    """生成HTML页面"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票模拟交易系统 v1.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .card h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }

        /* 账户概览 */
        .account-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .account-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .account-item .label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 8px;
        }

        .account-item .value {
            font-size: 24px;
            font-weight: bold;
        }

        .profit {
            color: #10b981;
        }

        .loss {
            color: #ef4444;
        }

        /* 持仓表格 */
        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }

        tr:hover {
            background: #f9fafb;
        }

        /* 按钮 */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-danger {
            background: #ef4444;
            color: white;
        }

        .btn-success {
            background: #10b981;
            color: white;
        }

        /* 状态指示 */
        .status {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-trading {
            background: #d1fae5;
            color: #065f46;
        }

        .status-closed {
            background: #fee2e2;
            color: #991b1b;
        }

        /* 实时更新 */
        .update-time {
            color: #6b7280;
            font-size: 12px;
            margin-top: 10px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #6b7280;
        }

        /* 响应式 */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }

            .account-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 股票模拟交易系统 v1.0</h1>

        <!-- 交易状态 -->
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2>交易状态</h2>
                <div>
                    <span id="trading-status" class="status">加载中...</span>
                    <button class="btn btn-primary" onclick="autoTrade()">🤖 自动交易</button>
                </div>
            </div>
        </div>

        <!-- 账户概览 -->
        <div class="card">
            <h2>💰 账户概览</h2>
            <div class="account-grid" id="account-grid">
                <div class="loading">加载中...</div>
            </div>
            <p class="update-time" id="update-time"></p>
        </div>

        <!-- 持仓列表 -->
        <div class="card">
            <h2>📊 当前持仓 (<span id="position-count">0</span>只)</h2>
            <table id="positions-table">
                <thead>
                    <tr>
                        <th>股票代码</th>
                        <th>股票名称</th>
                        <th>买入价</th>
                        <th>现价</th>
                        <th>持仓数</th>
                        <th>市值</th>
                        <th>收益</th>
                        <th>收益率</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="positions-body">
                    <tr>
                        <td colspan="9" class="loading">加载中...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 交易记录 -->
        <div class="card">
            <h2>📝 最近交易</h2>
            <table id="transactions-table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>股票</th>
                        <th>类型</th>
                        <th>价格</th>
                        <th>数量</th>
                        <th>金额</th>
                        <th>手续费</th>
                        <th>原因</th>
                    </tr>
                </thead>
                <tbody id="transactions-body">
                    <tr>
                        <td colspan="8" class="loading">加载中...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let ws;

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadAccount();
            loadPositions();
            loadTransactions();
            loadTradingStatus();
            connectWebSocket();
        });

        // 连接WebSocket
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'update') {
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
            const grid = document.getElementById('account-grid');
            const profitClass = account.total_profit >= 0 ? 'profit' : 'loss';

            grid.innerHTML = `
                <div class="account-item">
                    <div class="label">总资产</div>
                    <div class="value">¥${formatNumber(account.total_asset)}</div>
                </div>
                <div class="account-item">
                    <div class="label">可用资金</div>
                    <div class="value">¥${formatNumber(account.available_cash)}</div>
                </div>
                <div class="account-item">
                    <div class="label">持仓市值</div>
                    <div class="value">¥${formatNumber(account.market_value)}</div>
                </div>
                <div class="account-item">
                    <div class="label">总收益</div>
                    <div class="value ${profitClass}">¥${formatNumber(account.total_profit)}</div>
                </div>
                <div class="account-item">
                    <div class="label">收益率</div>
                    <div class="value ${profitClass}">${account.total_profit_rate.toFixed(2)}%</div>
                </div>
                <div class="account-item">
                    <div class="label">初始资金</div>
                    <div class="value">¥${formatNumber(account.initial_capital)}</div>
                </div>
            `;

            document.getElementById('update-time').textContent = 
                `最后更新: ${new Date().toLocaleString('zh-CN')}`;
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
                tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#6b7280;">暂无持仓</td></tr>';
                return;
            }

            tbody.innerHTML = positions.map(p => {
                const profitClass = p.profit >= 0 ? 'profit' : 'loss';
                return `
                    <tr>
                        <td>${p.code}</td>
                        <td><strong>${p.name}</strong></td>
                        <td>¥${p.buy_price.toFixed(2)}</td>
                        <td>¥${(p.current_price || p.buy_price).toFixed(2)}</td>
                        <td>${p.shares}股</td>
                        <td>¥${formatNumber(p.market_value || p.shares * p.buy_price)}</td>
                        <td class="${profitClass}">¥${formatNumber(p.profit)}</td>
                        <td class="${profitClass}">${p.profit_rate.toFixed(2)}%</td>
                        <td>
                            <button class="btn btn-danger" onclick="sellStock('${p.code}')">卖出</button>
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
            const tbody = document.getElementById('transactions-body');

            if (transactions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#6b7280;">暂无交易记录</td></tr>';
                return;
            }

            tbody.innerHTML = transactions.map(t => {
                const typeClass = t.type === 'buy' ? 'status-closed' : 'status-trading';
                const typeText = t.type === 'buy' ? '买入' : '卖出';
                return `
                    <tr>
                        <td>${new Date(t.timestamp).toLocaleString('zh-CN')}</td>
                        <td><strong>${t.name}</strong> (${t.code})</td>
                        <td><span class="status ${typeClass}">${typeText}</span></td>
                        <td>¥${t.price.toFixed(2)}</td>
                        <td>${t.shares}股</td>
                        <td>¥${formatNumber(t.amount)}</td>
                        <td>¥${t.fee.toFixed(2)}</td>
                        <td>${t.reason || '-'}</td>
                    </tr>
                `;
            }).join('');
        }

        // 加载交易状态
        async function loadTradingStatus() {
            try {
                const res = await fetch('/api/trading-status');
                const json = await res.json();
                if (json.success) {
                    const status = document.getElementById('trading-status');
                    if (json.data.is_trading) {
                        status.className = 'status status-trading';
                        status.textContent = '🟢 交易中 - ' + json.data.message;
                    } else {
                        status.className = 'status status-closed';
                        status.textContent = '🔴 休市 - ' + json.data.message;
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
            return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        }

        // 定时刷新
        setInterval(() => {
            loadAccount();
            loadPositions();
            loadTradingStatus();
        }, 30000); // 30秒刷新一次
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

    print(f"🚀 股票模拟交易系统启动")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"📊 初始资金: ¥50,000")

    uvicorn.run(app, host=host, port=port)
