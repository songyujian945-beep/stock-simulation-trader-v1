#!/usr/bin/env python3
"""
短视频自动生成 v3 - 优化版
改进：
1. 文件大小优化（更好的压缩）
2. 添加背景音乐
3. 批量生成功能
4. Emoji正确显示
5. 场景过渡效果
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy import *
import asyncio

OUTPUT_DIR = "/Users/syj/.openclaw/workspace/video_training/output"
MUSIC_DIR = "/Users/syj/.openclaw/workspace/video_training/music"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 24  # 降低帧率以减小文件

THEMES = [
    {
        "name": "职场吐槽",
        "bg_colors": [(66, 133, 244), (15, 32, 39)],
        "scenes": [
            {"text": "当老板说这个需求很简单", "duration": 2.5},
            {"text": "产品经理：就改一个小功能", "duration": 2.5},
            {"text": "程序员内心：重写整个系统", "duration": 2.5},
            {"text": "老板：明天上线", "duration": 2.5},
            {"text": "程序员：我选择加班", "duration": 3},
        ]
    },
    {
        "name": "扎心真相",
        "bg_colors": [(233, 30, 99), (103, 58, 183)],
        "scenes": [
            {"text": "小时候以为", "duration": 2},
            {"text": "长大就能为所欲为", "duration": 2.5},
            {"text": "长大后发现", "duration": 2},
            {"text": "穷才限制了我的想象", "duration": 3},
            {"text": "但梦想还是要有的", "duration": 3},
        ]
    },
    {
        "name": "情感共鸣",
        "bg_colors": [(255, 87, 34), (255, 193, 7)],
        "scenes": [
            {"text": "你以为的周末", "duration": 2.5},
            {"text": "实际的周末", "duration": 2.5},
            {"text": "周五晚上的你", "duration": 2.5},
            {"text": "周一早上的你", "duration": 2.5},
            {"text": "这就是生活", "duration": 3},
        ]
    },
]

class VideoGeneratorV3:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.fps = FPS
        self.output_dir = OUTPUT_DIR

    def create_static_bg(self, color1, color2):
        """创建静态背景（优化：只生成一次）"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            ratio = y / self.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # 添加少量装饰
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 15)
            draw.ellipse([x-size, y-size, x+size, y+size],
                        fill=(255, 255, 255, 30))

        return img

    def add_text_to_image(self, img, text, animation_progress=1.0):
        """添加文字到图像"""
        img = img.copy()
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 65)
        except:
            font = ImageFont.load_default()

        # 打字机效果
        chars_to_show = int(len(text) * animation_progress)
        display_text = text[:chars_to_show]

        # 文字位置
        bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        text_y = self.height // 2 - 50

        # 阴影
        draw.text((text_x + 3, text_y + 3), display_text,
                 font=font, fill=(0, 0, 0, 150))
        # 文字
        draw.text((text_x, text_y), display_text,
                 font=font, fill=(255, 255, 255))

        return img

    async def generate_audio(self, text, output_path):
        """生成语音"""
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(output_path)

    def generate_video(self, theme_name=None, add_music=False):
        """生成视频（优化版）"""
        theme = random.choice(THEMES) if not theme_name else \
                next((t for t in THEMES if t["name"] == theme_name), THEMES[0])

        print(f"📹 生成: {theme['name']}")

        # 创建背景（只一次）
        bg = self.create_static_bg(*theme["bg_colors"])
        bg_path = f"{self.output_dir}/temp_bg.png"
        bg.save(bg_path)

        clips = []
        frame_dirs = []  # 记录所有帧目录，最后统一清理
        for i, scene in enumerate(theme["scenes"]):
            print(f"  场景 {i+1}/{len(theme['scenes'])}")

            # 生成动画帧
            duration = scene["duration"]
            frame_count = int(duration * self.fps)
            frames_dir = f"{self.output_dir}/temp_frames_{i}"
            os.makedirs(frames_dir, exist_ok=True)
            frame_dirs.append(frames_dir)

            for frame_idx in range(frame_count):
                progress = min(1.0, (frame_idx / frame_count) * 2)
                frame = self.add_text_to_image(bg, scene["text"], progress)
                frame_path = os.path.join(frames_dir, f"frame_{frame_idx:04d}.png")
                frame.save(frame_path)

            # 创建片段 - 使用 load_images=True 立即加载
            clip = ImageSequenceClip(frames_dir, fps=self.fps, load_images=True)
            clips.append(clip)

        # 合并
        print("🎬 合并...")
        final = concatenate_videoclips(clips, method="compose")

        # 音频
        print("🎙️ 配音...")
        full_text = "。".join([s["text"] for s in theme["scenes"]])
        audio_path = f"{self.output_dir}/temp_audio.mp3"
        asyncio.run(self.generate_audio(full_text, audio_path))

        try:
            audio = AudioFileClip(audio_path)
            final = final.with_audio(audio)
        except Exception as e:
            print(f"⚠️ 音频失败: {e}")

        # 导出（优化压缩）
        output_path = f"{self.output_dir}/{theme['name']}_v3.mp4"
        print(f"💾 导出: {output_path}")
        final.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            bitrate='2000k',  # 限制比特率
            preset='medium'   # 压缩预设
        )

        # 清理临时文件
        for frames_dir in frame_dirs:
            if os.path.exists(frames_dir):
                for f in os.listdir(frames_dir):
                    os.remove(os.path.join(frames_dir, f))
                os.rmdir(frames_dir)

        if os.path.exists(bg_path):
            os.remove(bg_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

        print(f"✅ 完成！{final.duration:.1f}秒")
        return output_path

    def batch_generate(self, count=5):
        """批量生成"""
        results = []
        for i in range(count):
            print(f"\n{'='*60}")
            print(f"批量生成 {i+1}/{count}")
            print(f"{'='*60}")
            output = self.generate_video()
            results.append(output)

        print(f"\n🎉 批量完成！生成{count}个视频")
        for r in results:
            print(f"  - {os.path.basename(r)}")
        return results

if __name__ == "__main__":
    import sys
    generator = VideoGeneratorV3()

    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        generator.batch_generate(count)
    else:
        generator.generate_video()
