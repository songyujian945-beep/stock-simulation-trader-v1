#!/usr/bin/env python3
"""股票交易引擎 v2 - 模拟版本"""
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import DatabaseManager


class StockTraderV2:
    """股票交易引擎 v2 - 正确的账算逻辑"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db = DatabaseManager(config.get('database', {}).get('path', 'data/stock_trader.db'))

    def is_trading_time(self) -> Tuple[bool, str]:
        """判断是否在交易时间"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()

        if weekday >= 5:
            return False, "周末休市"

        morning_open = time(9, 30)
        morning_close = time(11, 30)
        afternoon_open = time(13, 0)
        afternoon_close = time(15, 0)

        if morning_open <= current_time <= morning_close:
            return True, "上午交易时段"
        elif afternoon_open <= current_time <= afternoon_close:
            return True, "下午交易时段"
        else:
            return False, "非交易时段"

    def get_realtime_price(self, code: str) -> Optional[Dict]:
        """获取股票实时价格（模拟）"""
        base_prices = {
            '600019': 6.96,  
            '600585': 25.56, 
            '601939': 9.24,  
            '600030': 25.74, 
        }
        
        price = base_prices.get(code, 10.0)
        change = random.uniform(-0.1, 0.1)
        
        return {
            'code': code,
            'name': code,
            'price': round(price + change, 2),
            'change_percent': round((price + change - price) / price * 100, 2),
            'volume': random.randint(100000, 10000000),
            'amount': random.randint(1000000, 100000000),
            'high': price + 0.2,
            'low': price - 0.2,
            'open': price
        }

    def calculate_fee(self, amount: float, is_sell: bool = False) -> Dict:
        """计算交易费用"""
        commission = max(amount * self.config.get('account', {}).get('commission_rate', 0.0003), self.config.get('account', {}).get('min_commission', 5))
        stamp_tax = amount * self.config.get('account', {}).get('stamp_tax', 0.001) if is_sell else 0
        
        return {
            'commission': round(commission, 2),
            'stamp_tax': round(stamp_tax, 2),
            'total': round(commission + stamp_tax, 2)
        }

    def buy_stock(self, code: str, shares: int = None) -> Dict:
        """买入股票"""
        is_trading, msg = self.is_trading_time()
        if not is_trading:
            return {'success': False, 'message': f'无法买入: {msg}'}

        quote = self.get_realtime_price(code)
        if not quote:
            return {'success': False, 'message': f'获取{code}实时价格失败'}

        price = quote['price']

        account = self.db.get_account()
        available = account['available_cash']

        if shares is None:
            max_shares = int((available * 0.2) / price)
            shares = (max_shares // 100) * 100

        if shares < 100:
            return {'success': False, 'message': '资金不足，至少需要买入1手(100股)'}

        amount = shares * price
        fee = self.calculate_fee(amount, is_sell=False)
        total_cost = amount + fee['total']

        if total_cost > available:
            return {'success': False, 'message': f'资金不足，需要{total_cost:.2f}'}

        self.db.add_position(code, quote['name'], price, shares)
        self.db.add_transaction(code, quote['name'], 'buy', price, shares, amount, fee['total'])
        self.db.update_account_v2(available_cash=available - total_cost)

        return {
            'success': True,
            'message': f'成功买入{shares}股',
            'details': {
                'code': code,
                'name': quote['name'],
                'price': price,
                'shares': shares,
                'amount': amount,
                'fee': fee['total'],
                'total_cost': total_cost
            }
        }

    def sell_stock(self, code: str, shares: int = None) -> Dict:
        """卖出股票"""
        is_trading, msg = self.is_trading_time()
        if not is_trading:
            return {'success': False, 'message': f'无法卖出: {msg}'}

        positions = self.db.get_positions()
        position = next((p for p in positions if p['code'] == code), None)

        if not position:
            return {'success': False, 'message': f'没有{code}的持仓'}

        # T+1规则
        buy_time = datetime.strptime(position['buy_time'], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()

        if buy_time.date() == now.date():
            return {
                'success': False,
                'message': f'T+1限制：{code}今日买入，明日才可卖出'
            }

        quote = self.get_realtime_price(code)
        if not quote:
            return {'success': False, 'message': f'获取{code}行情失败'}

        price = quote['price']
        shares = shares or position['shares']

        if shares > position['shares']:
            return {'success': False, 'message': f'持仓不足，只有{position["shares"]}股'}

        amount = shares * price
        fee = self.calculate_fee(amount, is_sell=True)
        total_income = amount - fee['total']

        self.db.remove_position(code)
        self.db.add_transaction(code, quote['name'], 'sell', price, shares, amount, fee['total'])
        self.db.update_account_v2(available_cash=account['available_cash'] + total_income)

        return {
            'success': True,
            'message': f'成功卖出{shares}股',
            'details': {
                'code': code,
                'price': price,
                'shares': shares,
                'amount': amount,
                'fee': fee['total'],
                'total_income': total_income
            }
        }

    def update_positions(self):
        """更新所有持仓的实时价格"""
        positions = self.db.get_positions()
        for pos in positions:
            quote = self.get_realtime_price(pos['code'])
            if quote:
                self.db.update_position(code=pos['code'], current_price=quote['price'])

    def get_account_overview(self) -> Dict:
        """获取账户概览"""
        self.update_positions()

        account = self.db.get_account()
        positions = self.db.get_positions()

        # 总市值 = sum(当前股价 × 持仓数量)
        total_market_value = sum(
            pos['shares'] * (pos.get('current_price') or pos['buy_price'])
            for pos in positions
        )

        # 总资产 = 总市值 + 可用现金
        total_asset = total_market_value + account['available_cash']

        # 总收益 = 总资产 - 初始本金
        total_profit = total_asset - account['initial_capital']

        # 收益率 = 总收益 / 初始本金
        total_profit_rate = (total_profit / account['initial_capital']) * 100 if account['initial_capital'] > 0 else 0

        self.db.update_account(
            market_value=total_market_value,
            total_asset=total_asset,
            total_profit=total_profit,
            total_profit_rate=total_profit_rate
        )

        return {
            'account': self.db.get_account(),
            'positions': positions,
            'recent_transactions': self.db.get_transactions(limit=10),
            'position_count': len(positions),
            'is_trading_time': self.is_trading_time()
        }
