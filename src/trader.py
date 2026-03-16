#!/usr/bin/env python3
"""
股票模拟交易系统 - 交易引擎
"""
import akshare as ak
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import sys
import os
import requests
import re

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import DatabaseManager
from strategy import StockStrategy

# 导入新浪财经价格获取工具
try:
    from price_fetcher import get_realtime_price_sina
    USE_SINA = True
    print("✅ 使用新浪财经接口（稳定）")
except ImportError:
    USE_SINA = False
    print("⚠️  使用akshare接口（可能需要代理）")

class StockTrader:
    """股票交易引擎"""

    def __init__(self, config: Dict):
        self.config = config
        self.db = DatabaseManager(config.get('database', {}).get('path', 'data/stock_trader.db'))
        self.strategy = StockStrategy()

        # 交易配置
        self.commission_rate = config.get('account', {}).get('commission_rate', 0.0003)
        self.stamp_tax = config.get('account', {}).get('stamp_tax', 0.001)
        self.min_commission = config.get('account', {}).get('min_commission', 5)
        self.max_positions = config.get('strategy', {}).get('max_positions', 5)
        self.position_size = config.get('strategy', {}).get('position_size', 0.2)

    # ========== 交易时间判断 ==========

    def is_trading_time(self) -> Tuple[bool, str]:
        """判断是否在交易时间"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()

        # 周末不交易
        if weekday >= 5:
            return False, "周末休市"

        # 交易时间段
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

    # ========== 获取实时行情 ==========

    def get_realtime_price(self, code: str) -> Optional[Dict]:
        """获取股票实时价格（带超时控制）"""
        # 优先使用新浪财经接口（更稳定）
        if USE_SINA:
            return get_realtime_price_sina(code, timeout=5)
        
        # 降级到akshare（可能需要代理）
        try:
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                return None
            
            stock = df[df['代码'] == code]
            
            if stock.empty:
                return None
            
            row = stock.iloc[0]
            return {
                'code': code,
                'name': row['名称'],
                'price': float(row['最新价']),
                'change_percent': float(row['涨跌幅']),
                'volume': float(row['成交量']),
                'amount': float(row['成交额']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'open': float(row['今开'])
            }
        except Exception as e:
            print(f"获取{code}行情失败: {e}")
            return None

    # ========== 计算交易费用 ==========

    def calculate_fee(self, amount: float, is_sell: bool = False) -> Dict:
        """计算交易费用"""
        # 佣金
        commission = max(amount * self.commission_rate, self.min_commission)

        # 印花税（仅卖出）
        stamp_tax = amount * self.stamp_tax if is_sell else 0

        return {
            'commission': round(commission, 2),
            'stamp_tax': round(stamp_tax, 2),
            'total': round(commission + stamp_tax, 2)
        }

    # ========== 买入股票 ==========

    def buy_stock(self, code: str, shares: int = None) -> Dict:
        """买入股票（必须使用实时价格）"""
        # 检查交易时间
        is_trading, msg = self.is_trading_time()
        if not is_trading:
            return {'success': False, 'message': f'无法买入: {msg}'}

        # 获取实时价格（必须成功）
        quote = self.get_realtime_price(code)
        
        # 如果获取失败，拒绝交易
        if not quote:
            return {'success': False, 'message': f'获取{code}实时价格失败，拒绝交易'}
        if not quote:
            return {'success': False, 'message': f'获取{code}行情失败'}

        price = quote['price']

        # 计算买入数量（100股为一手）
        account = self.db.get_account()
        available = account['available_cash']

        if shares is None:
            # 自动计算可买数量
            max_shares = int((available * self.position_size) / price)
            shares = (max_shares // 100) * 100  # 向下取整到100股倍数

        if shares < 100:
            return {'success': False, 'message': '资金不足，至少需要买入1手(100股)'}

        # 计算费用
        amount = shares * price
        fee = self.calculate_fee(amount, is_sell=False)
        total_cost = amount + fee['total']

        if total_cost > available:
            return {'success': False, 'message': f'资金不足，需要{total_cost:.2f}，可用{available:.2f}'}

        # 执行买入
        self.db.add_position(code, quote['name'], price, shares)
        
        # 立即设置当前价格（买入价=当前价）
        self.db.update_position(code, current_price=price, profit=0, profit_rate=0)
        
        self.db.add_transaction(
            code, quote['name'], 'buy',
            price, shares, amount, fee['total'],
            reason=f"策略买入 @¥{price:.2f}"
        )

        # 更新账户（正确计算总资产）
        new_cash = available - total_cost
        new_market_value = self._calculate_market_value() + (shares * price)  # 增加持仓市值
        new_total_asset = new_cash + new_market_value
        new_profit = new_total_asset - account['initial_capital']
        new_profit_rate = (new_profit / account['initial_capital']) * 100 if account['initial_capital'] > 0 else 0

        self.db.update_account(
            available_cash=new_cash,
            market_value=new_market_value,
            total_asset=new_total_asset,
            total_profit=new_profit,
            total_profit_rate=new_profit_rate
        )

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

    def _calculate_market_value(self) -> float:
        """计算当前持仓总市值"""
        positions = self.db.get_positions()
        total_value = 0
        for pos in positions:
            # 使用当前价格（如果有）或买入价格
            current_price = pos.get('current_price') or pos['buy_price']
            total_value += pos['shares'] * current_price
        return total_value

    # ========== 卖出股票 ==========

    def sell_stock(self, code: str, shares: int = None) -> Dict:
        """卖出股票（遵守T+1规则）"""
        # 检查交易时间
        is_trading, msg = self.is_trading_time()
        if not is_trading:
            return {'success': False, 'message': f'无法卖出: {msg}'}

        # 获取持仓
        positions = self.db.get_positions()
        position = None
        for p in positions:
            if p['code'] == code:
                position = p
                break

        if not position:
            return {'success': False, 'message': f'没有{code}的持仓'}

        # 🔒 T+1规则：检查是否买入当天
        buy_time = datetime.strptime(position['buy_time'], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        
        # 如果买入日期 == 当前日期，拒绝卖出
        if buy_time.date() == now.date():
            return {
                'success': False, 
                'message': f'T+1限制：{code}今日买入，明日才可卖出'
            }

        # 获取实时价格
        quote = self.get_realtime_price(code)
        if not quote:
            return {'success': False, 'message': f'获取{code}行情失败'}

        price = quote['price']
        shares = shares or position['shares']

        if shares > position['shares']:
            return {'success': False, 'message': f'持仓不足，只有{position["shares"]}股'}

        # 计算费用和收益
        amount = shares * price
        fee = self.calculate_fee(amount, is_sell=True)
        total_income = amount - fee['total']

        buy_amount = shares * position['buy_price']
        profit = total_income - buy_amount
        profit_rate = (profit / buy_amount) * 100

        # 执行卖出
        self.db.remove_position(code)
        self.db.add_transaction(
            code, quote['name'], 'sell',
            price, shares, amount, fee['total'],
            reason=f"卖出，收益{profit:.2f}({profit_rate:+.2f}%)"
        )

        # 更新账户（卖出时减少市值）
        account = self.db.get_account()
        new_cash = account['available_cash'] + total_income
        
        # 计算新的持仓市值（卖出后减少）
        new_market_value = self._calculate_market_value() - (shares * position['buy_price'])
        new_total_asset = new_cash + new_market_value
        new_profit = new_total_asset - account['initial_capital']
        new_profit_rate = (new_profit / account['initial_capital']) * 100 if account['initial_capital'] > 0 else 0
        
        self.db.update_account(
            available_cash=new_cash,
            market_value=new_market_value,
            total_asset=new_total_asset,
            total_profit=new_profit,
            total_profit_rate=new_profit_rate
        )

        return {
            'success': True,
            'message': f'成功卖出{shares}股，收益{profit:.2f}元({profit_rate:+.2f}%)',
            'details': {
                'code': code,
                'name': quote['name'],
                'price': price,
                'shares': shares,
                'amount': amount,
                'fee': fee['total'],
                'total_income': total_income,
                'profit': profit,
                'profit_rate': profit_rate,
                'new_cash': new_cash,
                'new_market_value': new_market_value,
                'new_total_asset': new_total_asset
            }
        }

    # ========== 自动交易 ==========

    def auto_trade(self) -> Dict:
        """自动交易（根据策略）"""
        results = {
            'buy': [],
            'sell': [],
            'hold': []
        }

        # 检查交易时间
        is_trading, msg = self.is_trading_time()
        if not is_trading:
            return {'success': False, 'message': msg, 'results': results}

        # 1. 检查持仓，判断是否卖出（遵守T+1）
        positions = self.db.get_positions()
        for pos in positions:
            # 🔒 T+1检查：跳过今天买入的股票
            buy_time = datetime.strptime(pos['buy_time'], '%Y-%m-%d %H:%M:%S')
            if buy_time.date() == datetime.now().date():
                results['hold'].append({
                    'code': pos['code'],
                    'name': pos['name'],
                    'buy_price': pos['buy_price'],
                    'current_price': pos.get('current_price', pos['buy_price']),
                    'profit_rate': 0,
                    'reason': 'T+1限制，今日不可卖出'
                })
                continue
            
            quote = self.get_realtime_price(pos['code'])
            if not quote:
                continue

            should_sell, reason = self.strategy.should_sell(pos, quote['price'])

            if should_sell:
                result = self.sell_stock(pos['code'])
                results['sell'].append({
                    'code': pos['code'],
                    'name': pos['name'],
                    'action': 'sell',
                    'success': result['success'],
                    'message': result['message'],
                    'reason': reason
                })
            else:
                results['hold'].append({
                    'code': pos['code'],
                    'name': pos['name'],
                    'buy_price': pos['buy_price'],
                    'current_price': quote['price'],
                    'profit_rate': ((quote['price'] - pos['buy_price']) / pos['buy_price']) * 100
                })

        # 2. 如果持仓未满，寻找买入机会
        if len(positions) < self.max_positions:
            # 获取推荐股票池
            stocks = self.strategy.get_stock_pool(10)

            for stock in stocks:
                # 避免重复买入
                if any(p['code'] == stock['code'] for p in positions):
                    continue

                should_buy, reason = self.strategy.should_buy(stock)

                if should_buy:
                    # 必须使用实时价格买入，不传fallback_price
                    result = self.buy_stock(stock['code'])
                    results['buy'].append({
                        'code': stock['code'],
                        'name': stock['name'],
                        'action': 'buy',
                        'success': result['success'],
                        'message': result['message'],
                        'reason': reason
                    })

                    # 买入后更新持仓列表
                    if result['success']:
                        positions = self.db.get_positions()
                        if len(positions) >= self.max_positions:
                            break

        return {
            'success': True,
            'message': '自动交易完成',
            'results': results
        }

    # ========== 更新持仓价格 ==========

    def update_positions(self):
        """更新所有持仓的实时价格"""
        positions = self.db.get_positions()
        total_market_value = 0

        for pos in positions:
            quote = self.get_realtime_price(pos['code'])
            if quote:
                self.db.update_position(
                    pos['code'],
                    current_price=quote['price'],
                    profit=(quote['price'] - pos['buy_price']) * pos['shares'],
                    profit_rate=((quote['price'] - pos['buy_price']) / pos['buy_price']) * 100
                )
                total_market_value += quote['price'] * pos['shares']

        # 更新账户市值
        account = self.db.get_account()
        total_asset = account['available_cash'] + total_market_value
        total_profit = total_asset - account['initial_capital']

        self.db.update_account(
            market_value=total_market_value,
            total_asset=total_asset,
            total_profit=total_profit,
            total_profit_rate=(total_profit / account['initial_capital']) * 100
        )

    # ========== 获取账户概览 ==========

    def get_account_overview(self) -> Dict:
        """获取账户概览"""
        account = self.db.get_account()
        positions = self.db.get_positions()
        transactions = self.db.get_transactions(limit=10)

        # 更新持仓价格
        self.update_positions()

        # 重新获取更新后的数据
        account = self.db.get_account()
        positions = self.db.get_positions()

        return {
            'account': account,
            'positions': positions,
            'recent_transactions': transactions,
            'position_count': len(positions),
            'is_trading_time': self.is_trading_time()
        }


if __name__ == "__main__":
    # 测试交易引擎
    import json

    with open('../config.json') as f:
        config = json.load(f)

    trader = StockTrader(config)

    # 检查交易时间
    is_trading, msg = trader.is_trading_time()
    print(f"交易时间: {is_trading} - {msg}")

    # 获取账户概览
    overview = trader.get_account_overview()
    print("\n账户概览:")
    print(json.dumps(overview, indent=2, ensure_ascii=False, default=str))
