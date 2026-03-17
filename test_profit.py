#!/usr/bin/env python3
"""快速测试收益计算"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trader import StockTrader
import json

print("="*60)
print("股票交易系统 - 收益计算测试")
print("="*60)

# 初始化交易器
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path) as f:
    config = json.load(f)

trader = StockTrader(config)

# 获取账户概览
overview = trader.get_account_overview()

print("\n账户信息:")
print(f"初始资金: ¥{overview['account']['initial_capital']}")
print(f"可用现金: ¥{overview['account']['available_cash']}")
print(f"持仓市值: ¥{overview['account']['market_value']}")
print(f"总资产: ¥{overview['account']['total_asset']}")
print(f"总收益: ¥{overview['account']['total_profit']}")
print(f"收益率: ¥{overview['account']['total_profit_rate']:.2f}%")

print("\n持仓列表:")
for pos in overview['positions']:
    profit = pos['profit']
    profit_rate = pos['profit_rate']
    print(f"  {pos['code']} {pos['name']}: ¥{pos['buy_price']:.2f} -> ¥{pos['current_price']:.2f}, "
          f"{pos['shares']}股, 收益: ¥{profit:.2f} ({profit_rate:.2f}%)")

print("\n交易记录:")
for t in overview['recent_transactions']:
    print(f"  {t['type'].upper()}: {t['code']} {t['shares']}股 @ ¥{t['price']:.2f}, "
          f"手续费: ¥{t['fee']:.2f}")

# 验证计算
positions = overview['positions']
available_cash = overview['account']['available_cash']
initial_capital = overview['account']['initial_capital']

# 手续费
commission_rate = config['account']['commission_rate']
min_commission = config['account']['min_commission']
total_fees = sum(max(pos['shares'] * pos['buy_price'] * commission_rate, min_commission)
                for pos in positions)

# 股票变动
stock_change = sum(pos['shares'] * (pos['current_price'] - pos['buy_price'])
                  for pos in positions)

# 正确收益
correct_profit = (available_cash + sum(pos['shares'] * pos['current_price'] for pos in positions)
                 - initial_capital) - total_fees

print("\n" + "="*60)
print("验证:")
print("="*60)
print(f"持仓收益(股票变动): ¥{stock_change:.2f}")
print(f"总手续费: ¥{total_fees:.2f}")
print(f"------------------")
print(f"正确收益计算: ¥{correct_profit:.2f}")
print(f"API返回收益: ¥{overview['account']['total_profit']:.2f}")
print(f"差异: ¥{overview['account']['total_profit'] - correct_profit:.2f}")

if abs(overview['account']['total_profit'] - correct_profit) < 0.01:
    print("\n✅ 收益计算正确！")
    sys.exit(0)
else:
    print("\n❌ 收益计算有误！")
    sys.exit(1)
