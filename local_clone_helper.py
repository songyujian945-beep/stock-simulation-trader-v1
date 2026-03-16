#!/usr/bin/env python3
"""
本地分身协作系统
让Ollama本地模型协助OpenClaw处理任务
"""

import requests
import json
import time
from datetime import datetime

OLLAMA_API = "http://localhost:11434/api"

class LocalClone:
    def __init__(self, model="qwen2:7b"):
        self.model = model
        self.api = OLLAMA_API
        
    def chat(self, message, stream=False):
        """与分身对话"""
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "stream": stream
        }
        
        start = time.time()
        response = requests.post(f"{self.api}/chat", json=data)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            return {
                "response": result["message"]["content"],
                "time": elapsed,
                "model": self.model
            }
        else:
            return {"error": response.text, "time": elapsed}
    
    def generate(self, prompt):
        """简单生成"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        start = time.time()
        response = requests.post(f"{self.api}/generate", json=data)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            return {
                "response": result["response"],
                "time": elapsed
            }
        else:
            return {"error": response.text}
    
    def test_capabilities(self):
        """测试分身能力"""
        tests = [
            ("中文对话", "你好，请介绍一下你自己"),
            ("代码生成", "用Python写一个快速排序"),
            ("文案创作", "给一个抖音短视频写3个吸引人的标题，主题是'职场吐槽'"),
            ("创意生成", "给出5个适合抖音的短视频创意"),
            ("数据分析", "分析这个数据的趋势：1,2,2,3,5,8,13,21")
        ]
        
        results = []
        for name, prompt in tests:
            print(f"\n测试: {name}")
            result = self.chat(prompt)
            results.append({
                "test": name,
                "time": result.get("time", 0),
                "success": "error" not in result
            })
            print(f"  耗时: {result.get('time', 0):.2f}秒")
            print(f"  结果: {result.get('response', '')[:100]}...")
        
        return results

# 协作任务分配
TASK_ALLOCATION = {
    "本地分身擅长": [
        "简单对话和问答",
        "批量文案生成",
        "代码片段生成",
        "创意头脑风暴",
        "标题和描述生成"
    ],
    "云端我擅长": [
        "复杂推理和决策",
        "工具调用和执行",
        "文件操作和系统管理",
        "网络搜索和数据获取",
        "长期记忆和上下文理解"
    ]
}

if __name__ == "__main__":
    clone = LocalClone()
    
    print("="*60)
    print("本地分身能力测试")
    print("="*60)
    
    # 测试基本能力
    results = clone.test_capabilities()
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    success_count = sum(1 for r in results if r["success"])
    avg_time = sum(r["time"] for r in results) / len(results)
    
    print(f"通过: {success_count}/{len(results)}")
    print(f"平均耗时: {avg_time:.2f}秒")
    
    print("\n任务分配建议:")
    for category, tasks in TASK_ALLOCATION.items():
        print(f"\n{category}:")
        for task in tasks:
            print(f"  - {task}")
