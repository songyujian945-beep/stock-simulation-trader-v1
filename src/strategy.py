#!/usr/bin/env python3
"""
股票模拟交易系统 - 选股策略模块
动态选股、技术指标分析
"""
import akshare as ak
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import random

# 导入新浪财经API
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sina_api import SinaStockAPI

class StockStrategy:
    """选股策略"""

    def __init__(self):
        self.min_price = 1  # 最低股价
        self.max_price = 60  # 最高股价
        self.min_volume = 100000  # 最小成交量
        self.sina_api = SinaStockAPI()  # 使用新浪API

    def get_stock_pool(self, count: int = 20) -> List[Dict]:
        """动态获取股票池（使用新浪财经API）"""
        try:
            # 获取A股实时行情
            df = ak.stock_zh_a_spot_em()

            # 过滤条件
            df = df[
                (df['最新价'] >= self.min_price) &
                (df['最新价'] <= self.max_price) &
                (df['成交量'] >= self.min_volume)
            ]

            # 计算评分
            df['score'] = self._calculate_score(df)

            # 按评分排序
            df = df.sort_values('score', ascending=False)

            # 随机选择前count只股票
            top_stocks = df.head(count * 2)
            selected = top_stocks.sample(n=min(count, len(top_stocks)))

            stocks = []
            for _, row in selected.iterrows():
                stocks.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'change_percent': float(row['涨跌幅']),
                    'volume': float(row['成交量']),
                    'amount': float(row['成交额']),
                    'score': float(row['score'])
                })

            return stocks

        except Exception as e:
            print(f"获取股票池失败: {e}")
            return self._get_fallback_stocks()

    def _calculate_score(self, df: pd.DataFrame) -> pd.Series:
        """计算股票评分"""
        # 涨跌幅权重 - 避免过度追高
        change_score = np.where(
            (df['涨跌幅'] > 0) & (df['涨跌幅'] < 5),  # 温和上涨
            df['涨跌幅'] * 2,
            np.where(df['涨跌幅'] < 0,  # 下跌给低分
                     df['涨跌幅'] * 0.5,
                     0)
        )

        # 成交额权重 - 关注活跃股票
        amount_score = (df['成交额'] / df['成交额'].mean()) * 10

        # 综合评分
        score = change_score + amount_score
        return score

    def _get_fallback_stocks(self) -> List[Dict]:
        """备用股票池（当API失败时）- 价格1-60元"""
        fallback = [
            {'code': '600030', 'name': '中信证券', 'price': 25},
            {'code': '601166', 'name': '兴业银行', 'price': 18},
            {'code': '601318', 'name': '中国平安', 'price': 45},
            {'code': '600036', 'name': '招商银行', 'price': 32},
            {'code': '000651', 'name': '格力电器', 'price': 38},
            {'code': '600276', 'name': '恒瑞医药', 'price': 42},
            {'code': '000333', 'name': '美的集团', 'price': 55},
            {'code': '601688', 'name': '华泰证券', 'price': 15},
            {'code': '600585', 'name': '海螺水泥', 'price': 28},
            {'code': '000002', 'name': '万科A', 'price': 12},
            {'code': '600028', 'name': '中国石化', 'price': 5},
            {'code': '601288', 'name': '农业银行', 'price': 3},
            {'code': '601398', 'name': '工商银行', 'price': 5},
            {'code': '600019', 'name': '宝钢股份', 'price': 6},
            {'code': '601939', 'name': '建设银行', 'price': 6},
        ]

        for stock in fallback:
            stock['change_percent'] = random.uniform(-3, 5)
            stock['volume'] = random.randint(100000, 1000000)
            stock['score'] = random.uniform(5, 15)

        return random.sample(fallback, min(5, len(fallback)))

    def should_buy(self, stock: Dict) -> tuple:
        """判断是否应该买入（积极策略）"""
        score = stock.get('score', 0)
        change = stock.get('change_percent', 0)
        volume = stock.get('volume', 0)

        # 1. 温和上涨（评分要求降低，更容易买入）
        if score > 5 and 0 < change < 5:
            return True, f"温和上涨，评分{score:.1f}，涨幅{change:.2f}%"

        # 2. 超跌反弹（扩大范围）
        if -7 < change < -1:
            return True, f"超跌反弹机会，跌幅{change:.2f}%"

        # 3. 成交量放大（活跃股）
        if volume > 500000 and score > 3:
            return True, f"成交量放大，成交{volume:.0f}股，评分{score:.1f}"

        # 4. 平盘整理（可能突破）
        if -1 < change < 1 and score > 4:
            return True, f"平盘整理，可能突破，评分{score:.1f}"

        # 5. 强势上涨（追涨）
        if 3 < change < 8 and score > 6:
            return True, f"强势上涨，涨幅{change:.2f}%，评分{score:.1f}"

        # 6. 随机买入（模拟盘可以更积极）
        if random.random() < 0.3 and score > 2:  # 30%概率买入评分>2的股票
            return True, f"积极建仓，评分{score:.1f}"

        return False, "不符合买入条件"

    def should_sell(self, position: Dict, current_price: float) -> tuple:
        """判断是否应该卖出"""
        buy_price = position['buy_price']
        profit_rate = ((current_price - buy_price) / buy_price) * 100

        # 止盈
        if profit_rate >= 10:
            return True, f"达到止盈点，收益率{profit_rate:.2f}%"

        # 止损
        if profit_rate <= -5:
            return True, f"触发止损，亏损{profit_rate:.2f}%"

        return False, "继续持有"


if __name__ == "__main__":
    strategy = StockStrategy()
    stocks = strategy.get_stock_pool(10)
    print("推荐股票池:")
    for stock in stocks:
        print(f"{stock['code']} {stock['name']}: ¥{stock['price']:.2f} "
              f"({stock['change_percent']:+.2f}%) 评分:{stock['score']:.1f}")
