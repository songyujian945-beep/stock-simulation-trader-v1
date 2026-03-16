#!/usr/bin/env python3
"""
短视频自动生成 v1 - 优化版
改进：
1. 竖屏9:16（抖音标准）
2. 更丰富的画面效果
3. 背景音乐
4. 更好的节奏
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import edge_tts
from moviepy.editor import *
import asyncio

# 配置
OUTPUT_DIR = "/Users/syj/.openclaw/workspace/video_training/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 竖屏尺寸（抖音）
WIDTH, HEIGHT = 1080, 1920
FPS = 30

# 热门短视频主题池
THEMES = [
    {
        "name": "职场吐槽",
        "scenes": [
            {"text": "当老板说'这个需求很简单'时", "emoji": "😅"},
            {"text": "产品经理：就改一个小功能", "emoji": "🙃"},
            {"text": "程序员内心：重写整个系统", "emoji": "💀"},
            {"text": "老板：明天上线", "emoji": "😱"},
            {"text": "程序员：我选择加班", "emoji": "😭"},
        ]
    },
    {
        "name": "情感共鸣",
        "scenes": [
            {"text": "你以为的周末", "emoji": "🎉"},
            {"text": "实际的周末", "emoji": "😴"},
            {"text": "周五晚上的你", "emoji": "🥳"},
            {"text": "周一早上的你", "emoji": "🧟"},
            {"text": "这就是生活", "emoji": "💪"},
        ]
    },
    {
        "name": "扎心真相",
        "scenes": [
            {"text": "小时候以为", "emoji": "👶"},
            {"text": "长大就能为所欲为", "emoji": "😎"},
            {"text": "长大后发现", "emoji": "😢"},
            {"text": "穷才限制了我的想象", "emoji": "💸"},
            {"text": "但梦想还是要有的", "emoji": "✨"},
        ]
    },
]

class VideoGeneratorV1:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.fps = FPS
        self.output_dir = OUTPUT_DIR
        
    def create_gradient_bg(self, color1, color2, direction='vertical'):
        """创建渐变背景"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        if direction == 'vertical':
            for y in range(self.height):
                ratio = y / self.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        else:
            for x in range(self.width):
                ratio = x / self.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, self.height)], fill=(r, g, b))
        
        return img
    
    def add_particles(self, img, count=50, color=(255, 255, 255, 128)):
        """添加粒子效果"""
        draw = ImageDraw.Draw(img, 'RGBA')
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 8)
            alpha = random.randint(50, 200)
            particle_color = (*color[:3], alpha)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=particle_color)
        return img
    
    def create_text_image(self, text, emoji, bg_img, font_size=60):
        """创建带文字的场景图"""
        # 复制背景
        img = bg_img.copy()
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
            emoji_font = ImageFont.truetype("/System/Library/Fonts/AppleColorEmoji.ttc", 120)
        except:
            font = ImageFont.load_default()
            emoji_font = font
        
        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        text_y = self.height // 2 - 50
        
        # 绘制文字阴影
        shadow_offset = 4
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
                 font=font, fill=(0, 0, 0, 128))
        
        # 绘制文字
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
        
        # 绘制emoji（如果支持）
        try:
            emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            emoji_x = (self.width - emoji_width) // 2
            emoji_y = text_y - 200
            draw.text((emoji_x, emoji_y), emoji, font=emoji_font, fill=(255, 255, 255))
        except:
            pass
        
        return img
    
    async def generate_audio(self, text, output_path):
        """生成语音"""
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(output_path)
    
    def create_scene_clip(self, text, emoji, duration=3, bg_colors=None):
        """创建单个场景片段"""
        if bg_colors is None:
            # 随机选择渐变色
            palettes = [
                ((66, 133, 244), (15, 32, 39)),    # 蓝紫
                ((233, 30, 99), (103, 58, 183)),   # 粉紫
                ((255, 87, 34), (255, 193, 7)),    # 橙黄
                ((0, 150, 136), (0, 96, 100)),     # 青绿
            ]
            bg_colors = random.choice(palettes)
        
        # 创建背景
        bg = self.create_gradient_bg(*bg_colors)
        bg = self.add_particles(bg, count=30)
        
        # 创建文字图像
        text_img = self.create_text_image(text, emoji, bg)
        
        # 保存临时图片
        temp_img = f"{self.output_dir}/temp_scene.png"
        text_img.save(temp_img)
        
        # 创建视频片段
        clip = ImageClip(temp_img).set_duration(duration)
        
        # 添加淡入淡出效果
        clip = clip.crossfadein(0.3).crossfadeout(0.3)
        
        return clip
    
    def generate_video(self, theme_name=None):
        """生成完整视频"""
        # 随机选择主题
        if theme_name:
            theme = next((t for t in THEMES if t["name"] == theme_name), THEMES[0])
        else:
            theme = random.choice(THEMES)
        
        print(f"📹 生成主题: {theme['name']}")
        
        clips = []
        for i, scene in enumerate(theme["scenes"]):
            print(f"  场景 {i+1}/{len(theme['scenes'])}: {scene['text']}")
            
            # 创建视频片段
            clip = self.create_scene_clip(
                scene["text"], 
                scene["emoji"],
                duration=2.5
            )
            clips.append(clip)
        
        # 合并所有片段
        print("🎬 合并片段...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # 添加淡入淡出
        final_video = final_video.fadein(0.5).fadeout(0.5)
        
        # 生成音频
        print("🎙️ 生成配音...")
        full_text = "。".join([s["text"] for s in theme["scenes"]])
        audio_path = f"{self.output_dir}/audio.mp3"
        asyncio.run(self.generate_audio(full_text, audio_path))
        
        # 添加音频
        audio = AudioFileClip(audio_path)
        if audio.duration < final_video.duration:
            # 音频太短，循环
            audio = audio.loop(duration=final_video.duration)
        else:
            # 音频太长，截断
            audio = audio.subclip(0, final_video.duration)
        
        final_video = final_video.set_audio(audio)
        
        # 导出视频
        output_path = f"{self.output_dir}/{theme['name']}_v1.mp4"
        print(f"💾 导出视频: {output_path}")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # 清理临时文件
        os.remove(f"{self.output_dir}/temp_scene.png")
        os.remove(audio_path)
        
        print(f"✅ 完成！时长: {final_video.duration:.1f}秒")
        return output_path

if __name__ == "__main__":
    generator = VideoGeneratorV1()
    # 随机生成一个主题
    output = generator.generate_video()
    print(f"\n输出: {output}")
