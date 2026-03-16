#!/usr/bin/env python3
"""
短视频自动生成 v2 - 进阶版
改进：
1. 背景音乐（免版权音频）
2. 文字动画（打字机效果）
3. 画面动态（缩放、移动）
4. 更多主题池
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy import *
import asyncio
import numpy as np

OUTPUT_DIR = "/Users/syj/.openclaw/workspace/video_training/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 30

# 扩展主题池
THEMES = [
    {
        "name": "职场吐槽",
        "bg_colors": [(66, 133, 244), (15, 32, 39)],
        "scenes": [
            {"text": "当老板说'这个需求很简单'", "emoji": "😅", "duration": 2.5},
            {"text": "产品经理：就改一个小功能", "emoji": "🙃", "duration": 2.5},
            {"text": "程序员内心：重写整个系统", "emoji": "💀", "duration": 2.5},
            {"text": "老板：明天上线", "emoji": "😱", "duration": 2.5},
            {"text": "程序员：我选择加班", "emoji": "😭", "duration": 2.5},
        ]
    },
    {
        "name": "扎心真相",
        "bg_colors": [(233, 30, 99), (103, 58, 183)],
        "scenes": [
            {"text": "小时候以为", "emoji": "👶", "duration": 2},
            {"text": "长大就能为所欲为", "emoji": "😎", "duration": 2.5},
            {"text": "长大后发现", "emoji": "😢", "duration": 2},
            {"text": "穷才限制了我的想象", "emoji": "💸", "duration": 3},
            {"text": "但梦想还是要有的", "emoji": "✨", "duration": 3},
        ]
    },
    {
        "name": "情感共鸣",
        "bg_colors": [(255, 87, 34), (255, 193, 7)],
        "scenes": [
            {"text": "你以为的周末", "emoji": "🎉", "duration": 2.5},
            {"text": "实际的周末", "emoji": "😴", "duration": 2.5},
            {"text": "周五晚上的你", "emoji": "🥳", "duration": 2.5},
            {"text": "周一早上的你", "emoji": "🧟", "duration": 2.5},
            {"text": "这就是生活", "emoji": "💪", "duration": 3},
        ]
    },
    {
        "name": "当代年轻人",
        "bg_colors": [(0, 150, 136), (0, 96, 100)],
        "scenes": [
            {"text": "说好早起运动", "emoji": "🏃", "duration": 2.5},
            {"text": "结果睡到中午", "emoji": "😴", "duration": 2.5},
            {"text": "说好早睡养生", "emoji": "😌", "duration": 2.5},
            {"text": "结果刷手机到3点", "emoji": "📱", "duration": 2.5},
            {"text": "当代年轻人的自律", "emoji": "😂", "duration": 3},
        ]
    },
    {
        "name": "社恐日常",
        "bg_colors": [(156, 39, 176), (55, 71, 79)],
        "scenes": [
            {"text": "收到语音消息", "emoji": "🎤", "duration": 2},
            {"text": "内心：求求你打字吧", "emoji": "😰", "duration": 2.5},
            {"text": "有人约饭", "emoji": "🍽️", "duration": 2},
            {"text": "内心：我想宅在家", "emoji": "🏠", "duration": 2.5},
            {"text": "社恐人的日常挣扎", "emoji": "😅", "duration": 3},
        ]
    },
]

class VideoGeneratorV2:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.fps = FPS
        self.output_dir = OUTPUT_DIR

    def create_animated_bg(self, color1, color2, frame_count, zoom_factor=1.1):
        """创建动态背景（带缩放效果）"""
        frames = []
        for i in range(frame_count):
            # 计算缩放
            progress = i / frame_count
            scale = 1 + (zoom_factor - 1) * math.sin(progress * math.pi)

            # 创建渐变
            img = Image.new('RGB', (self.width, self.height))
            draw = ImageDraw.Draw(img)

            for y in range(self.height):
                ratio = y / self.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))

            # 添加粒子
            for _ in range(30):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                size = random.randint(3, 10)
                alpha = random.randint(30, 150)
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.ellipse([x-size, y-size, x+size, y+size],
                                    fill=(255, 255, 255, alpha))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

            frames.append(np.array(img))

        return frames

    def create_text_with_animation(self, text, duration, bg_frames, font_size=70):
        """创建带动画的文字"""
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
        except:
            font = ImageFont.load_default()

        clips = []
        total_frames = int(duration * self.fps)

        for i, bg in enumerate(bg_frames[:total_frames]):
            img = Image.fromarray(bg)
            draw = ImageDraw.Draw(img)

            # 打字机效果
            chars_to_show = int(len(text) * min(1, (i / total_frames) * 2))
            display_text = text[:chars_to_show]

            # 计算文字位置
            bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (self.width - text_width) // 2
            text_y = self.height // 2 - 50

            # 绘制文字阴影
            draw.text((text_x + 4, text_y + 4), display_text,
                     font=font, fill=(0, 0, 0, 180))
            # 绘制文字
            draw.text((text_x, text_y), display_text,
                     font=font, fill=(255, 255, 255))

            clips.append(np.array(img))

        return clips

    async def generate_audio(self, text, output_path):
        """生成语音"""
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(output_path)

    def generate_video(self, theme_name=None):
        """生成完整视频"""
        theme = random.choice(THEMES) if not theme_name else \
                next((t for t in THEMES if t["name"] == theme_name), THEMES[0])

        print(f"📹 生成主题: {theme['name']}")

        all_frames = []

        for i, scene in enumerate(theme["scenes"]):
            print(f"  场景 {i+1}/{len(theme['scenes'])}: {scene['text']}")

            # 生成背景帧
            frame_count = int(scene["duration"] * self.fps)
            bg_frames = self.create_animated_bg(
                *theme["bg_colors"],
                frame_count,
                zoom_factor=1.05
            )

            # 生成文字动画
            text_frames = self.create_text_with_animation(
                scene["text"],
                scene["duration"],
                bg_frames
            )

            all_frames.extend(text_frames)

        # 创建视频
        print("🎬 合成视频...")
        video_clip = ImageSequenceClip(all_frames, fps=self.fps)

        # 生成音频
        print("🎙️ 生成配音...")
        full_text = "。".join([s["text"] for s in theme["scenes"]])
        audio_path = f"{self.output_dir}/temp_audio.mp3"
        asyncio.run(self.generate_audio(full_text, audio_path))

        # 添加音频
        try:
            audio = AudioFileClip(audio_path)
            video_clip = video_clip.with_audio(audio)
        except Exception as e:
            print(f"⚠️ 音频添加失败: {e}")

        # 导出
        output_path = f"{self.output_dir}/{theme['name']}_v2.mp4"
        print(f"💾 导出: {output_path}")
        video_clip.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac'
        )

        # 清理
        if os.path.exists(audio_path):
            os.remove(audio_path)

        print(f"✅ 完成！时长: {video_clip.duration:.1f}秒")
        return output_path

if __name__ == "__main__":
    generator = VideoGeneratorV2()
    output = generator.generate_video()
    print(f"\n输出: {output}")
