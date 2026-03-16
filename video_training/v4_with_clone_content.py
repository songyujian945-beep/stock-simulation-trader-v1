#!/usr/bin/env python3
"""
v4 - 整合分身生成内容
使用本地Qwen2生成的内容创建视频
"""

import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
from moviepy import *

# 加载分身生成的内容
with open('/Users/syj/.openclaw/workspace/video_training/themes_qwen.json', 'r', encoding='utf-8') as f:
    THEMES = json.load(f)

with open('/Users/syj/.openclaw/workspace/video_training/title_templates.txt', 'r', encoding='utf-8') as f:
    TITLES = [line.strip() for line in f if line.strip()]

OUTPUT_DIR = "/Users/syj/.openclaw/workspace/video_training/output"
WIDTH, HEIGHT = 1080, 1920
FPS = 24

class VideoGeneratorV4:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.fps = FPS
        self.output_dir = OUTPUT_DIR

    def create_bg(self, color1, color2):
        """创建渐变背景"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            ratio = y / self.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def add_text(self, img, text, progress=1.0):
        """添加文字"""
        img = img.copy()
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 55)
        except:
            font = ImageFont.load_default()

        # 打字机效果
        chars_to_show = int(len(text) * progress)
        display_text = text[:chars_to_show]

        # 文字位置（居中）
        bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        text_y = self.height // 2 - 50

        # 阴影 + 文字
        draw.text((text_x + 3, text_y + 3), display_text, font=font, fill=(0, 0, 0, 150))
        draw.text((text_x, text_y), display_text, font=font, fill=(255, 255, 255))

        return img

    def generate_video(self, theme_idx=None):
        """生成视频"""
        if theme_idx is None:
            theme_idx = random.randint(0, len(THEMES) - 1)

        theme = THEMES[theme_idx]
        print(f"📹 主题: {theme['主题名称']}")

        # 随机配色
        palettes = [
            [(66, 133, 244), (15, 32, 39)],
            [(233, 30, 99), (103, 58, 183)],
            [(255, 87, 34), (255, 193, 7)],
            [(0, 150, 136), (0, 96, 100)],
        ]
        bg_colors = random.choice(palettes)

        # 创建背景
        bg = self.create_bg(*bg_colors)
        bg_path = f"{self.output_dir}/temp_bg.png"
        bg.save(bg_path)

        clips = []
        scenes = theme['场景描述']

        for i, scene in enumerate(scenes):
            print(f"  场景 {i+1}/{len(scenes)}")

            # 提取场景文字（去掉编号）
            scene_text = scene.split('.', 1)[1].strip() if '.' in scene else scene
            # 限制长度
            if len(scene_text) > 30:
                scene_text = scene_text[:30] + "..."

            duration = 3
            frame_count = int(duration * self.fps)
            frames_dir = f"{self.output_dir}/temp_frames_{i}"
            os.makedirs(frames_dir, exist_ok=True)

            for frame_idx in range(frame_count):
                progress = min(1.0, (frame_idx / frame_count) * 2)
                frame = self.add_text(bg, scene_text, progress)
                frame.save(os.path.join(frames_dir, f"frame_{frame_idx:04d}.png"))

            clip = ImageSequenceClip(frames_dir, fps=self.fps)
            clips.append(clip)

            # 清理
            for f in os.listdir(frames_dir):
                os.remove(os.path.join(frames_dir, f))
            os.rmdir(frames_dir)

        # 合并
        print("🎬 合并...")
        final = concatenate_videoclips(clips, method="compose")

        # 导出
        output_path = f"{self.output_dir}/{theme['主题名称']}_v4.mp4"
        print(f"💾 导出: {output_path}")
        final.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            bitrate='2000k',
            preset='medium'
        )

        # 清理
        os.remove(bg_path)

        print(f"✅ 完成！{final.duration:.1f}秒")
        return output_path

if __name__ == "__main__":
    generator = VideoGeneratorV4()
    # 随机生成一个主题
    output = generator.generate_video()
    print(f"\n输出: {output}")
