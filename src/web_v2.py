"""
股票模拟交易系统 - Web服务 v2 - 按照正确的账算逻辑
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import asyncio
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trader_v2 import StockTraderV2

app = FastAPI(title="股票模拟交易系统 v2")

# 全局变量
trader = None
websocket_clients = []

def init_trader():
    """初始化交易引擎"""
    global trader
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path) as f:
        config = json.load(f)
    trader = StockTraderV2(config)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """主页面"""
    return generate_html()

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
    if result['success']:
        await broadcast_update()
    return result

@app.post("/api/sell/{code}")
async def sell_stock(code: str, shares: int = None):
    """卖出股票"""
    if not trader:
        init_trader()
    result = trader.sell_stock(code, shares)
    if result['success']:
        await broadcast_update()
    return result

@app.post("/api/auto-trade")
async def auto_trade():
    """执行自动交易"""
    if not trader:
        init_trader()
    result = trader.auto_trade()
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接"""
    await websocket.accept()
    websocket_clients.append(websocket)

    try:
        if trader:
            overview = trader.get_account_overview()
            await websocket.send_json({
                "type": "init",
                "data": overview
            })

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except Exception as e:
        print(f"WebSocket断开: {e}")
    finally:
        websocket_clients.remove(websocket)

async def broadcast_update():
    """广播更新"""
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

def generate_html():
    """生成HTML页面"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票模拟交易系统 v2</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #f5f5f5; padding: 20px; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .metric { background: #ecf0f1; padding: 15px; border-radius: 6px; }
        .metric-label { color: #7f8c8d; font-size: 14px; }
        .metric-value { font-size: 24px; font-weight: bold; margin-top: 10px; }
        .fee-display { font-size: 14px; color: #e74c3c; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #f8f9fa; }
        .profit { color: #27ae60; }
        .loss { color: #c0392b; }
        button { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        .btn-buy { background: #27ae60; color: white; }
        .btn-sell { background: #c0392b; color: white; }
        .btn-auto { background: #f39c12; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 股票模拟交易系统 v2</h1>
        <p>正确的账算逻辑</p>
    </div>

    <div class="grid">
        <div class="metric">
            <div class="metric-label">总资产</div>
            <div class="metric-value" id="total-asset">¥0.00</div>
        </div>
        <div class="metric">
            <div class="metric-label">可用现金</div>
            <div class="metric-value" id="available-cash">¥0.00</div>
        </div>
        <div class="metric">
            <div class="metric-label">持仓市值</div>
            <div class="metric-value" id="market-value">¥0.00</div>
        </div>
        <div class="metric">
            <div class="metric-label">总收益</div>
            <div class="metric-value" id="total-profit">¥0.00</div>
        </div>
        <div class="metric">
            <div class="metric-label">收益率</div>
            <div class="metric-value" id="profit-rate">0.00%</div>
        </div>
        <div class="metric">
            <div class="metric-label">已付手续费</div>
            <div class="metric-value fee-display" id="total-fee">¥0.00</div>
        </div>
    </div>

    <div class="card">
        <h2>持仓列表</h2>
        <table>
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
                </tr>
            </thead>
            <tbody id="positions"></tbody>
        </table>
    </div>

    <button class="btn-auto" onclick="autoTrade()">自动交易</button>

    <script>
        let ws;
        const positions = new Map();

        document.addEventListener('DOMContentLoaded', function() {
            loadAccount();
            loadPositions();
            connectWebSocket();
        });

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

        function displayAccount(account) {
            document.getElementById('total-asset').textContent = '¥' + account.total_asset.toFixed(2);
            document.getElementById('available-cash').textContent = '¥' + account.available_cash.toFixed(2);
            document.getElementById('market-value').textContent = '¥' + account.market_value.toFixed(2);

            const profit = account.total_profit;
            const profitEl = document.getElementById('total-profit');
            profitEl.textContent = (profit >= 0 ? '+' : '') + '¥' + profit.toFixed(2);
            profitEl.className = 'metric-value ' + (profit >= 0 ? 'profit' : 'loss');

            const rateEl = document.getElementById('profit-rate');
            rateEl.textContent = (account.total_profit_rate >= 0 ? '+' : '') + account.total_profit_rate.toFixed(2) + '%';

            // 获取手续费
            fetch('/api/transactions')
                .then(res => res.json())
                .then(data => {
                    const totalFee = data.data.reduce((sum, t) => sum + t.fee, 0);
                    document.getElementById('total-fee').textContent = '已付 ¥' + totalFee.toFixed(2);
                });
        }

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

        function displayPositions(positions) {
            const tbody = document.getElementById('positions');
            tbody.innerHTML = positions.map(p => {
                const currentPrice = p.current_price || p.buy_price;
                const profit = (currentPrice - p.buy_price) * p.shares;
                const profitRate = ((currentPrice - p.buy_price) / p.buy_price) * 100;
                
                return `
                    <tr>
                        <td>${p.code}</td>
                        <td>${p.name}</td>
                        <td>¥${p.buy_price.toFixed(2)}</td>
                        <td>¥${currentPrice.toFixed(2)}</td>
                        <td>${p.shares}</td>
                        <td>¥${(currentPrice * p.shares).toFixed(2)}</td>
                        <td class="${profit >= 0 ? 'profit' : 'loss'}">${profit >= 0 ? '+' : ''}¥${profit.toFixed(2)}</td>
                        <td class="${profitRate >= 0 ? 'profit' : 'loss'}">${profitRate >= 0 ? '+' : ''}${profitRate.toFixed(2)}%</td>
                    </tr>
                `;
            }).join('');
        }

        async function autoTrade() {
            try {
                const res = await fetch('/api/auto-trade', { method: 'POST' });
                const json = await res.json();
                alert(JSON.stringify(json, null, 2));
                loadAccount();
                loadPositions();
            } catch (e) {
                alert('自动交易失败: ' + e.message);
            }
        }

        async function sellStock(code) {
            if (!confirm(`确定要卖出 ${code} 吗?`)) return;
            try {
                const res = await fetch(`/api/sell/${code}`, { method: 'POST' });
                const json = await res.json();
                alert(json.message);
                if (json.success) {
                    loadAccount();
                    loadPositions();
                }
            } catch (e) {
                alert('卖出失败: ' + e.message);
            }
        }

        async function buyStock(code) {
            if (!confirm(`确定要买入 ${code} 吗?`)) return;
            try {
                const res = await fetch(`/api/buy/${code}`, { method: 'POST' });
                const json = await res.json();
                alert(json.message);
                if (json.success) {
                    loadAccount();
                    loadPositions();
                }
            } catch (e) {
                alert('买入失败: ' + e.message);
            }
        }

        function updateDisplay(data) {
            if (data.account) displayAccount(data.account);
            if (data.positions) displayPositions(data.positions);
        }
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn

    init_trader()

    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path) as f:
        config = json.load(f)

    web_config = config.get('web', {})
    host = web_config.get('host', '127.0.0.1')
    port = web_config.get('port', 8081)

    print("🚀 股票模拟交易系统 v2 启动")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"📚 原理: 总市值 = sum(当前股价 × 持仓数量)")
    print(f"   总收益 = 总资产 - 初始本金")
    print(f"   收益率 = 总收益 / 初始本金")

    uvicorn.run(app, host=host, port=port)
