"""模拟价格获取器 - 用于快速测试"""
def get_realtime_price_sina(code, timeout=5):
    """模拟实时价格"""
    import random
    
    # 模拟价格波动
    base_prices = {
        '600019': 6.96,  # 宝钢股份
        '600585': 25.56,  # 海螺水泥
        '601939': 9.24,  # 建设银行
        '600030': 25.74,  # 中信证券
    }
    
    price = base_prices.get(code, 10.0)
    change = random.uniform(-0.1, 0.1)
    
    return {
        'code': code,
        'name': code,  # 模拟名称
        'price': round(price + change, 2),
        'change_percent': round((price + change - price) / price * 100, 2),
        'volume': random.randint(100000, 10000000),
        'amount': random.randint(1000000, 100000000),
        'high': price + 0.2,
        'low': price - 0.2,
        'open': price
    }
