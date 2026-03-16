#!/usr/bin/env python3
"""
股票模拟交易系统 - 主程序
作者: 宋先生的数字分身
版本: v1.0.0
"""
import sys
import os
import argparse
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票模拟交易系统 v1.0')
    parser.add_argument('command', choices=['start', 'web', 'status', 'trade'],
                       help='命令: start-启动, web-Web界面, status-状态, trade-交易')
    parser.add_argument('--code', help='股票代码')
    parser.add_argument('--shares', type=int, help='股数')
    parser.add_argument('--action', choices=['buy', 'sell'], help='操作类型')

    args = parser.parse_args()

    if args.command == 'start':
        start_system()
    elif args.command == 'web':
        start_web()
    elif args.command == 'status':
        show_status()
    elif args.command == 'trade':
        if not args.code or not args.action:
            print("❌ 交易需要指定 --code 和 --action")
            return
        execute_trade(args.code, args.action, args.shares)

def start_system():
    """启动系统"""
    print("=" * 60)
    print("📈 股票模拟交易系统 v1.0")
    print("=" * 60)
    print()
    print("系统功能:")
    print("  ✅ 动态选股 - 自动筛选优质股票")
    print("  ✅ 实时监控 - 实时更新持仓价格")
    print("  ✅ 自动交易 - 根据策略自动买卖")
    print("  ✅ Web界面  - 可视化监控面板")
    print()
    print("启动方式:")
    print("  python main.py web       # 启动Web界面")
    print("  python main.py status    # 查看账户状态")
    print("  python main.py trade --code 600519 --action buy  # 手动交易")
    print()

def start_web():
    """启动Web服务"""
    from src.web import app
    import uvicorn
    import json

    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)

    web_config = config.get('web', {})
    host = web_config.get('host', '127.0.0.1')
    port = web_config.get('port', 8080)

    print()
    print("=" * 60)
    print("🚀 股票模拟交易系统 v1.0 - Web界面")
    print("=" * 60)
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"📊 初始资金: ¥50,000")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    uvicorn.run(app, host=host, port=port)

def show_status():
    """显示系统状态"""
    from src.trader import StockTrader
    import json

    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)

    trader = StockTrader(config)
    overview = trader.get_account_overview()
    is_trading, msg = trader.is_trading_time()

    print()
    print("=" * 60)
    print("📊 账户概览")
    print("=" * 60)
    print(f"{'总资产:':<15} ¥{overview['account']['total_asset']:,.2f}")
    print(f"{'可用资金:':<15} ¥{overview['account']['available_cash']:,.2f}")
    print(f"{'持仓市值:':<15} ¥{overview['account']['market_value']:,.2f}")
    print(f"{'总收益:':<15} ¥{overview['account']['total_profit']:,.2f}")
    print(f"{'收益率:':<15} {overview['account']['total_profit_rate']:.2f}%")
    print()
    print(f"{'交易状态:':<15} {msg}")
    print(f"{'持仓数量:':<15} {overview['position_count']}只")
    print("=" * 60)
    print()

    if overview['positions']:
        print("📈 当前持仓:")
        print("-" * 60)
        for pos in overview['positions']:
            profit_sign = '+' if pos['profit'] >= 0 else ''
            print(f"{pos['code']} {pos['name']}")
            print(f"  买入价: ¥{pos['buy_price']:.2f}  "
                  f"现价: ¥{pos['current_price']:.2f}  "
                  f"收益: {profit_sign}{pos['profit']:.2f}元 ({profit_sign}{pos['profit_rate']:.2f}%)")
        print("=" * 60)

def execute_trade(code: str, action: str, shares: int = None):
    """执行交易"""
    from src.trader import StockTrader
    import json

    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)

    trader = StockTrader(config)

    print()
    print("=" * 60)
    print(f"{'买入' if action == 'buy' else '卖出'}股票: {code}")
    print("=" * 60)

    if action == 'buy':
        result = trader.buy_stock(code, shares)
    else:
        result = trader.sell_stock(code, shares)

    if result['success']:
        print(f"✅ {result['message']}")
        if 'details' in result:
            print()
            print("交易详情:")
            for key, value in result['details'].items():
                print(f"  {key}: {value}")
    else:
        print(f"❌ {result['message']}")

    print("=" * 60)
    print()

if __name__ == '__main__':
    main()
