#!/usr/bin/env python3
"""
短视频自动训练系统
自动迭代、评估、优化
"""

import os
import json
import subprocess
from datetime import datetime

TRAINING_LOG = "/Users/syj/.openclaw/workspace/video_training/training_log.json"

class AutoTrainer:
    def __init__(self):
        self.log_file = TRAINING_LOG
        self.load_log()

    def load_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file) as f:
                self.log = json.load(f)
        else:
            self.log = {
                "iterations": [],
                "best_version": None,
                "best_score": 0,
                "started_at": datetime.now().isoformat()
            }

    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

    def evaluate_video(self, video_path):
        """评估视频质量（自动化指标）"""
        # 获取视频信息
        cmd = f"ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of json {video_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        try:
            info = json.loads(result.stdout)
            duration = float(info['format']['duration'])
            size = int(info['format']['size'])
            width = int(info['streams'][0]['width'])
            height = int(info['streams'][0]['height'])
            fps = eval(info['streams'][0]['r_frame_rate'])

            # 计算评分
            score = 0

            # 1. 时长评分（理想15-60秒）
            if 15 <= duration <= 60:
                score += 20
            elif 10 <= duration <= 90:
                score += 10

            # 2. 分辨率评分
            if width == 1080 and height == 1920:
                score += 20  # 完美的竖屏
            elif width >= 720:
                score += 10

            # 3. 帧率评分
            if fps >= 30:
                score += 20
            elif fps >= 24:
                score += 10

            # 4. 文件大小评分（压缩效率）
            bytes_per_second = size / duration
            if 5000 <= bytes_per_second <= 20000:  # 合理范围
                score += 20
            elif bytes_per_second < 50000:
                score += 10

            # 5. 加分项（需要人工评估或高级算法）
            # - 有背景音乐：+10
            # - 有动画效果：+10
            # - 有配音：+10
            # 暂时跳过，后续可通过AI分析

            return {
                "score": score,
                "duration": duration,
                "size": size,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "bytes_per_second": bytes_per_second
            }
        except Exception as e:
            return {"score": 0, "error": str(e)}

    def run_iteration(self, version, script_path):
        """运行一次迭代"""
        print(f"\n{'='*60}")
        print(f"迭代版本: v{version}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # 运行脚本生成视频
        result = subprocess.run(
            f"source video_env/bin/activate && python {script_path}",
            shell=True,
            cwd="/Users/syj/.openclaw/workspace",
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ 生成失败:\n{result.stderr}")
            return None

        # 找到生成的视频
        output_dir = "/Users/syj/.openclaw/workspace/video_training/output"
        videos = [f for f in os.listdir(output_dir) if f.endswith(f'_v{version}.mp4')]

        if not videos:
            print("❌ 未找到生成的视频")
            return None

        video_path = os.path.join(output_dir, videos[0])
        print(f"\n📹 评估视频: {videos[0]}")

        # 评估视频
        eval_result = self.evaluate_video(video_path)

        # 记录结果
        iteration = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "video": videos[0],
            "evaluation": eval_result,
            "script": script_path
        }

        self.log["iterations"].append(iteration)

        # 更新最佳版本
        if eval_result["score"] > self.log["best_score"]:
            self.log["best_version"] = version
            self.log["best_score"] = eval_result["score"]
            print(f"🏆 新的最佳版本！评分: {eval_result['score']}/100")

        self.save_log()

        print(f"\n📊 评估结果:")
        print(f"  评分: {eval_result['score']}/100")
        print(f"  时长: {eval_result['duration']:.1f}秒")
        print(f"  大小: {eval_result['size']/1024:.1f}KB")
        print(f"  分辨率: {eval_result['resolution']}")
        print(f"  帧率: {eval_result['fps']}fps")

        return eval_result

    def get_next_version(self):
        """获取下一个版本号"""
        if not self.log["iterations"]:
            return 1
        return max(i["version"] for i in self.log["iterations"]) + 1

    def summary(self):
        """训练总结"""
        print(f"\n{'='*60}")
        print("训练总结")
        print(f"{'='*60}")
        print(f"总迭代次数: {len(self.log['iterations'])}")
        print(f"最佳版本: v{self.log['best_version']}")
        print(f"最高评分: {self.log['best_score']}/100")
        print(f"\n版本演进:")
        for i in self.log["iterations"]:
            print(f"  v{i['version']}: {i['evaluation']['score']}/100 - {i['video']}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    trainer = AutoTrainer()

    # 测试评估现有视频
    test_video = "/Users/syj/.openclaw/workspace/video_training/output/扎心真相_v1.mp4"
    if os.path.exists(test_video):
        print("测试评估 v1 视频...")
        result = trainer.evaluate_video(test_video)
        print(f"评分: {result}")
