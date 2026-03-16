#!/usr/bin/env python3
"""
股票模拟交易系统 - Web服务器
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from datetime import datetime
from typing import List
import os

from core import DatabaseManager
from market import MarketData
from trader import TradingEngine

# 加载配置
with open('config.json') as f:
    config = json.load(f)

# 初始化
db = DatabaseManager(config['database']['path'])
market = MarketData()
engine = TradingEngine(db, market, config)

app = FastAPI(title="股票模拟交易系统")

# WebSocket连接列表
active_connections: List[WebSocket] = []

@app.get("/")
async def root():
    """主页"""
    html_file = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/account")
async def get_account():
    """获取账户信息"""
    account = db.get_account()
    return {
        "success": True,
        "data": account
    }

@app.get("/api/positions")
async def get_positions():
    """获取持仓信息"""
    # 更新持仓价格
    engine.update_positions()

    positions = db.get_positions()
    return {
        "success": True,
        "data": positions,
        "count": len(positions)
    }

@app.get("/api/transactions")
async def get_transactions(limit: int = 50):
    """获取交易记录"""
    transactions = db.get_transactions(limit)
    return {
        "success": True,
        "data": transactions,
        "count": len(transactions)
    }

@app.post("/api/buy")
async def manual_buy(code: str, shares: int):
    """手动买入"""
    # 获取实时价格
    stock_data = market.get_realtime_price(code)
    if not stock_data:
        return {
            "success": False,
            "message": f"无法获取{code}的实时价格"
        }

    result = engine.buy_stock(
        code=code,
        name=stock_data['name'],
        price=stock_data['price'],
        shares=shares,
        reason="手动买入"
    )

    return result

@app.post("/api/sell")
async def manual_sell(code: str, shares: int):
    """手动卖出"""
    # 获取实时价格
    stock_data = market.get_realtime_price(code)
    if not stock_data:
        return {
            "success": False,
            "message": f"无法获取{code}的实时价格"
        }

    result = engine.sell_stock(
        code=code,
        price=stock_data['price'],
        shares=shares,
        reason="手动卖出"
    )

    return result

@app.post("/api/auto_trade")
async def trigger_auto_trade():
    """触发自动交易"""
    results = engine.auto_trade()
    return {
        "success": True,
        "data": results
    }

@app.get("/api/scan_stocks")
async def scan_stocks():
    """扫描股票"""
    candidates = market.scan_stocks_by_strategy()
    return {
        "success": True,
        "data": candidates,
        "count": len(candidates)
    }

@app.get("/api/trading_status")
async def get_trading_status():
    """获取交易状态"""
    is_trading = market.is_trading_time()
    now = datetime.now()

    return {
        "success": True,
        "data": {
            "is_trading_time": is_trading,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "weekday": now.weekday(),
            "message": "交易中" if is_trading else "休市"
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接 - 实时推送"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # 等待客户端消息
            data = await websocket.receive_text()

            # 处理消息
            if data == "ping":
                await websocket.send_text("pong")

            elif data == "update":
                # 发送最新数据
                account = db.get_account()
                positions = db.get_positions()
                engine.update_positions()

                await websocket.send_text(json.dumps({
                    "type": "update",
                    "account": account,
                    "positions": positions,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False))

    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        active_connections.remove(websocket)

async def broadcast_update():
    """广播更新到所有客户端"""
    if not active_connections:
        return

    account = db.get_account()
    positions = db.get_positions()
    engine.update_positions()

    message = json.dumps({
        "type": "update",
        "account": account,
        "positions": positions,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False)

    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    print(f"""
╔══════════════════════════════════════════════╗
║     股票模拟交易系统 v1.0.0               ║
╠══════════════════════════════════════════════╣
║  访问地址: http://{config['web']['host']}:{config['web']['port']}         ║
║  初始资金: ¥{config['account']['initial_capital']:,}                    ║
║  交易时间: 周一至周五 9:30-15:00          ║
╚══════════════════════════════════════════════╝
    """)
    uvicorn.run(
        app,
        host=config['web']['host'],
        port=config['web']['port'],
        log_level="info"
    )
