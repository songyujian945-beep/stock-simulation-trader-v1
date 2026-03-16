#!/usr/bin/env python3
"""生成小红书配图"""

from PIL import Image, ImageDraw, ImageFont
import os

# 创建图片
width, height = 1080, 1920
img = Image.new('RGB', (width, height), color='#1a1a2e')
draw = ImageDraw.Draw(img)

# 颜色
colors = {
    'title': '#ffffff',
    'profit': '#00ff88',
    'loss': '#ff4757',
    'text': '#e0e0e0',
    'accent': '#7c3aed'
}

# 绘制渐变背景
for y in range(height):
    r = int(26 + (y / height) * 20)
    g = int(26 + (y / height) * 10)
    b = int(46 + (y / height) * 30)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

try:
    # 尝试加载字体
    font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
    font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
    font_normal = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
except:
    font_title = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_normal = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 绘制内容
y_offset = 100

# 标题
title = "📊 实盘记录 Day 3"
bbox = draw.textbbox((0, 0), title, font=font_title)
title_width = bbox[2] - bbox[0]
draw.text(((width - title_width) / 2, y_offset), title, fill=colors['title'], font=font_title)
y_offset += 120

# 分割线
draw.line([(100, y_offset), (width - 100, y_offset)], fill=colors['accent'], width=3)
y_offset += 50

# 数据卡片
def draw_card(y, title, value, color):
    # 背景
    draw.rounded_rectangle([(80, y), (width - 80, y + 100)], radius=15, fill='#2a2a4a')
    # 标题
    draw.text((100, y + 15), title, fill=colors['text'], font=font_normal)
    # 数值
    draw.text((100, y + 55), value, fill=color, font=font_large)

draw_card(y_offset, "初始资金", "¥50,000", colors['text'])
y_offset += 130

draw_card(y_offset, "当前资产", "¥52,907", colors['profit'])
y_offset += 130

draw_card(y_offset, "总收益", "+¥2,907 (+5.81%)", colors['profit'])
y_offset += 130

# 分割线
y_offset += 30
draw.line([(100, y_offset), (width - 100, y_offset)], fill=colors['accent'], width=2)
y_offset += 50

# 今日操作
draw.text((100, y_offset), "✅ 今日操作", fill=colors['title'], font=font_large)
y_offset += 80

draw.text((100, y_offset), "卖出浪潮信息 100股 @ ¥63.30", fill=colors['text'], font=font_normal)
y_offset += 60

draw.text((100, y_offset), "成本: ¥34.23  →  盈利: +84.9%", fill=colors['profit'], font=font_normal)
y_offset += 100

# 策略说明
draw.text((100, y_offset), "💡 我的策略", fill=colors['title'], font=font_large)
y_offset += 80

strategies = [
    "止盈: +5% 卖出",
    "止损: -3% 割肉",
    "持仓: 最多3天",
    "仓位: 单只≤20%"
]

for s in strategies:
    draw.text((120, y_offset), f"• {s}", fill=colors['text'], font=font_normal)
    y_offset += 50

# 底部金句
y_offset = height - 200
draw.text((100, y_offset), "💰 炒股最怕的就是贪", fill=colors['accent'], font=font_large)
y_offset += 60
draw.text((100, y_offset), "赚到手里的才是真钱", fill=colors['text'], font=font_normal)

# 保存
output_path = os.path.expanduser('~/.openclaw/workspace/video_training/output/xiaohongshu_post.png')
img.save(output_path, quality=95)
print(f"✅ 图片已保存: {output_path}")
