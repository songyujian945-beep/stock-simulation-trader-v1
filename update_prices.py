#!/usr/bin/env python3
"""
定时更新持仓价格的后台任务
每分钟更新一次实时价格
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trader import StockTrader
import json

async def update_prices_periodically():
    """定时更新价格（每60秒）"""
    print("🔄 启动价格更新任务...")
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as f:
        config = json.load(f)
    
    trader = StockTrader(config)
    
    while True:
        try:
            print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - 更新持仓价格...")
            
            positions = trader.db.get_positions()
            
            if not positions:
                print("  当前无持仓")
                await asyncio.sleep(60)
                continue
            
            print(f"  发现 {len(positions)} 只持仓")
            
            updated_count = 0
            for pos in positions:
                try:
                    quote = trader.get_realtime_price(pos['code'])
                    if quote:
                        current_price = quote['price']
                        trader.db.update_position(
                            pos['code'],
                            current_price=current_price,
                            profit=(current_price - pos['buy_price']) * pos['shares'],
                            profit_rate=((current_price - pos['buy_price']) / pos['buy_price']) * 100
                        )
                        print(f"  ✅ {pos['code']} {pos['name']}: ¥{current_price:.2f}")
                        updated_count += 1
                    else:
                        print(f"  ⚠️  {pos['code']} {pos['name']}: 获取失败，使用原价 ¥{pos['buy_price']:.2f}")
                except Exception as e:
                    print(f"  ❌ {pos['code']}: 更新失败 - {e}")
            
            # 更新账户总市值
            if updated_count > 0:
                trader.update_positions()
                account = trader.db.get_account()
                print(f"\n  账户更新完成:")
                print(f"  持仓市值: ¥{account['market_value']:.2f}")
                print(f"  总资产: ¥{account['total_asset']:.2f}")
                print(f"  收益率: {account['total_profit_rate']:.2f}%")
            
            # 等待60秒
            await asyncio.sleep(60)
            
        except KeyboardInterrupt:
            print("\n停止价格更新任务")
            break
        except Exception as e:
            print(f"\n❌ 价格更新任务出错: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(update_prices_periodically())
