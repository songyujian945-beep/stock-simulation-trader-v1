#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《三只小猪》3分钟完整版
按照脚本制作，尽量丰富细节
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy import *
import asyncio
import random

output_dir = "/Users/syj/.openclaw/workspace/video_output"
os.makedirs(output_dir, exist_ok=True)

WIDTH, HEIGHT = 1920, 1080  # 横屏（更适合动画）
FPS = 24

# 脚本内容
scenes = [
    {
        'id': 1,
        'duration': 20,
        'text': '很久很久以前，在一片开满鲜花的春日森林里，住着猪妈妈和她的三个宝贝儿子。森林里溪水叮咚，鸟语花香，每一棵大树都披着嫩绿的新叶，温柔的春风吹得野花轻轻摇晃。',
        'type': 'intro'
    },
    {
        'id': 2,
        'duration': 25,
        'text': '猪妈妈温柔地说："孩子们，你们长大了，要离开妈妈，自己盖房子生活啦，一定要小心森林里的大灰狼！"三只小猪点点头，蹦蹦跳跳地告别妈妈，走进了森林深处。',
        'type': 'mother'
    },
    {
        'id': 3,
        'duration': 30,
        'text': '老大灰灰最偷懒，他觉得盖房子太麻烦，随手捡了一堆干枯的干草，在空旷的草地上搭了一间草房子。风一吹，草房子就摇摇晃晃，可他却觉得又快又省力。',
        'type': 'straw'
    },
    {
        'id': 4,
        'duration': 30,
        'text': '老二白白比老大勤快一点，他捡来森林里的细树枝和小木头，在小树林里盖了一间木房子。木房子看起来比草房坚固，可木头之间的缝隙，连小松鼠都能钻进去。',
        'type': 'wood'
    },
    {
        'id': 5,
        'duration': 30,
        'text': '老三花花最聪明也最勤劳，他来到河边的石滩，搬来结实的红砖头和黄泥，一块一块认真砌墙。他盖的砖房子方方正正、坚固厚实，风吹不倒，雨打不烂。',
        'type': 'brick'
    },
    {
        'id': 6,
        'duration': 20,
        'text': '忽然，狂风大作，乌云密布，凶狠的大灰狼从森林里冲了出来！他对着草房子轻轻一吹，干草瞬间飞散；又对着木房子用力一吹，树枝木头散落一地！',
        'type': 'blow'
    },
    {
        'id': 7,
        'duration': 15,
        'text': '两只小猪拼命逃到老三的砖房子里，大灰狼用尽全身力气吹啊撞啊，可结实的砖房子纹丝不动！大灰狼没办法，只能灰溜溜地逃走了。',
        'type': 'escape'
    },
    {
        'id': 8,
        'duration': 10,
        'text': '从此，三只小猪在结实的砖房子里，开开心心地生活在一起，再也不怕大灰狼啦！',
        'type': 'ending'
    }
]

def create_background(scene_type):
    """创建场景背景"""
    img = Image.new('RGB', (WIDTH, HEIGHT), (135, 206, 250))
    draw = ImageDraw.Draw(img)
    
    # 天空渐变
    for y in range(HEIGHT // 2):
        ratio = y / (HEIGHT // 2)
        r = int(135 + (176 - 135) * ratio)
        g = int(206 + (224 - 206) * ratio)
        b = int(250 + (230 - 250) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    # 根据场景添加环境
    if scene_type == 'intro':
        # 森林清晨 - 薄雾、阳光、树木
        draw_forest(draw, morning=True)
    elif scene_type == 'mother':
        # 小木屋
        draw_cabin(draw)
    elif scene_type in ['straw', 'wood', 'brick']:
        # 草地/森林/河边
        if scene_type == 'straw':
            draw_meadow(draw)
        elif scene_type == 'wood':
            draw_woods(draw)
        else:
            draw_river(draw)
    elif scene_type == 'blow':
        # 乌云密布
        draw_storm(draw)
    elif scene_type == 'escape':
        # 砖房前
        draw_brick_house_env(draw)
    else:
        # 温暖结局
        draw_happy_scene(draw)
    
    return img

def draw_forest(draw, morning=True):
    """画森林"""
    # 地面
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(34, 139, 34))
    
    # 树木
    for x in range(100, WIDTH-100, 200):
        draw_tree(draw, x, HEIGHT*2//3, scale=1.2)
    
    # 雾气效果（简化）
    for i in range(3):
        y = 300 + i * 50
        draw.rectangle([0, y, WIDTH, y+30], fill=(255, 255, 255, 50))
    
    # 太阳
    if morning:
        draw_sun(draw, WIDTH-150, 100, 70)

def draw_cabin(draw):
    """画小木屋"""
    # 地面
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(34, 139, 34))
    
    # 木屋
    x, y = WIDTH//2, HEIGHT//2
    draw.rectangle([x-200, y-100, x+200, y+100], fill=(139, 90, 43), outline=(0,0,0), width=4)
    draw.polygon([(x-220, y-100), (x, y-250), (x+220, y-100)], fill=(101, 67, 33))
    draw.rectangle([x-50, y+20, x+50, y+100], fill=(101, 67, 33))
    
    # 挂着的玉米和辣椒
    draw.ellipse([x-180, y-80, x-160, y-50], fill=(255, 215, 0))
    draw.ellipse([x+160, y-80, x+180, y-50], fill=(255, 0, 0))
    
    # 树木
    draw_tree(draw, 150, HEIGHT*2//3, 0.9)
    draw_tree(draw, WIDTH-150, HEIGHT*2//3, 0.9)

def draw_meadow(draw):
    """画草地"""
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(124, 252, 0))
    # 枯草堆
    for x in range(200, WIDTH-200, 150):
        draw.ellipse([x-40, HEIGHT//2, x+40, HEIGHT//2+80], fill=(218, 165, 32))

def draw_woods(draw):
    """画树林"""
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(34, 139, 34))
    for x in range(100, WIDTH, 180):
        draw_tree(draw, x, HEIGHT*2//3, 0.7)

def draw_river(draw):
    """画河边"""
    # 草地
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(34, 139, 34))
    # 河流
    draw.rectangle([0, HEIGHT*3//4, WIDTH, HEIGHT], fill=(65, 105, 225))
    # 石滩
    for i in range(10):
        x = random.randint(100, WIDTH-100)
        y = HEIGHT*3//4 + random.randint(-20, 20)
        r = random.randint(10, 30)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(128, 128, 128))

def draw_storm(draw):
    """画暴风雨"""
    # 灰暗天空
    for y in range(HEIGHT // 2):
        ratio = y / (HEIGHT // 2)
        r = int(70 + (90 - 70) * ratio)
        g = int(70 + (90 - 70) * ratio)
        b = int(80 + (100 - 80) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    # 乌云
    for i in range(5):
        x = 200 + i * 300
        draw.ellipse([x-100, 50, x+100, 150], fill=(50, 50, 60))
    
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(25, 50, 25))

def draw_brick_house_env(draw):
    """砖房环境"""
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(34, 139, 34))
    draw_sun(draw, WIDTH-150, 100, 60)

def draw_happy_scene(draw):
    """欢乐场景"""
    # 蓝天
    for y in range(HEIGHT // 2):
        ratio = y / (HEIGHT // 2)
        r = int(135 + (176 - 135) * ratio)
        g = int(206 + (224 - 206) * ratio)
        b = int(250 + (230 - 250) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=(124, 252, 0))
    
    # 花朵
    random.seed(42)
    for _ in range(30):
        x = random.randint(50, WIDTH-50)
        y = random.randint(HEIGHT*2//3+20, HEIGHT-50)
        color = random.choice([(255, 0, 0), (255, 255, 0), (255, 0, 255)])
        draw.ellipse([x-8, y-8, x+8, y+8], fill=color)
    
    # 彩虹
    colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255)]
    for i, c in enumerate(colors):
        draw.arc([100, 50, WIDTH-100, 400], 180, 360, fill=c, width=20)

def draw_sun(draw, x, y, r):
    """画太阳"""
    # 光芒
    for i in range(12):
        angle = i * 30 * math.pi / 180
        x1 = x + int((r + 15) * math.cos(angle))
        y1 = y + int((r + 15) * math.sin(angle))
        x2 = x + int((r + 40) * math.cos(angle))
        y2 = y + int((r + 40) * math.sin(angle))
        draw.line([x1, y1, x2, y2], fill=(255, 223, 0), width=5)
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 223, 0))

def draw_tree(draw, x, y, scale=1):
    """画树"""
    w = int(25 * scale)
    h = int(100 * scale)
    draw.rectangle([x-w, y, x+w, y+h], fill=(139, 69, 19))
    
    # 树冠
    for dy, r in [(0, 60), (-30, 50), (-60, 40)]:
        r = int(r * scale)
        draw.ellipse([x-r, y+int(dy*scale)-r, x+r, y+int(dy*scale)+r], fill=(34, 139, 34))

def draw_characters(draw, scene_type):
    """画角色"""
    if scene_type == 'intro':
        # 猪妈妈 + 三只小猪
        draw_pig(draw, WIDTH//2, HEIGHT//2+100, 1.2, 'mother')
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2+250, 0.7, ['gray', 'white', 'smart'][i])
    
    elif scene_type == 'mother':
        draw_pig(draw, WIDTH//2, HEIGHT//2+100, 1.2, 'mother')
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2+250, 0.7, ['gray', 'white', 'smart'][i])
    
    elif scene_type == 'straw':
        # 老大 + 草房
        draw_straw_house(draw, WIDTH//2, HEIGHT//2)
        draw_pig(draw, WIDTH//2, HEIGHT//2+250, 0.8, 'gray')
    
    elif scene_type == 'wood':
        draw_wood_house(draw, WIDTH//2, HEIGHT//2)
        draw_pig(draw, WIDTH//2, HEIGHT//2+250, 0.8, 'white')
    
    elif scene_type == 'brick':
        draw_brick_house(draw, WIDTH//2, HEIGHT//2)
        draw_pig(draw, WIDTH//2, HEIGHT//2+250, 0.8, 'smart')
    
    elif scene_type == 'blow':
        draw_wolf(draw, WIDTH//4, HEIGHT//2+150, 1.3, angry=True)
        # 倒塌的房子
        draw_destroyed_house(draw, WIDTH//2, HEIGHT//2, 'straw')
        draw_destroyed_house(draw, 3*WIDTH//4, HEIGHT//2, 'wood')
        # 飞散效果
        for i in range(20):
            x = random.randint(100, WIDTH-100)
            y = random.randint(HEIGHT//4, HEIGHT//2)
            size = random.randint(5, 15)
            color = random.choice([(218, 165, 32), (139, 90, 43)])
            draw.rectangle([x, y, x+size, y+size//2], fill=color)
    
    elif scene_type == 'escape':
        draw_brick_house(draw, WIDTH//2, HEIGHT//2)
        # 三只小猪在房子里
        for i, x in enumerate([WIDTH//2-80, WIDTH//2, WIDTH//2+80]):
            draw_pig(draw, x, HEIGHT//2+50, 0.5, ['gray', 'white', 'smart'][i], in_house=True)
        draw_wolf(draw, WIDTH//4, HEIGHT//2+200, 1.0, angry=True, tired=True)
    
    else:  # ending
        draw_brick_house(draw, WIDTH//2, HEIGHT//2-50)
        # 三只快乐的小猪
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2+200, 0.8, ['gray', 'white', 'smart'][i], happy=True)
        # 猪妈妈
        draw_pig(draw, WIDTH//2, HEIGHT//2+350, 1.0, 'mother', happy=True)

def draw_pig(draw, x, y, scale=1, pig_type='normal', in_house=False, happy=False):
    """画小猪"""
    x, y = int(x), int(y)
    scale = float(scale)
    
    # 身体
    r = int(60 * scale)
    body_color = {
        'gray': (180, 180, 180),
        'white': (255, 255, 255),
        'smart': (255, 182, 193),
        'mother': (255, 192, 203),
        'normal': (255, 182, 193)
    }.get(pig_type, (255, 182, 193))
    
    draw.ellipse([x-r, y-r//2, x+r, y+r//2], fill=body_color, outline=(0,0,0), width=2)
    
    # 头
    head_r = int(45 * scale)
    draw.ellipse([x-head_r, y-head_r, x+head_r, y+head_r], fill=body_color, outline=(0,0,0), width=2)
    
    # 耳朵
    for dx in [-1, 1]:
        ear_x = x + int(dx * 25 * scale)
        draw.ellipse([ear_x-10, y-int(40*scale), ear_x+10, y-int(20*scale)], 
                    fill=body_color, outline=(0,0,0), width=1)
    
    # 眼睛
    for dx in [-1, 1]:
        ex = x + int(dx * 12 * scale)
        draw.ellipse([ex-8, y-15, ex+8, y+5], fill=(255, 255, 255))
        if happy:
            # 开心的弯眼
            draw.arc([ex-6, y-12, ex+6, y], 0, 180, fill=(0,0,0), width=2)
        else:
            draw.ellipse([ex-4, y-10, ex+4, y], fill=(0, 0, 0))
    
    # 鼻子
    draw.ellipse([x-12, y+8, x+12, y+25], fill=(255, 150, 160))
    draw.ellipse([x-6, y+12, x-2, y+18], fill=(0,0,0))
    draw.ellipse([x+2, y+12, x+6, y+18], fill=(0,0,0))
    
    # 特征
    if pig_type == 'smart':
        # 小帽子
        draw.polygon([(x-15, y-40), (x, y-60), (x+15, y-40)], fill=(0, 100, 255))
    
    if happy:
        # 笑容
        draw.arc([x-15, y+25, x+15, y+40], 0, 180, fill=(0,0,0), width=2)

def draw_wolf(draw, x, y, scale=1, angry=False, tired=False):
    """画大灰狼"""
    x, y = int(x), int(y)
    scale = float(scale)
    
    # 身体
    r = int(70 * scale)
    draw.ellipse([x-r, y-r//2, x+r, y+r//2], fill=(105, 105, 105), outline=(0,0,0), width=3)
    
    # 头
    head_r = int(55 * scale)
    draw.ellipse([x-head_r, y-head_r, x+head_r, y+head_r//2], fill=(105, 105, 105), outline=(0,0,0), width=3)
    
    # 尖耳朵
    for dx in [-1, 1]:
        points = [
            (x + int(dx * 35 * scale), y - int(25 * scale)),
            (x + int(dx * 50 * scale), y - int(70 * scale)),
            (x + int(dx * 15 * scale), y - int(40 * scale))
        ]
        draw.polygon(points, fill=(105, 105, 105), outline=(0,0,0), width=2)
    
    # 眼睛
    eye_color = (255, 0, 0) if angry else (0, 100, 0)
    for dx in [-1, 1]:
        ex = x + int(dx * 20 * scale)
        draw.ellipse([ex-10, y-20, ex+10, y], fill=(255, 255, 255))
        if tired:
            # 累的眼睛（X形）
            draw.line([ex-5, y-15, ex+5, y-5], fill=(0,0,0), width=2)
            draw.line([ex-5, y-5, ex+5, y-15], fill=(0,0,0), width=2)
        else:
            draw.ellipse([ex-5, y-15, ex+5, y-5], fill=eye_color)
    
    # 鼻子
    draw.ellipse([x-10, y+5, x+10, y+18], fill=(0, 0, 0))
    
    # 嘴
    if angry:
        draw.polygon([(x-25, y+25), (x, y+45), (x+25, y+25)], fill=(0,0,0))
        for dx in range(-15, 20, 8):
            draw.polygon([(x+dx-2, y+25), (x+dx, y+35), (x+dx+2, y+25)], fill=(255,255,255))
    else:
        draw.arc([x-20, y+15, x+20, y+35], 0, 180, fill=(0,0,0), width=2)
    
    # 尾巴
    tail_x = x - int(70 * scale)
    for i in range(6):
        offset = int(math.sin(i * 0.7) * 12)
        draw.ellipse([tail_x-offset-6, y-i*5-6, tail_x-offset+6, y-i*5+6], fill=(105, 105, 105))

def draw_straw_house(draw, x, y):
    """画草房"""
    x, y = int(x), int(y)
    # 房身
    draw.rectangle([x-120, y-80, x+120, y+80], fill=(218, 165, 32), outline=(0,0,0), width=3)
    # 屋顶
    draw.polygon([(x-140, y-80), (x, y-200), (x+140, y-80)], fill=(184, 134, 11), outline=(0,0,0), width=2)
    # 门
    draw.rectangle([x-30, y+10, x+30, y+80], fill=(139, 90, 43))
    # 稻草纹理
    for i in range(-100, 101, 20):
        draw.line([(x+i, y-80), (x+i, y+80)], fill=(184, 134, 11), width=1)

def draw_wood_house(draw, x, y):
    """画木房"""
    x, y = int(x), int(y)
    draw.rectangle([x-130, y-90, x+130, y+90], fill=(139, 90, 43), outline=(0,0,0), width=4)
    draw.polygon([(x-150, y-90), (x, y-220), (x+150, y-90)], fill=(101, 67, 33), outline=(0,0,0), width=3)
    draw.rectangle([x-35, y+15, x+35, y+90], fill=(101, 67, 33))
    # 木纹
    for i in range(-100, 101, 25):
        draw.line([(x+i, y-90), (x+i, y+90)], fill=(101, 67, 33), width=2)
    # 窗户
    draw.rectangle([x+70, y-50, x+110, y-10], fill=(200, 230, 255), outline=(0,0,0), width=2)

def draw_brick_house(draw, x, y):
    """画砖房"""
    x, y = int(x), int(y)
    # 房身
    draw.rectangle([x-150, y-100, x+150, y+100], fill=(178, 34, 34), outline=(0,0,0), width=5)
    # 屋顶
    draw.polygon([(x-170, y-100), (x, y-250), (x+170, y-100)], fill=(139, 69, 19), outline=(0,0,0), width=3)
    # 门
    draw.rectangle([x-45, y+20, x+45, y+100], fill=(101, 67, 33), outline=(0,0,0), width=3)
    draw.ellipse([x+25, y+50, x+40, y+65], fill=(255, 215, 0))
    # 窗户
    for dx in [-90, 90]:
        draw.rectangle([x+dx-35, y-60, x+dx+35, y], fill=(200, 230, 255), outline=(0,0,0), width=3)
        draw.line([(x+dx, y-60), (x+dx, y)], fill=(0,0,0), width=2)
        draw.line([(x+dx-35, y-30), (x+dx+35, y-30)], fill=(0,0,0), width=2)
    # 砖纹
    for i in range(-80, 81, 20):
        draw.line([(x+i, y-100), (x+i, y+100)], fill=(139, 26, 26), width=1)
    # 烟囱
    draw.rectangle([x+80, y-180, x+120, y-100], fill=(139, 69, 19), outline=(0,0,0), width=2)

def draw_destroyed_house(draw, x, y, house_type):
    """画倒塌的房子"""
    x, y = int(x), int(y)
    color = (218, 165, 32) if house_type == 'straw' else (139, 90, 43)
    
    random.seed(hash(house_type))
    for _ in range(8):
        rx = x + random.randint(-80, 80)
        ry = y + random.randint(-50, 50)
        rw = random.randint(20, 50)
        rh = random.randint(15, 35)
        draw.rectangle([rx, ry, rx+rw, ry+rh], fill=color, outline=(0,0,0), width=2)

async def generate_audio(text, output_file, duration):
    """生成语音"""
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural", rate='-10%')
    await communicate.save(output_file)

def create_subtitle(text, duration):
    """创建字幕"""
    txt_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    except:
        font = ImageFont.load_default()
    
    # 文字换行
    words = text
    lines = []
    if len(words) > 25:
        lines = [words[:25], words[25:]]
    else:
        lines = [words]
    
    y_offset = HEIGHT - 150
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        
        # 背景
        draw.rectangle([x-15, y_offset-10, x+tw+15, y_offset+50], fill=(0, 0, 0, 180))
        
        # 文字
        draw.text((x, y_offset), line, font=font, fill=(255, 255, 255))
        y_offset += 60
    
    txt_path = f"{output_dir}/subtitle_{hash(text)}.png"
    txt_img.save(txt_path)
    
    return ImageClip(txt_path).with_duration(duration)

def main():
    print("🎬 开始制作3分钟完整版...")
    print("=" * 60)
    
    clips = []
    total_duration = 0
    
    for i, scene in enumerate(scenes):
        print(f"\n📹 场景 {scene['id']}/{len(scenes)}: {scene['text'][:30]}...")
        
        # 1. 创建背景
        bg = create_background(scene['type'])
        
        # 2. 添加角色
        draw = ImageDraw.Draw(bg)
        draw_characters(draw, scene['type'])
        
        # 3. 保存图片
        img_path = f"{output_dir}/scene_3min_{i}.png"
        bg.save(img_path)
        
        # 4. 生成语音
        audio_path = f"{output_dir}/audio_3min_{i}.mp3"
        asyncio.run(generate_audio(scene['text'], audio_path, scene['duration']))
        
        # 5. 获取实际音频时长
        audio = AudioFileClip(audio_path)
        actual_duration = audio.duration + 0.5
        
        # 6. 创建视频片段
        video = ImageClip(img_path).with_duration(actual_duration)
        
        # 7. 添加字幕
        subtitle = create_subtitle(scene['text'], actual_duration)
        
        # 8. 合成
        final = CompositeVideoClip([video, subtitle]).with_audio(audio)
        clips.append(final)
        
        total_duration += actual_duration
        print(f"   ✅ 场景 {scene['id']} 完成 ({actual_duration:.1f}秒)")
    
    print("\n" + "=" * 60)
    print("拼接所有场景...")
    
    # 合并
    result = concatenate_videoclips(clips, method="compose")
    
    # 输出
    output = f"{output_dir}/three_pigs_3min.mp4"
    print(f"\n💾 渲染最终视频: {output}")
    print(f"预计总时长: {total_duration:.1f}秒 (约{total_duration/60:.1f}分钟)")
    print("渲染中，请稍候...")
    
    result.write_videofile(
        output,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        bitrate='8000k',
        preset='medium',
        logger=None
    )
    
    # 清理
    result.close()
    for c in clips:
        c.close()
    
    print("\n" + "=" * 60)
    print("✅ 3分钟完整版制作完成！")
    print(f"📍 文件位置: {output}")
    print(f"⏱️  总时长: {total_duration:.1f} 秒")
    print(f"📐 分辨率: {WIDTH}x{HEIGHT}")
    print(f"🎨 场景数: {len(scenes)} 个")
    print("=" * 60)

if __name__ == "__main__":
    main()
