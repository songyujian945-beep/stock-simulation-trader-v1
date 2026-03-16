#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《三只小猪》最终版 - 优化性能
"""

import os
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy import *
import asyncio

output_dir = "/Users/syj/.openclaw/workspace/video_output"
os.makedirs(output_dir, exist_ok=True)

WIDTH, HEIGHT = 1920, 1080
FPS = 24

# 精简的场景
scenes = [
    {'id': 1, 'text': '很久以前，在美丽的春日森林里，住着猪妈妈和她的三个宝贝儿子。', 'type': 'intro'},
    {'id': 2, 'text': '猪妈妈说："孩子们，你们长大了，要自己盖房子生活啦，小心大灰狼！"', 'type': 'mother'},
    {'id': 3, 'text': '老大最懒，用干草搭了一间草房子，风一吹就摇晃。', 'type': 'straw'},
    {'id': 4, 'text': '老二用木头盖了一间木房子，木板缝隙很大。', 'type': 'wood'},
    {'id': 5, 'text': '老三最勤劳，用红砖和黄泥盖了坚固的砖房子。', 'type': 'brick'},
    {'id': 6, 'text': '突然，大灰狼来了！它吹倒了草房，又吹倒了木房！', 'type': 'blow'},
    {'id': 7, 'text': '但砖房子怎么也吹不倒，大灰狼只能灰溜溜地逃走。', 'type': 'escape'},
    {'id': 8, 'text': '从此，三只小猪幸福地生活在一起，再也不怕大灰狼啦！', 'type': 'ending'},
]

def draw_scene(scene_type):
    """绘制场景"""
    # 基础背景
    if scene_type in ['blow']:
        # 暴风雨
        bg_color = (100, 100, 110)
    else:
        # 蓝天
        bg_color = (135, 206, 250)
    
    img = Image.new('RGB', (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 地面
    ground_color = (34, 139, 34) if scene_type != 'blow' else (25, 60, 25)
    draw.rectangle([0, HEIGHT*2//3, WIDTH, HEIGHT], fill=ground_color)
    
    # 太阳（非暴风雨场景）
    if scene_type not in ['blow']:
        draw.ellipse([WIDTH-180, 80, WIDTH-80, 180], fill=(255, 223, 0))
    
    # 简单树木
    if scene_type in ['intro', 'mother']:
        for x in [150, WIDTH-150]:
            # 树干
            draw.rectangle([x-15, HEIGHT*2//3, x+15, HEIGHT*2//3+80], fill=(139, 69, 19))
            # 树冠
            draw.ellipse([x-50, HEIGHT*2//3-80, x+50, HEIGHT*2//3], fill=(34, 139, 34))
    
    # 根据场景类型绘制特定内容
    if scene_type == 'intro':
        # 三只小猪
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2+150, 0.8)
    
    elif scene_type == 'mother':
        # 木屋
        draw_cabin(draw, WIDTH//2, HEIGHT//2-50)
        # 小猪
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2+200, 0.7)
    
    elif scene_type == 'straw':
        draw_straw_house(draw, WIDTH//2, HEIGHT//2-30)
        draw_pig(draw, WIDTH//2, HEIGHT//2+220, 0.8)
    
    elif scene_type == 'wood':
        draw_wood_house(draw, WIDTH//2, HEIGHT//2-30)
        draw_pig(draw, WIDTH//2, HEIGHT//2+220, 0.8)
    
    elif scene_type == 'brick':
        draw_brick_house(draw, WIDTH//2, HEIGHT//2-30)
        draw_pig(draw, WIDTH//2, HEIGHT//2+220, 0.8)
    
    elif scene_type == 'blow':
        # 倒塌的房子
        draw_destroyed(draw, WIDTH//3, HEIGHT//2, (218, 165, 32))
        draw_destroyed(draw, 2*WIDTH//3, HEIGHT//2, (139, 90, 43))
        # 大灰狼
        draw_wolf(draw, WIDTH//4, HEIGHT//2+150, angry=True)
    
    elif scene_type == 'escape':
        draw_brick_house(draw, WIDTH//2, HEIGHT//2-50)
        # 三只小猪
        for i, x in enumerate([WIDTH//2-80, WIDTH//2, WIDTH//2+80]):
            draw_pig(draw, x, HEIGHT//2+50, 0.6)
        # 累趴的狼
        draw_wolf(draw, WIDTH//4, HEIGHT//2+220, angry=False, tired=True)
    
    else:  # ending
        draw_brick_house(draw, WIDTH//2, HEIGHT//2-80)
        # 快乐的小猪
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2+180, 0.8)
        # 彩虹
        colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255)]
        for i, c in enumerate(colors):
            draw.arc([150, 50, WIDTH-150, 350], 180, 360, fill=c, width=15)
    
    return img

def draw_pig(draw, x, y, scale=1):
    """画小猪"""
    x, y, scale = int(x), int(y), float(scale)
    r = int(50 * scale)
    
    # 身体
    draw.ellipse([x-r, y-r//2, x+r, y+r//2], fill=(255, 182, 193), outline=(0,0,0), width=2)
    # 头
    hr = int(40 * scale)
    draw.ellipse([x-hr, y-hr, x+hr, y+hr], fill=(255, 182, 193), outline=(0,0,0), width=2)
    # 耳朵
    for dx in [-1, 1]:
        ex = x + int(dx * 25 * scale)
        draw.ellipse([ex-8, y-int(35*scale), ex+8, y-int(20*scale)], fill=(255, 182, 193))
    # 眼睛
    for dx in [-1, 1]:
        ex = x + int(dx * 12 * scale)
        draw.ellipse([ex-6, y-12, ex+6, y], fill=(255, 255, 255))
        draw.ellipse([ex-3, y-9, ex+3, y-3], fill=(0, 0, 0))
    # 鼻子
    draw.ellipse([x-10, y+5, x+10, y+18], fill=(255, 150, 160))
    draw.ellipse([x-5, y+9, x-2, y+14], fill=(0,0,0))
    draw.ellipse([x+2, y+9, x+5, y+14], fill=(0,0,0))

def draw_wolf(draw, x, y, angry=True, tired=False):
    """画大灰狼"""
    x, y = int(x), int(y)
    r = 60
    
    # 身体
    draw.ellipse([x-r, y-r//2, x+r, y+r//2], fill=(105, 105, 105), outline=(0,0,0), width=3)
    # 头
    draw.ellipse([x-50, y-50, x+50, y+30], fill=(105, 105, 105), outline=(0,0,0), width=3)
    # 尖耳朵
    draw.polygon([(x-35, y-25), (x-50, y-65), (x-15, y-35)], fill=(105, 105, 105), outline=(0,0,0))
    draw.polygon([(x+35, y-25), (x+50, y-65), (x+15, y-35)], fill=(105, 105, 105), outline=(0,0,0))
    # 眼睛
    for dx in [-1, 1]:
        ex = x + dx * 20
        draw.ellipse([ex-8, y-18, ex+8, y], fill=(255, 255, 255))
        if tired:
            # X眼睛
            draw.line([ex-4, y-14, ex+4, y-4], fill=(0,0,0), width=2)
            draw.line([ex-4, y-4, ex+4, y-14], fill=(0,0,0), width=2)
        else:
            color = (255, 0, 0) if angry else (0, 100, 0)
            draw.ellipse([ex-4, y-14, ex+4, y-6], fill=color)
    # 鼻子
    draw.ellipse([x-8, y+5, x+8, y+15], fill=(0, 0, 0))
    # 嘴
    if angry:
        draw.polygon([(x-20, y+20), (x, y+35), (x+20, y+20)], fill=(0,0,0))

def draw_cabin(draw, x, y):
    """画木屋"""
    x, y = int(x), int(y)
    draw.rectangle([x-120, y-60, x+120, y+60], fill=(139, 90, 43), outline=(0,0,0), width=3)
    draw.polygon([(x-140, y-60), (x, y-150), (x+140, y-60)], fill=(101, 67, 33))
    draw.rectangle([x-30, y+15, x+30, y+60], fill=(101, 67, 33))
    # 挂物
    draw.ellipse([x-100, y-40, x-85, y-25], fill=(255, 215, 0))
    draw.ellipse([x+85, y-40, x+100, y-25], fill=(255, 0, 0))

def draw_straw_house(draw, x, y):
    """画草房"""
    x, y = int(x), int(y)
    draw.rectangle([x-100, y-60, x+100, y+60], fill=(218, 165, 32), outline=(0,0,0), width=3)
    draw.polygon([(x-120, y-60), (x, y-160), (x+120, y-60)], fill=(184, 134, 11))
    draw.rectangle([x-25, y+10, x+25, y+60], fill=(139, 90, 43))
    # 稻草纹理
    for i in range(-80, 81, 15):
        draw.line([(x+i, y-60), (x+i, y+60)], fill=(184, 134, 11), width=1)

def draw_wood_house(draw, x, y):
    """画木房"""
    x, y = int(x), int(y)
    draw.rectangle([x-110, y-70, x+110, y+70], fill=(139, 90, 43), outline=(0,0,0), width=4)
    draw.polygon([(x-130, y-70), (x, y-170), (x+130, y-70)], fill=(101, 67, 33))
    draw.rectangle([x-30, y+15, x+30, y+70], fill=(101, 67, 33))
    # 木纹
    for i in range(-80, 81, 20):
        draw.line([(x+i, y-70), (x+i, y+70)], fill=(101, 67, 33), width=2)
    # 窗户
    draw.rectangle([x+60, y-40, x+95, y-5], fill=(200, 230, 255), outline=(0,0,0), width=2)

def draw_brick_house(draw, x, y):
    """画砖房"""
    x, y = int(x), int(y)
    draw.rectangle([x-130, y-80, x+130, y+80], fill=(178, 34, 34), outline=(0,0,0), width=4)
    draw.polygon([(x-150, y-80), (x, y-200), (x+150, y-80)], fill=(139, 69, 19))
    draw.rectangle([x-40, y+20, x+40, y+80], fill=(101, 67, 33), outline=(0,0,0), width=2)
    draw.ellipse([x+25, y+45, x+35, y+55], fill=(255, 215, 0))
    # 窗户
    for dx in [-75, 75]:
        draw.rectangle([x+dx-30, y-50, x+dx+30, y], fill=(200, 230, 255), outline=(0,0,0), width=3)
        draw.line([(x+dx, y-50), (x+dx, y)], fill=(0,0,0), width=2)
        draw.line([(x+dx-30, y-25), (x+dx+30, y-25)], fill=(0,0,0), width=2)
    # 砖纹
    for i in range(-60, 61, 15):
        draw.line([(x+i, y-80), (x+i, y+80)], fill=(139, 26, 26), width=1)
    # 烟囱
    draw.rectangle([x+70, y-150, x+100, y-80], fill=(139, 69, 19))

def draw_destroyed(draw, x, y, color):
    """画倒塌的房子"""
    x, y = int(x), int(y)
    import random
    random.seed(hash(color))
    for _ in range(6):
        rx = x + random.randint(-60, 60)
        ry = y + random.randint(-40, 40)
        rw = random.randint(20, 45)
        rh = random.randint(15, 30)
        draw.rectangle([rx, ry, rx+rw, ry+rh], fill=color, outline=(0,0,0), width=2)

async def gen_audio(text, path):
    """生成语音"""
    comm = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await comm.save(path)

def main():
    print("🎬 开始制作《三只小猪》最终版...")
    print("=" * 60)
    
    clips = []
    
    for i, scene in enumerate(scenes):
        print(f"\n📹 场景 {scene['id']}/{len(scenes)}: {scene['text'][:25]}...")
        
        # 1. 绘制场景
        img = draw_scene(scene['type'])
        img_path = f"{output_dir}/scene_final_{i}.png"
        img.save(img_path, optimize=True)
        
        # 2. 生成语音
        audio_path = f"{output_dir}/audio_final_{i}.mp3"
        asyncio.run(gen_audio(scene['text'], audio_path))
        
        # 3. 获取音频时长
        audio = AudioFileClip(audio_path)
        duration = audio.duration + 0.5
        
        # 4. 创建视频片段
        video = ImageClip(img_path).with_duration(duration)
        
        # 5. 添加字幕
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
        except:
            font = ImageFont.load_default()
        
        txt_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        
        # 处理长文本
        text = scene['text']
        lines = [text[k:k+28] for k in range(0, len(text), 28)]
        
        y_pos = HEIGHT - 120 - len(lines) * 45
        for line in lines:
            bbox = txt_draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (WIDTH - tw) // 2
            txt_draw.rectangle([x-12, y_pos-8, x+tw+12, y_pos+42], fill=(0, 0, 0, 200))
            txt_draw.text((x, y_pos), line, font=font, fill=(255, 255, 255))
            y_pos += 50
        
        txt_path = f"{output_dir}/txt_final_{i}.png"
        txt_img.save(txt_path)
        subtitle = ImageClip(txt_path).with_duration(duration)
        
        # 6. 合成
        final_clip = CompositeVideoClip([video, subtitle]).with_audio(audio)
        clips.append(final_clip)
        
        print(f"   ✅ 完成 ({duration:.1f}秒)")
    
    # 合并
    print("\n" + "=" * 60)
    print("拼接所有场景...")
    result = concatenate_videoclips(clips, method="compose")
    
    output = f"{output_dir}/three_pigs_final.mp4"
    print(f"💾 渲染视频: {output}")
    
    result.write_videofile(
        output,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        bitrate='6000k',
        preset='fast',
        logger=None
    )
    
    result.close()
    for c in clips:
        c.close()
    
    total = sum([c.duration for c in clips])
    print("\n" + "=" * 60)
    print("✅ 制作完成！")
    print(f"📍 位置: {output}")
    print(f"⏱️  时长: {total:.1f}秒 ({total/60:.1f}分钟)")
    print(f"📐 分辨率: {WIDTH}x{HEIGHT}")
    print("=" * 60)

if __name__ == "__main__":
    main()
