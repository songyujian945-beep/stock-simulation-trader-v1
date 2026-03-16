"""
账户更新工具函数
修复总资产计算逻辑
"""

def update_account_after_trade(db, operation: str, cash_change: float, stock_code: str = None, shares: int = None, price: float = None):
    """
    交易后更新账户（正确计算总资产）
    
    Args:
        db: 数据库实例
        operation: 'buy' 或 'sell'
        cash_change: 现金变化（买入为负，卖出为正）
        stock_code: 股票代码
        shares: 股数
        price: 价格
    """
    account = db.get_account()
    
    # 1. 更新可用现金
    new_cash = account['available_cash'] + cash_change
    
    # 2. 重新计算持仓市值
    positions = db.get_positions()
    new_market_value = 0
    
    for pos in positions:
        # 如果是刚买入的股票，还没有在positions中，需要加上
        if operation == 'buy' and pos['code'] == stock_code:
            new_market_value += shares * price
        else:
            # 使用当前价格或买入价格
            current_price = pos.get('current_price') or pos['buy_price']
            new_market_value += pos['shares'] * current_price
    
    # 3. 计算总资产
    new_total_asset = new_cash + new_market_value
    
    # 4. 计算收益
    initial_capital = account['initial_capital']
    new_profit = new_total_asset - initial_capital
    new_profit_rate = (new_profit / initial_capital) * 100 if initial_capital > 0 else 0
    
    # 5. 更新账户
    db.update_account(
        available_cash=new_cash,
        market_value=new_market_value,
        total_asset=new_total_asset,
        total_profit=new_profit,
        total_profit_rate=new_profit_rate
    )
    
    print(f"📊 账户更新:")
    print(f"  现金: ¥{account['available_cash']:.2f} → ¥{new_cash:.2f}")
    print(f"  市值: ¥{account['market_value']:.2f} → ¥{new_market_value:.2f}")
    print(f"  总资产: ¥{account['total_asset']:.2f} → ¥{new_total_asset:.2f}")
    print(f"  收益率: {account['total_profit_rate']:.2f}% → {new_profit_rate:.2f}%")


def recalculate_total_asset(db):
    """
    重新计算总资产（用于修复）
    """
    account = db.get_account()
    positions = db.get_positions()
    
    # 计算持仓总市值
    market_value = 0
    for pos in positions:
        current_price = pos.get('current_price') or pos['buy_price']
        market_value += pos['shares'] * current_price
    
    # 计算总资产
    total_asset = account['available_cash'] + market_value
    
    # 计算收益
    initial_capital = account['initial_capital']
    profit = total_asset - initial_capital
    profit_rate = (profit / initial_capital) * 100 if initial_capital > 0 else 0
    
    # 更新账户
    db.update_account(
        market_value=market_value,
        total_asset=total_asset,
        total_profit=profit,
        total_profit_rate=profit_rate
    )
    
    print("✅ 总资产已重新计算:")
    print(f"  现金: ¥{account['available_cash']:.2f}")
    print(f"  市值: ¥{market_value:.2f}")
    print(f"  总资产: ¥{total_asset:.2f}")
    print(f"  收益率: {profit_rate:.2f}%")
    
    return {
        'available_cash': account['available_cash'],
        'market_value': market_value,
        'total_asset': total_asset,
        'profit': profit,
        'profit_rate': profit_rate
    }


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'src')
    from core import DatabaseManager
    
    db = DatabaseManager('data/stock_trader.db')
    result = recalculate_total_asset(db)
    
    print("\n当前账户状态:")
    account = db.get_account()
    for key, value in account.items():
        if key in ['available_cash', 'market_value', 'total_asset', 'total_profit']:
            print(f"  {key}: {value}")
