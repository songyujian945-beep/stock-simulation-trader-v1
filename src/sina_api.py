#!/usr/bin/env python3
"""
实时股票价格获取模块 - 使用新浪财经接口
"""
import requests
import re
from typing import Dict, Optional

class SinaStockAPI:
    """新浪财经实时行情接口"""
    
    def __init__(self):
        self.base_url = "http://hq.sinajs.cn/list={}"
        self.headers = {
            'Referer': 'http://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 5  # 5秒超时
    
    def get_realtime_price(self, code: str) -> Optional[Dict]:
        """
        获取实时股票价格
        
        Args:
            code: 股票代码（6位数字）
        
        Returns:
            包含价格信息的字典，失败返回None
        """
        # 添加市场前缀
        if code.startswith('6'):
            sina_code = f"sh{code}"  # 上海
        elif code.startswith('0') or code.startswith('3'):
            sina_code = f"sz{code}"  # 深圳
        else:
            sina_code = code
        
        try:
            url = self.base_url.format(sina_code)
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'gbk'
            
            # 解析数据
            data = response.text
            if 'hq_str_' not in data:
                return None
            
            # 格式: var hq_str_sh601318="中国平安,60.44,59.90,60.50,..."
            match = re.search(r'="([^"]+)"', data)
            if not match:
                return None
            
            parts = match.group(1).split(',')
            if len(parts) < 32:
                return None
            
            # 解析字段
            name = parts[0]
            open_price = float(parts[1])
            yesterday_price = float(parts[2])
            current_price = float(parts[3])
            high_price = float(parts[4])
            low_price = float(parts[5])
            volume = float(parts[8])  # 成交量（股）
            amount = float(parts[9])  # 成交额（元）
            
            # 计算涨跌幅
            change_percent = ((current_price - yesterday_price) / yesterday_price) * 100 if yesterday_price > 0 else 0
            
            return {
                'code': code,
                'name': name,
                'price': current_price,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'yesterday': yesterday_price,
                'change_percent': round(change_percent, 2),
                'volume': volume,
                'amount': amount
            }
            
        except requests.Timeout:
            print(f"⚠️  获取{code}价格超时（{self.timeout}秒）")
            return None
        except Exception as e:
            print(f"❌ 获取{code}价格失败: {e}")
            return None
    
    def get_batch_prices(self, codes: list) -> Dict[str, Dict]:
        """
        批量获取多只股票价格
        
        Args:
            codes: 股票代码列表
        
        Returns:
            {code: price_data} 字典
        """
        results = {}
        for code in codes:
            result = self.get_realtime_price(code)
            if result:
                results[code] = result
        return results


# 测试代码
if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 测试新浪财经接口")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    api = SinaStockAPI()
    
    test_stocks = [
        ('601318', '中国平安'),
        ('600028', '中国石化'),
        ('000858', '五粮液'),
        ('600519', '贵州茅台')
    ]
    
    for code, expected_name in test_stocks:
        print(f"\n测试 {code} {expected_name}")
        result = api.get_realtime_price(code)
        if result:
            print(f"✅ 名称: {result['name']}")
            print(f"   价格: ¥{result['price']:.2f}")
            print(f"   涨跌: {result['change_percent']:+.2f}%")
        else:
            print(f"❌ 获取失败")
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
