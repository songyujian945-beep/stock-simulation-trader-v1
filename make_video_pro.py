#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《三只小猪》增强版 - 更丰富的动画和内容
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy import *
import asyncio
import random

# 创建输出目录
output_dir = "/Users/syj/.openclaw/workspace/video_output"
os.makedirs(output_dir, exist_ok=True)

# 视频配置
WIDTH, HEIGHT = 1080, 1920
FPS = 30  # 提高帧率

# 颜色
COLORS = {
    'sky_top': (135, 206, 250),
    'sky_bottom': (176, 224, 230),
    'grass': (34, 139, 34),
    'grass_light': (124, 252, 0),
    'pig_pink': (255, 182, 193),
    'pig_dark': (219, 112, 147),
    'wolf_gray': (105, 105, 105),
    'wolf_dark': (70, 70, 70),
    'straw': (218, 165, 32),
    'wood': (139, 90, 43),
    'brick': (178, 34, 34),
    'sun': (255, 223, 0),
    'cloud': (255, 255, 255),
    'tree_trunk': (139, 69, 19),
    'tree_leaves': (34, 139, 34),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
}

# 故事文本（更丰富的内容）
scenes = [
    {'text': '很久很久以前，猪妈妈有三只可爱的小猪。', 'subtitle': '小猪们渐渐长大了...', 'scene_type': 'intro'},
    {'text': '猪妈妈说："孩子们，你们该自己盖房子住了。"', 'subtitle': '', 'scene_type': 'mother'},
    {'text': '猪大哥最懒，用稻草很快盖好了房子。', 'subtitle': '"这样我就可以睡觉了！"', 'scene_type': 'straw_house'},
    {'text': '猪二哥用木头盖房子，也不太结实。', 'subtitle': '"这看起来不错！"', 'scene_type': 'wood_house'},
    {'text': '猪小弟最勤劳，用了很久盖砖头房子。', 'subtitle': '"我要盖最坚固的房子！"', 'scene_type': 'brick_house'},
    {'text': '突然，一只可怕的大灰狼出现了！', 'subtitle': '', 'scene_type': 'wolf_appear'},
    {'text': '大灰狼吹了口气，稻草房就倒了！', 'subtitle': '"呼——"', 'scene_type': 'blow_straw'},
    {'text': '木头房子也被吹倒了！', 'subtitle': '"救命啊！"', 'scene_type': 'blow_wood'},
    {'text': '但是砖头房子怎么也吹不倒！', 'subtitle': '"吹不动！"', 'scene_type': 'blow_brick'},
    {'text': '大灰狼累得气喘吁吁，灰溜溜地跑了。', 'subtitle': '', 'scene_type': 'wolf_leave'},
    {'text': '从此，三只小猪幸福地生活在一起。', 'subtitle': '勤劳才能成功！', 'scene_type': 'happy_ending'},
]

def create_gradient_background():
    """创建渐变天空"""
    img = Image.new('RGB', (WIDTH, HEIGHT))
    for y in range(HEIGHT // 2):
        ratio = y / (HEIGHT // 2)
        r = int(COLORS['sky_top'][0] * (1 - ratio) + COLORS['sky_bottom'][0] * ratio)
        g = int(COLORS['sky_top'][1] * (1 - ratio) + COLORS['sky_bottom'][1] * ratio)
        b = int(COLORS['sky_top'][2] * (1 - ratio) + COLORS['sky_bottom'][2] * ratio)
        for x in range(WIDTH):
            img.putpixel((x, y), (r, g, b))
    return img

def draw_sun(draw, x, y, radius=80):
    """画太阳（带光芒）"""
    for i in range(12):
        angle = i * 30 * math.pi / 180
        x1 = x + int((radius + 20) * math.cos(angle))
        y1 = y + int((radius + 20) * math.sin(angle))
        x2 = x + int((radius + 50) * math.cos(angle))
        y2 = y + int((radius + 50) * math.sin(angle))
        draw.line([x1, y1, x2, y2], fill=COLORS['sun'], width=8)
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=COLORS['sun'])
    draw.arc([x-25, y-10, x+25, y+30], 0, 180, fill=COLORS['black'], width=4)
    draw.ellipse([x-20, y-25, x-10, y-15], fill=COLORS['black'])
    draw.ellipse([x+10, y-25, x+20, y-15], fill=COLORS['black'])

def draw_clouds(draw, frame=0):
    """画飘动的云朵"""
    cloud_positions = [(100, 200), (400, 150), (800, 250), (600, 180)]
    for i, (cx, cy) in enumerate(cloud_positions):
        offset = int(math.sin((frame + i * 50) / 30) * 20)
        cx = (cx + offset) % WIDTH
        for dx, dy, r in [(-30, 0, 40), (0, -10, 50), (30, 0, 40), (0, 10, 35)]:
            draw.ellipse([cx+dx-r, cy+dy-r, cx+dx+r, cy+dy+r], fill=COLORS['cloud'])

def draw_tree(draw, x, y, scale=1):
    """画树"""
    w = int(30 * scale)
    h = int(120 * scale)
    draw.rectangle([x-w, y, x+w, y+h], fill=COLORS['tree_trunk'])
    for i, (dy, r) in enumerate([(0, 80), (-40, 70), (-80, 55)]):
        r = int(r * scale)
        draw.ellipse([x-r, y+int(dy*scale)-r, x+r, y+int(dy*scale)+r], fill=COLORS['tree_leaves'])

def draw_grass_with_flowers(draw):
    """画草地（带花朵）"""
    for y in range(HEIGHT // 2, HEIGHT):
        ratio = (y - HEIGHT // 2) / (HEIGHT // 2)
        color = (
            int(COLORS['grass_light'][0] * (1 - ratio) + COLORS['grass'][0] * ratio),
            int(COLORS['grass_light'][1] * (1 - ratio) + COLORS['grass'][1] * ratio),
            int(COLORS['grass_light'][2] * (1 - ratio) + COLORS['grass'][2] * ratio),
        )
        draw.line([(0, y), (WIDTH, y)], fill=color, width=1)
    
    random.seed(42)
    for _ in range(20):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(HEIGHT // 2 + 50, HEIGHT - 100)
        color = random.choice([(255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        for dx in [-5, 5, 0]:
            for dy in [-5, 5, 0]:
                draw.ellipse([x+dx-4, y+dy-4, x+dx+4, y+dy+4], fill=color)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=(255, 255, 0))

def draw_pig_detailed(draw, x, y, scale=1, facing='right'):
    """画详细的小猪"""
    x, y, scale = int(x), int(y), float(scale)
    r = int(80 * scale)
    
    # 身体
    draw.ellipse([x-r, y-r//2, x+r, y+r//2], fill=COLORS['pig_pink'], outline=COLORS['pig_dark'], width=3)
    
    # 头
    head_r = int(60 * scale)
    head_x = x + (int(50 * scale) if facing == 'right' else -int(50 * scale))
    draw.ellipse([head_x-head_r, y-head_r//2, head_x+head_r, y+head_r//2], 
                 fill=COLORS['pig_pink'], outline=COLORS['pig_dark'], width=3)
    
    # 耳朵
    for dx in [-1, 1]:
        ear_x = head_x + int(dx * 30 * scale)
        draw.ellipse([ear_x-15, y-int(50*scale), ear_x+15, y-int(20*scale)], 
                    fill=COLORS['pig_pink'], outline=COLORS['pig_dark'], width=2)
    
    # 眼睛
    for dx in [-1, 1]:
        ex = head_x + int(dx * 15 * scale)
        draw.ellipse([ex-10, y-30, ex+10, y-10], fill=COLORS['white'])
        draw.ellipse([ex-5, y-25, ex+5, y-15], fill=COLORS['black'])
    
    # 鼻子
    draw.ellipse([head_x-20, y+5, head_x+20, y+35], fill=(255, 150, 160))
    draw.ellipse([head_x-10, y+12, head_x-2, y+20], fill=COLORS['black'])
    draw.ellipse([head_x+2, y+12, head_x+10, y+20], fill=COLORS['black'])
    
    # 腿
    leg_y = y + int(40 * scale)
    for dx in [-1, 1]:
        for dz in [-0.5, 0.5]:
            lx = x + int(dx * 50 * scale * dz)
            draw.rectangle([lx-8, leg_y, lx+8, leg_y+40], fill=COLORS['pig_pink'], 
                         outline=COLORS['pig_dark'], width=2)
    
    # 尾巴
    tail_x = x - (int(80 * scale) if facing == 'right' else -int(80 * scale))
    for i in range(5):
        offset = int(math.sin(i * 0.8) * 10)
        draw.ellipse([tail_x-offset-5, y-i*5-5, tail_x-offset+5, y-i*5+5], fill=COLORS['pig_pink'])

def draw_wolf_detailed(draw, x, y, scale=1, angry=False):
    """画详细的大灰狼"""
    x, y, scale = int(x), int(y), float(scale)
    r = int(90 * scale)
    
    # 身体
    draw.ellipse([x-r, y-r//2, x+r, y+r//2], fill=COLORS['wolf_gray'], 
                 outline=COLORS['wolf_dark'], width=3)
    
    # 头
    head_r = int(70 * scale)
    draw.ellipse([x-head_r, y-head_r, x+head_r, y+head_r//2], 
                 fill=COLORS['wolf_gray'], outline=COLORS['wolf_dark'], width=3)
    
    # 尖耳朵
    for dx in [-1, 1]:
        ear_points = [
            (x + int(dx * 40 * scale), y - int(30 * scale)),
            (x + int(dx * 60 * scale), y - int(80 * scale)),
            (x + int(dx * 20 * scale), y - int(50 * scale))
        ]
        draw.polygon(ear_points, fill=COLORS['wolf_gray'], outline=COLORS['wolf_dark'])
    
    # 眼睛
    eye_color = (255, 0, 0) if angry else COLORS['black']
    for dx in [-1, 1]:
        ex = x + int(dx * 25 * scale)
        draw.ellipse([ex-12, y-25, ex+12, y], fill=COLORS['white'])
        draw.ellipse([ex-6, y-18, ex+6, y-6], fill=eye_color)
    
    # 鼻子
    draw.ellipse([x-15, y+5, x+15, y+25], fill=COLORS['black'])
    
    # 嘴巴
    if angry:
        draw.polygon([(x-30, y+30), (x, y+50), (x+30, y+30)], fill=COLORS['black'])
        for dx in range(-20, 25, 10):
            draw.polygon([(x+dx-3, y+30), (x+dx, y+40), (x+dx+3, y+30)], fill=COLORS['white'])
    else:
        draw.arc([x-25, y+15, x+25, y+45], 0, 180, fill=COLORS['black'], width=3)
    
    # 腿
    for dx in [-1, 1]:
        draw.rectangle([x+int(dx*40)-10, y+int(45*scale), x+int(dx*40)+10, y+int(85*scale)], 
                      fill=COLORS['wolf_gray'], outline=COLORS['wolf_dark'], width=2)
    
    # 尾巴
    tail_x = x - int(90 * scale)
    for i in range(8):
        offset = int(math.sin(i * 0.6) * 15)
        draw.ellipse([tail_x-offset-8, y-i*6-8, tail_x-offset+8, y-i*6+8], fill=COLORS['wolf_gray'])

def draw_house_detailed(draw, x, y, house_type, destroyed=False):
    """画详细的房子"""
    x, y = int(x), int(y)
    
    if house_type == 'straw':
        wall_color = COLORS['straw']
        roof_color = (184, 134, 11)
        label = '稻草房'
    elif house_type == 'wood':
        wall_color = COLORS['wood']
        roof_color = (101, 67, 33)
        label = '木头房'
    else:
        wall_color = COLORS['brick']
        roof_color = (139, 69, 19)
        label = '砖头房'
    
    w, h = 350, 280
    
    if destroyed:
        for i in range(5):
            rx = x + random.randint(-150, 150)
            ry = y + random.randint(-50, 150)
            rw = random.randint(30, 80)
            rh = random.randint(20, 50)
            draw.rectangle([rx, ry, rx+rw, ry+rh], fill=wall_color, outline=COLORS['black'])
    else:
        # 房身
        draw.rectangle([x-w//2, y-h//2, x+w//2, y+h//2], 
                      fill=wall_color, outline=COLORS['black'], width=4)
        
        # 屋顶
        roof_points = [(x-w//2-30, y-h//2), (x, y-h//2-180), (x+w//2+30, y-h//2)]
        draw.polygon(roof_points, fill=roof_color, outline=COLORS['black'])
        
        # 门
        draw.rectangle([x-50, y+h//2-150, x+50, y+h//2], 
                      fill=(101, 67, 33), outline=COLORS['black'], width=3)
        draw.ellipse([x+30, y+h//2-80, x+45, y+h//2-60], fill=(255, 215, 0))
        
        # 窗户
        for dx in [-120, 120]:
            draw.rectangle([x+dx-50, y-h//4-50, x+dx+50, y-h//4+50], 
                          fill=(200, 230, 255), outline=COLORS['black'], width=3)
            draw.line([x+dx, y-h//4-50, x+dx, y-h//4+50], fill=COLORS['black'], width=2)
            draw.line([x+dx-50, y-h//4, x+dx+50, y-h//4], fill=COLORS['black'], width=2)
        
        # 烟囱
        draw.rectangle([x+w//2-80, y-h//2-100, x+w//2-40, y-h//2-30], 
                      fill=roof_color, outline=COLORS['black'])
        
        # 标签
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 45)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        label_y = y + h//2 + 30
        draw.rectangle([x-text_w//2-20, label_y-10, x+text_w//2+20, label_y+50], 
                      fill=(255, 255, 255), outline=COLORS['black'])
        draw.text((x - text_w//2, label_y), label, fill=COLORS['black'], font=font)

def create_scene_image(scene_index, frame=0):
    """创建场景图片"""
    img = create_gradient_background()
    draw = ImageDraw.Draw(img)
    
    draw_sun(draw, WIDTH - 150, 200, 60)
    draw_clouds(draw, frame)
    draw_grass_with_flowers(draw)
    
    for tx in [100, WIDTH - 100]:
        draw_tree(draw, tx, HEIGHT//2 + 50, scale=0.8)
    
    scene_type = scenes[scene_index]['scene_type']
    
    if scene_type == 'intro':
        positions = [(WIDTH//4, HEIGHT//2+100), (WIDTH//2-50, HEIGHT//2+80), 
                     (WIDTH//2+50, HEIGHT//2+80), (3*WIDTH//4, HEIGHT//2+100)]
        for i, (px, py) in enumerate(positions):
            draw_pig_detailed(draw, px, py, scale=0.7, facing='right' if i < 2 else 'left')
    
    elif scene_type == 'mother':
        draw_pig_detailed(draw, WIDTH//2, HEIGHT//2+100, scale=1.0)
        for i, px in enumerate([WIDTH//2-200, WIDTH//2, WIDTH//2+200]):
            draw_pig_detailed(draw, px, HEIGHT//2+350, scale=0.5, 
                            facing='right' if i == 0 else 'left' if i == 2 else 'right')
    
    elif scene_type == 'straw_house':
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'straw')
        draw_pig_detailed(draw, WIDTH//2, HEIGHT//2+350, scale=0.7, facing='right')
    
    elif scene_type == 'wood_house':
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'wood')
        draw_pig_detailed(draw, WIDTH//2, HEIGHT//2+350, scale=0.7, facing='right')
    
    elif scene_type == 'brick_house':
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'brick')
        draw_pig_detailed(draw, WIDTH//2, HEIGHT//2+350, scale=0.7, facing='right')
    
    elif scene_type == 'wolf_appear':
        draw_wolf_detailed(draw, WIDTH//4, HEIGHT//2+200, scale=1.2, angry=True)
        for i, px in enumerate([WIDTH//2-100, WIDTH//2, WIDTH//2+100]):
            draw_pig_detailed(draw, px, HEIGHT//2+350, scale=0.5, facing='left')
    
    elif scene_type == 'blow_straw':
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'straw', destroyed=True)
        draw_wolf_detailed(draw, WIDTH//4, HEIGHT//2+200, scale=1.2, angry=True)
        for i in range(10):
            fx = WIDTH//4 + 100 + i * 50
            fy = HEIGHT//2 + random.randint(-100, 100)
            draw.line([(fx, fy), (fx+40, fy)], fill=(200, 200, 200), width=3)
    
    elif scene_type == 'blow_wood':
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'wood', destroyed=True)
        draw_wolf_detailed(draw, WIDTH//4, HEIGHT//2+200, scale=1.2, angry=True)
        for i in range(10):
            fx = WIDTH//4 + 100 + i * 50
            fy = HEIGHT//2 + random.randint(-100, 100)
            draw.line([(fx, fy), (fx+40, fy)], fill=(200, 200, 200), width=3)
    
    elif scene_type == 'blow_brick':
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'brick', destroyed=False)
        draw_wolf_detailed(draw, WIDTH//4, HEIGHT//2+200, scale=1.2, angry=True)
        for i in range(0, 360, 30):
            angle = math.radians(i + frame * 5)
            rx = WIDTH//2 + int(250 * math.cos(angle))
            ry = HEIGHT//2 + int(200 * math.sin(angle))
            draw.ellipse([rx-5, ry-5, rx+5, ry+5], fill=(255, 215, 0))
    
    elif scene_type == 'wolf_leave':
        draw_wolf_detailed(draw, WIDTH - 150, HEIGHT//2+250, scale=0.8, angry=False)
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2+50, 'brick')
    
    else:  # happy_ending
        draw_house_detailed(draw, WIDTH//2, HEIGHT//2, 'brick')
        for i, px in enumerate([WIDTH//2-180, WIDTH//2, WIDTH//2+180]):
            draw_pig_detailed(draw, px, HEIGHT//2+350, scale=0.7, 
                            facing='right' if i == 0 else 'left' if i == 2 else 'right')
        rainbow_colors = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), 
                         (0,0,255), (75,0,130), (143,0,255)]
        for i, color in enumerate(rainbow_colors):
            draw.arc([100, 50, WIDTH-100, 400], 180, 360, fill=color, width=15)
    
    return img

async def generate_audio(text, output_file):
    """生成语音"""
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save(output_file)

def create_text_with_style(text, subtitle, duration):
    """创建带样式的文字"""
    txt_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)
    
    try:
        main_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 55)
        sub_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    except:
        main_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=main_font)
    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) // 2
    y = HEIGHT - 350
    
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if abs(dx) + abs(dy) <= 4:
                draw.text((x+dx, y+dy), text, font=main_font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=main_font, fill=COLORS['white'])
    
    if subtitle:
        bbox2 = draw.textbbox((0, 0), subtitle, font=sub_font)
        text_w2 = bbox2[2] - bbox2[0]
        x2 = (WIDTH - text_w2) // 2
        y2 = HEIGHT - 250
        draw.rectangle([x2-20, y2-10, x2+text_w2+20, y2+60], fill=(0, 0, 0, 150))
        draw.text((x2, y2), subtitle, font=sub_font, fill=(255, 215, 0))
    
    txt_path = f"{output_dir}/text_{hash(text)}.png"
    txt_img.save(txt_path)
    
    return ImageClip(txt_path).with_duration(duration)

def main():
    print("🎬 开始制作增强版视频...")
    print("=" * 50)
    
    clips = []
    
    for i, scene in enumerate(scenes):
        print(f"\n📹 场景 {i+1}/{len(scenes)}: {scene['text'][:20]}...")
        
        audio_path = f"{output_dir}/audio_pro_{i}.mp3"
        asyncio.run(generate_audio(scene['text'], audio_path))
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration + 1.0
        
        frames_needed = int(audio_duration * FPS)
        frame_step = 3
        
        print(f"   生成 {frames_needed} 帧动画...")
        
        frame_paths = []
        for f in range(0, frames_needed, frame_step):
            img = create_scene_image(i, f)
            frame_path = f"{output_dir}/frame_{i}_{f}.png"
            img.save(frame_path)
            frame_paths.append(frame_path)
        
        if len(frame_paths) > 1:
            video_clip = ImageSequenceClip(frame_paths, fps=FPS/frame_step)
            video_clip = video_clip.with_duration(audio_duration)
        else:
            video_clip = ImageClip(frame_paths[0]).with_duration(audio_duration)
        
        txt_clip = create_text_with_style(scene['text'], scene['subtitle'], audio_duration)
        
        scene_clip = CompositeVideoClip([video_clip, txt_clip])
        scene_clip = scene_clip.with_audio(audio_clip)
        
        clips.append(scene_clip)
        print(f"   ✅ 场景 {i+1} 完成 ({audio_duration:.1f}秒)")
        
        for fp in frame_paths:
            try:
                os.remove(fp)
            except:
                pass
    
    print("\n" + "=" * 50)
    print("拼接视频并添加转场效果...")
    
    final_clips = []
    for clip in clips:
        clip = clip.fadein(0.3).fadeout(0.3)
        final_clips.append(clip)
    
    final_video = concatenate_videoclips(final_clips, method="compose")
    
    output_path = f"{output_dir}/three_little_pigs_pro.mp4"
    print(f"\n💾 渲染视频到: {output_path}")
    print("这可能需要1-2分钟，请耐心等待...")
    
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k',
        preset='medium',
        logger=None
    )
    
    final_video.close()
    for clip in clips:
        clip.close()
    
    total_duration = sum([c.duration for c in clips])
    print("\n" + "=" * 50)
    print("✅ 视频制作完成！")
    print(f"📍 文件位置: {output_path}")
    print(f"⏱️  总时长: {total_duration:.1f} 秒")
    print(f"🎨 场景数: {len(scenes)} 个")
    print(f"📐 分辨率: {WIDTH}x{HEIGHT}")
    print("=" * 50)

if __name__ == "__main__":
    main()
