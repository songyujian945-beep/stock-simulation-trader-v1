#!/usr/bin/env python3
"""
股票模拟交易系统 - 行情数据获取
"""
import akshare as ak
import pandas as pd
from datetime import datetime, time
from typing import List, Dict, Optional
import time as time_module

class MarketData:
    """市场数据获取"""

    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 3  # 缓存3秒

    def is_trading_time(self) -> bool:
        """判断是否交易时间"""
        now = datetime.now()
        current_time = now.time()

        # 周末不交易
        if now.weekday() >= 5:
            return False

        # 上午 9:30-11:30
        if time(9, 30) <= current_time <= time(11, 30):
            return True

        # 下午 13:00-15:00
        if time(13, 0) <= current_time <= time(15, 0):
            return True

        return False

    def get_realtime_price(self, code: str) -> Optional[Dict]:
        """获取实时价格（带缓存）"""
        # 检查缓存
        if code in self.cache and code in self.cache_time:
            if time_module.time() - self.cache_time[code] < self.cache_duration:
                return self.cache[code]

        try:
            # 格式化股票代码
            if code.startswith('6'):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"

            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == code]

            if stock_data.empty:
                return None

            row = stock_data.iloc[0]
            data = {
                'code': code,
                'name': row['名称'],
                'price': float(row['最新价']),
                'change': float(row['涨跌幅']),
                'change_amount': float(row['涨跌额']),
                'volume': float(row['成交量']),
                'amount': float(row['成交额']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'open': float(row['今开']),
                'pre_close': float(row['昨收']),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 更新缓存
            self.cache[code] = data
            self.cache_time[code] = time_module.time()

            return data

        except Exception as e:
            print(f"获取{code}实时价格失败: {e}")
            return None

    def get_multiple_prices(self, codes: List[str]) -> Dict[str, Dict]:
        """批量获取实时价格"""
        result = {}
        for code in codes:
            data = self.get_realtime_price(code)
            if data:
                result[code] = data
            time_module.sleep(0.1)  # 避免请求过快
        return result

    def get_stock_list(self) -> List[Dict]:
        """获取所有A股列表"""
        try:
            df = ak.stock_zh_a_spot_em()
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change': row['涨跌幅'],
                    'industry': row.get('行业', '')
                })
            return stocks
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []

    def scan_stocks_by_strategy(self, strategy: str = 'rsi') -> List[Dict]:
        """根据策略扫描股票"""
        print(f"正在扫描股票（策略: {strategy}）...")

        try:
            # 获取所有股票
            df = ak.stock_zh_a_spot_em()

            # 筛选条件
            # 1. 价格 > 5元
            df = df[df['最新价'] > 5]

            # 2. 涨跌幅在合理范围
            df = df[(df['涨跌幅'] > -5) & (df['涨跌幅'] < 5)]

            # 3. 成交量 > 平均水平
            avg_volume = df['成交量'].mean()
            df = df[df['成交量'] > avg_volume]

            # 4. 排除ST股票
            df = df[~df['名称'].str.contains('ST')]

            # 5. 排除新股（上市不足60天）
            # 这里简化处理，实际需要获取上市日期

            # 按涨跌幅排序，选择前20只
            df = df.sort_values('涨跌幅', ascending=False).head(20)

            candidates = []
            for _, row in df.iterrows():
                candidates.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change': row['涨跌幅'],
                    'volume': row['成交量'],
                    'reason': f"涨幅{row['涨跌幅']:.2f}%, 成交活跃"
                })

            print(f"扫描完成，找到{len(candidates)}只候选股票")
            return candidates

        except Exception as e:
            print(f"扫描股票失败: {e}")
            return []

    def get_kline_data(self, code: str, period: str = 'daily', count: int = 30) -> pd.DataFrame:
        """获取K线数据"""
        try:
            if code.startswith('6'):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"

            df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="qfq")
            df = df.tail(count)
            return df
        except Exception as e:
            print(f"获取{code}K线数据失败: {e}")
            return pd.DataFrame()

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50  # 默认中性值

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

if __name__ == "__main__":
    market = MarketData()

    # 测试获取实时价格
    print("测试获取实时价格:")
    data = market.get_realtime_price("000001")
    if data:
        print(f"股票: {data['name']}, 价格: {data['price']}, 涨幅: {data['change']}%")

    # 测试交易时间判断
    print(f"\n当前是否交易时间: {market.is_trading_time()}")

    # 测试扫描股票
    print("\n扫描股票:")
    candidates = market.scan_stocks_by_strategy()
    for stock in candidates[:5]:
        print(f"{stock['code']} {stock['name']}: {stock['reason']}")
