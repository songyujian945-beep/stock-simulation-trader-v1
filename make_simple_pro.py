#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化版增强动画"""

import os
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy import *
import asyncio
import random

output_dir = "/Users/syj/.openclaw/workspace/video_output"
os.makedirs(output_dir, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 24

scenes = [
    {'text': '很久以前，三只小猪长大了', 'type': 'intro'},
    {'text': '猪大哥用稻草盖房子', 'type': 'straw'},
    {'text': '猪二哥用木头盖房子', 'type': 'wood'},
    {'text': '猪小弟用砖头盖房子', 'type': 'brick'},
    {'text': '大灰狼来了！吹倒了稻草房', 'type': 'blow1'},
    {'text': '又吹倒了木头房', 'type': 'blow2'},
    {'text': '但砖头房吹不倒', 'type': 'noblow'},
    {'text': '勤劳才能成功！', 'type': 'end'},
]

def draw_scene(scene_type):
    img = Image.new('RGB', (WIDTH, HEIGHT), (135, 206, 250))
    draw = ImageDraw.Draw(img)
    
    # 草地
    draw.rectangle([0, HEIGHT//2, WIDTH, HEIGHT], fill=(34, 139, 34))
    
    # 太阳
    draw.ellipse([WIDTH-200, 100, WIDTH-100, 200], fill=(255, 223, 0))
    
    # 根据场景画内容
    if scene_type == 'intro':
        for x in [WIDTH//4, WIDTH//2, 3*WIDTH//4]:
            # 简单的小猪（粉色圆圈+耳朵）
            draw.ellipse([x-60, HEIGHT//2+50, x+60, HEIGHT//2+170], fill=(255, 182, 193))
            draw.ellipse([x-40, HEIGHT//2+30, x-20, HEIGHT//2+50], fill=(255, 182, 193))
            draw.ellipse([x+20, HEIGHT//2+30, x+40, HEIGHT//2+50], fill=(255, 182, 193))
            # 眼睛和鼻子
            draw.ellipse([x-25, HEIGHT//2+80, x-15, HEIGHT//2+90], fill=(0,0,0))
            draw.ellipse([x+15, HEIGHT//2+80, x+25, HEIGHT//2+90], fill=(0,0,0))
            draw.ellipse([x-15, HEIGHT//2+105, x+15, HEIGHT//2+130], fill=(255, 150, 160))
    
    elif scene_type in ['straw', 'wood', 'brick']:
        # 房子
        colors = {'straw': (218, 165, 32), 'wood': (139, 90, 43), 'brick': (178, 34, 34)}
        labels = {'straw': '稻草房', 'wood': '木头房', 'brick': '砖头房'}
        color = colors[scene_type]
        
        # 房身
        draw.rectangle([WIDTH//2-150, HEIGHT//2-100, WIDTH//2+150, HEIGHT//2+100], 
                      fill=color, outline=(0,0,0), width=4)
        # 屋顶
        draw.polygon([(WIDTH//2-170, HEIGHT//2-100), (WIDTH//2, HEIGHT//2-250), 
                     (WIDTH//2+170, HEIGHT//2-100)], fill=(139, 69, 19))
        # 门
        draw.rectangle([WIDTH//2-40, HEIGHT//2+10, WIDTH//2+40, HEIGHT//2+100], fill=(101, 67, 33))
        # 窗户
        draw.rectangle([WIDTH//2-120, HEIGHT//2-70, WIDTH//2-60, HEIGHT//2-10], fill=(200, 230, 255))
        draw.rectangle([WIDTH//2+60, HEIGHT//2-70, WIDTH//2+120, HEIGHT//2-10], fill=(200, 230, 255))
        
        # 标签
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
            bbox = draw.textbbox((0, 0), labels[scene_type], font=font)
            tw = bbox[2] - bbox[0]
            draw.text((WIDTH//2-tw//2, HEIGHT//2+120), labels[scene_type], fill=(0,0,0), font=font)
        except:
            pass
        
        # 小猪
        draw.ellipse([WIDTH//2-60, HEIGHT//2+280, WIDTH//2+60, HEIGHT//2+400], fill=(255, 182, 193))
        draw.ellipse([WIDTH//2-40, HEIGHT//2+260, WIDTH//2-20, HEIGHT//2+280], fill=(255, 182, 193))
        draw.ellipse([WIDTH//2+20, HEIGHT//2+260, WIDTH//2+40, HEIGHT//2+280], fill=(255, 182, 193))
    
    elif scene_type in ['blow1', 'blow2']:
        # 倒塌的房子
        house_types = {'blow1': 'straw', 'blow2': 'wood'}
        colors = {'straw': (218, 165, 32), 'wood': (139, 90, 43)}
        color = colors[house_types[scene_type]]
        
        # 乱七八糟的房子碎片
        random.seed(42)
        for _ in range(8):
            x = WIDTH//2 + random.randint(-200, 200)
            y = HEIGHT//2 + random.randint(-100, 150)
            w = random.randint(30, 80)
            h = random.randint(20, 60)
            draw.rectangle([x, y, x+w, y+h], fill=color, outline=(0,0,0), width=2)
        
        # 大灰狼
        draw.ellipse([WIDTH//4-80, HEIGHT//2+100, WIDTH//4+80, HEIGHT//2+260], fill=(105, 105, 105))
        # 尖耳朵
        draw.polygon([(WIDTH//4-60, HEIGHT//2+100), (WIDTH//4-80, HEIGHT//2+50), (WIDTH//4-40, HEIGHT//2+100)], 
                    fill=(105, 105, 105))
        draw.polygon([(WIDTH//4+60, HEIGHT//2+100), (WIDTH//4+80, HEIGHT//2+50), (WIDTH//4+40, HEIGHT//2+100)], 
                    fill=(105, 105, 105))
        # 眼睛
        draw.ellipse([WIDTH//4-25, HEIGHT//2+140, WIDTH//4-5, HEIGHT//2+160], fill=(255, 0, 0))
        draw.ellipse([WIDTH//4+5, HEIGHT//2+140, WIDTH//4+25, HEIGHT//2+160], fill=(255, 0, 0))
        
        # 吹风效果
        for i in range(6):
            fx = WIDTH//4 + 150 + i * 60
            fy = HEIGHT//2 + 50 + i * 20
            draw.line([(fx, fy), (fx+50, fy)], fill=(200, 200, 200), width=4)
    
    elif scene_type == 'noblow':
        # 坚固的砖房
        draw.rectangle([WIDTH//2-150, HEIGHT//2-100, WIDTH//2+150, HEIGHT//2+100], 
                      fill=(178, 34, 34), outline=(0,0,0), width=5)
        draw.polygon([(WIDTH//2-170, HEIGHT//2-100), (WIDTH//2, HEIGHT//2-250), 
                     (WIDTH//2+170, HEIGHT//2-100)], fill=(139, 69, 19))
        draw.rectangle([WIDTH//2-40, HEIGHT//2+10, WIDTH//2+40, HEIGHT//2+100], fill=(101, 67, 33))
        
        # 防护盾效果
        draw.ellipse([WIDTH//2-200, HEIGHT//2-150, WIDTH//2+200, HEIGHT//2+150], 
                    outline=(255, 215, 0), width=5)
        
        # 大灰狼（累趴了）
        draw.ellipse([WIDTH//4-70, HEIGHT//2+150, WIDTH//4+70, HEIGHT//2+280], fill=(105, 105, 105))
        draw.text((WIDTH//4-30, HEIGHT//2+200), "累了...", fill=(0,0,0))
    
    else:  # end
        # 砖房 + 彩虹
        draw.rectangle([WIDTH//2-150, HEIGHT//2-100, WIDTH//2+150, HEIGHT//2+100], 
                      fill=(178, 34, 34), outline=(0,0,0), width=4)
        draw.polygon([(WIDTH//2-170, HEIGHT//2-100), (WIDTH//2, HEIGHT//2-250), 
                     (WIDTH//2+170, HEIGHT//2-100)], fill=(139, 69, 19))
        
        # 三只小猪
        for i, x in enumerate([WIDTH//2-180, WIDTH//2, WIDTH//2+180]):
            draw.ellipse([x-50, HEIGHT//2+250, x+50, HEIGHT//2+350], fill=(255, 182, 193))
        
        # 彩虹
        colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255)]
        for i, c in enumerate(colors):
            draw.arc([50, 50, WIDTH-50, 350], 180, 360, fill=c, width=12)
    
    return img

async def gen_audio(text, path):
    com = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await com.save(path)

def main():
    print("🎬 快速制作增强版...")
    clips = []
    
    for i, scene in enumerate(scenes):
        print(f"场景 {i+1}/{len(scenes)}: {scene['text'][:15]}...")
        
        # 生成图片
        img = draw_scene(scene['type'])
        img_path = f"{output_dir}/scene_pro_{i}.png"
        img.save(img_path)
        
        # 生成语音
        audio_path = f"{output_dir}/audio_pro_{i}.mp3"
        asyncio.run(gen_audio(scene['text'], audio_path))
        
        # 获取时长
        audio = AudioFileClip(audio_path)
        dur = audio.duration + 0.5
        
        # 创建片段
        video = ImageClip(img_path).with_duration(dur)
        
        # 添加文字
        txt_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 50)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), scene['text'], font=font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        y = HEIGHT - 300
        
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x+dx, y+dy), scene['text'], font=font, fill=(0, 0, 0))
        draw.text((x, y), scene['text'], font=font, fill=(255, 255, 255))
        
        txt_path = f"{output_dir}/txt_pro_{i}.png"
        txt_img.save(txt_path)
        txt = ImageClip(txt_path).with_duration(dur)
        
        # 合成
        final = CompositeVideoClip([video, txt]).with_audio(audio)
        clips.append(final)
    
    print("拼接视频...")
    result = concatenate_videoclips(clips)
    
    output = f"{output_dir}/three_little_pigs_enhanced.mp4"
    print(f"渲染中: {output}")
    result.write_videofile(output, fps=FPS, codec='libx264', audio_codec='aac', logger=None)
    
    result.close()
    for c in clips:
        c.close()
    
    duration = sum([c.duration for c in clips])
    print(f"\n✅ 完成！时长: {duration:.1f}秒")
    print(f"📍 位置: {output}")

if __name__ == "__main__":
    main()
