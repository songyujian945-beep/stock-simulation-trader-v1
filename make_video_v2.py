#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作一个简单的《三只小猪》儿童故事动画
"""

import os
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy import *
import asyncio

# 创建输出目录
output_dir = "/Users/syj/.openclaw/workspace/video_output"
os.makedirs(output_dir, exist_ok=True)

# 视频配置
WIDTH, HEIGHT = 1080, 1920  # 竖屏格式（抖音风格）
FPS = 24

# 颜色定义
COLORS = {
    'sky': (135, 206, 235),
    'grass': (124, 252, 0),
    'pig_pink': (255, 182, 193),
    'wolf_gray': (128, 128, 128),
    'straw': (210, 180, 140),
    'wood': (139, 90, 43),
    'brick': (178, 34, 34),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
}

# 故事文本（分成几个场景）
scenes = [
    {'text': '从前，有三只小猪离开了妈妈，要自己盖房子住。', 'duration': 5},
    {'text': '猪大哥很懒，用稻草盖了一座房子。', 'duration': 5},
    {'text': '猪二哥也不勤快，用木头盖了一座房子。', 'duration': 5},
    {'text': '猪小弟最勤劳，用砖头盖了一座坚固的房子。', 'duration': 5},
    {'text': '一天，大灰狼来了！它吹倒了稻草房。', 'duration': 5},
    {'text': '又吹倒了木头房！', 'duration': 4},
    {'text': '但是砖头房子吹不倒！', 'duration': 4},
    {'text': '三只小猪安全了！这个故事告诉我们：勤劳才能成功！', 'duration': 6},
]

def create_scene_image(scene_index, total_scenes):
    """创建一个场景的图片"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['sky'])
    draw = ImageDraw.Draw(img)
    
    # 画草地（下半部分）
    draw.rectangle([0, HEIGHT//2, WIDTH, HEIGHT], fill=COLORS['grass'])
    
    # 根据场景画不同的内容
    if scene_index == 0:
        for i, x in enumerate([WIDTH//4, WIDTH//2, 3*WIDTH//4]):
            draw_pig(draw, x, HEIGHT//2 + 100, COLORS['pig_pink'])
    elif scene_index == 1:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 100, COLORS['straw'], '稻草房')
        draw_pig(draw, WIDTH//2, HEIGHT//2 + 300, COLORS['pig_pink'])
    elif scene_index == 2:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 100, COLORS['wood'], '木头房')
        draw_pig(draw, WIDTH//2, HEIGHT//2 + 300, COLORS['pig_pink'])
    elif scene_index == 3:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 100, COLORS['brick'], '砖头房')
        draw_pig(draw, WIDTH//2, HEIGHT//2 + 300, COLORS['pig_pink'])
    elif scene_index == 4:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 100, COLORS['straw'], '稻草房')
        draw_wolf(draw, WIDTH//4, HEIGHT//2 + 200)
    elif scene_index == 5:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 100, COLORS['wood'], '木头房')
        draw_wolf(draw, WIDTH//4, HEIGHT//2 + 200)
    elif scene_index == 6:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 100, COLORS['brick'], '砖头房')
        draw_wolf(draw, WIDTH//4, HEIGHT//2 + 200)
    else:
        draw_house(draw, WIDTH//2, HEIGHT//2 + 50, COLORS['brick'], '砖头房')
        for i, x in enumerate([WIDTH//3, WIDTH//2, 2*WIDTH//3]):
            draw_pig(draw, x, HEIGHT//2 + 350, COLORS['pig_pink'])
    
    return img

def draw_pig(draw, x, y, color):
    """画一只小猪"""
    r = 80
    draw.ellipse([x-r, y-r, x+r, y+r], fill=color, outline=COLORS['black'])
    draw.ellipse([x-r+10, y-r-30, x-r+50, y-r+10], fill=color)
    draw.ellipse([x+r-50, y-r-30, x+r-10, y-r+10], fill=color)
    draw.ellipse([x-35, y-20, x-15, y], fill=COLORS['white'])
    draw.ellipse([x+15, y-20, x+35, y], fill=COLORS['white'])
    draw.ellipse([x-28, y-15, x-18, y-5], fill=COLORS['black'])
    draw.ellipse([x+18, y-15, x+28, y-5], fill=COLORS['black'])
    draw.ellipse([x-20, y+15, x+20, y+45], fill=(255, 150, 160))
    draw.ellipse([x-12, y+22, x-4, y+30], fill=COLORS['black'])
    draw.ellipse([x+4, y+22, x+12, y+30], fill=COLORS['black'])

def draw_wolf(draw, x, y):
    """画一只大灰狼"""
    r = 90
    draw.ellipse([x-r, y-r, x+r, y+r], fill=COLORS['wolf_gray'], outline=COLORS['black'])
    draw.polygon([(x-r, y-r), (x-r+30, y-r-50), (x-r+60, y-r)], fill=COLORS['wolf_gray'])
    draw.polygon([(x+r, y-r), (x+r-30, y-r-50), (x+r-60, y-r)], fill=COLORS['wolf_gray'])
    draw.ellipse([x-40, y-25, x-15, y], fill=COLORS['white'])
    draw.ellipse([x+15, y-25, x+40, y], fill=COLORS['white'])
    draw.ellipse([x-32, y-18, x-20, y-6], fill=COLORS['black'])
    draw.ellipse([x+20, y-18, x+32, y-6], fill=COLORS['black'])
    draw.arc([x-30, y+10, x+30, y+50], 0, 180, fill=COLORS['black'], width=3)

def draw_house(draw, x, y, color, label):
    """画一座房子"""
    w, h = 300, 250
    draw.rectangle([x-w//2, y-h//2, x+w//2, y+h//2], fill=color, outline=COLORS['black'])
    draw.polygon([(x-w//2-20, y-h//2), (x, y-h//2-150), (x+w//2+20, y-h//2)], 
                 fill=(139, 69, 19), outline=COLORS['black'])
    draw.rectangle([x-40, y+h//2-120, x+40, y+h//2], fill=(101, 67, 33))
    draw.rectangle([x-120, y-h//4-40, x-40, y-h//4+40], fill=COLORS['white'])
    draw.rectangle([x+40, y-h//4-40, x+120, y-h//4+40], fill=COLORS['white'])
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text((x - text_w//2, y + h//2 + 20), label, fill=COLORS['black'], font=font)

async def generate_audio(text, output_file):
    """生成语音"""
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save(output_file)

def create_text_clip(text, duration):
    """创建文字片段"""
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 50)
    except:
        font = ImageFont.load_default()
    
    txt_img = Image.new('RGBA', (WIDTH-100, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (WIDTH-100 - text_w) // 2
    y = (200 - text_h) // 2
    
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x+dx, y+dy), text, font=font, fill=COLORS['black'])
    draw.text((x, y), text, font=font, fill=COLORS['white'])
    
    txt_clip = ImageClip(txt_img).with_duration(duration)
    txt_clip = txt_clip.with_position(('center', HEIGHT - 300))
    
    return txt_clip

def main():
    print("🎬 开始制作视频...")
    
    clips = []
    
    for i, scene in enumerate(scenes):
        print(f"📹 处理场景 {i+1}/{len(scenes)}: {scene['text'][:15]}...")
        
        # 1. 生成场景图片
        img = create_scene_image(i, len(scenes))
        img_path = f"{output_dir}/scene_{i}.png"
        img.save(img_path)
        
        # 2. 生成语音
        audio_path = f"{output_dir}/audio_{i}.mp3"
        asyncio.run(generate_audio(scene['text'], audio_path))
        
        # 3. 获取音频时长
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration + 0.5
        
        # 4. 创建视频片段
        video_clip = ImageClip(img_path).with_duration(audio_duration)
        
        # 5. 添加文字
        txt_clip = create_text_clip(scene['text'], audio_duration)
        
        # 6. 合成
        scene_clip = CompositeVideoClip([video_clip, txt_clip])
        scene_clip = scene_clip.with_audio(audio_clip)
        
        clips.append(scene_clip)
        print(f"   ✅ 场景 {i+1} 完成")
    
    # 合并所有片段
    print("\n拼接视频...")
    final_video = concatenate_videoclips(clips)
    
    # 输出
    output_path = f"{output_dir}/three_little_pigs.mp4"
    print(f"💾 保存视频到: {output_path}")
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        logger=None
    )
    
    # 清理
    final_video.close()
    for clip in clips:
        clip.close()
    
    total_duration = sum([c.duration for c in clips])
    print(f"\n✅ 视频制作完成！")
    print(f"📍 文件位置: {output_path}")
    print(f"⏱️  时长: {total_duration:.1f} 秒")

if __name__ == "__main__":
    main()
