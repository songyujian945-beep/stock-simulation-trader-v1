#!/usr/bin/env python3
"""
修复账户数据脚本
重新计算所有账户的市值和总资产
"""
import sys
sys.path.insert(0, 'src')

from core import DatabaseManager

def fix_account_data():
    """修复账户数据"""
    db = DatabaseManager('data/stock_trader.db')
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔧 修复账户数据")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 1. 获取当前账户
    account = db.get_account()
    print("当前账户状态:")
    print(f"  初始资金: ¥{account['initial_capital']:.2f}")
    print(f"  可用现金: ¥{account['available_cash']:.2f}")
    print(f"  持仓市值: ¥{account['market_value']:.2f}")
    print(f"  总资产: ¥{account['total_asset']:.2f}")
    print(f"  总收益: ¥{account['total_profit']:.2f}")
    print(f"  收益率: {account['total_profit_rate']:.2f}%\n")
    
    # 2. 获取所有持仓
    positions = db.get_positions()
    print(f"当前持仓: {len(positions)}只\n")
    
    # 3. 计算实际市值
    actual_market_value = 0
    for pos in positions:
        # 使用买入价格计算市值
        pos_value = pos['shares'] * pos['buy_price']
        actual_market_value += pos_value
        print(f"  {pos['code']} {pos['name']}: {pos['shares']}股 × ¥{pos['buy_price']:.2f} = ¥{pos_value:.2f}")
    
    print(f"\n实际持仓市值: ¥{actual_market_value:.2f}\n")
    
    # 4. 计算正确的总资产
    correct_total_asset = account['available_cash'] + actual_market_value
    correct_profit = correct_total_asset - account['initial_capital']
    correct_profit_rate = (correct_profit / account['initial_capital']) * 100
    
    print("正确的账户数据:")
    print(f"  可用现金: ¥{account['available_cash']:.2f}")
    print(f"  持仓市值: ¥{actual_market_value:.2f}")
    print(f"  总资产: ¥{correct_total_asset:.2f}")
    print(f"  总收益: ¥{correct_profit:.2f}")
    print(f"  收益率: {correct_profit_rate:.2f}%\n")
    
    # 5. 更新账户
    if abs(account['market_value'] - actual_market_value) > 0.01:
        print("⚠️  发现不一致，正在修复...\n")
        db.update_account(
            market_value=actual_market_value,
            total_asset=correct_total_asset,
            total_profit=correct_profit,
            total_profit_rate=correct_profit_rate
        )
        print("✅ 账户数据已修复！\n")
    else:
        print("✅ 账户数据正确，无需修复。\n")
    
    # 6. 显示修复后的状态
    account = db.get_account()
    print("修复后账户状态:")
    print(f"  可用现金: ¥{account['available_cash']:.2f}")
    print(f"  持仓市值: ¥{account['market_value']:.2f}")
    print(f"  总资产: ¥{account['total_asset']:.2f}")
    print(f"  总收益: ¥{account['total_profit']:.2f}")
    print(f"  收益率: {account['total_profit_rate']:.2f}%")
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == '__main__':
    fix_account_data()
