#!/usr/bin/env python3
"""
通用服务监控守护脚本
- 监控多个服务的健康状态
- 自动拉起掉线服务
- 记录日志
"""

import json
import subprocess
import requests
import time
import os
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "monitor_config.json"
LOG_PATH = Path(__file__).parent / "monitor.log"

def load_config():
    """加载监控配置"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"services": {}}

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(LOG_PATH, 'a') as f:
        f.write(log_entry + "\n")

def check_http_service(name, url, timeout=5):
    """检查HTTP服务是否存活"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def check_process(pid_file):
    """检查进程是否存在"""
    if not os.path.exists(pid_file):
        return False
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # 发送信号0检查进程是否存在
        os.kill(pid, 0)
        return True
    except:
        return False

def start_service(service):
    """启动服务"""
    name = service["name"]
    workdir = service.get("workdir", "/tmp")
    command = service["command"]
    
    log(f"🚀 启动服务: {name}")
    
    try:
        os.chdir(workdir)
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(2)  # 等待启动
        return True
    except Exception as e:
        log(f"❌ 启动失败: {name} - {e}")
        return False

def monitor_service(service):
    """监控单个服务"""
    name = service["name"]
    check_type = service.get("check_type", "http")
    max_retries = service.get("max_retries", 3)
    auto_restart = service.get("auto_restart", True)
    
    # 检查服务状态
    is_alive = False
    
    if check_type == "http":
        url = service.get("check_url")
        if url:
            is_alive = check_http_service(name, url)
    elif check_type == "process":
        pid_file = service.get("pid_file")
        if pid_file:
            is_alive = check_process(pid_file)
    
    if is_alive:
        log(f"✅ {name} 运行正常")
        return True
    else:
        log(f"❌ {name} 已掉线")
        
        if auto_restart:
            for i in range(max_retries):
                log(f"🔄 尝试重启 {name} ({i+1}/{max_retries})")
                if start_service(service):
                    # 再次检查
                    time.sleep(3)
                    if check_type == "http":
                        is_alive = check_http_service(name, service.get("check_url"))
                    elif check_type == "process":
                        is_alive = check_process(service.get("pid_file"))
                    
                    if is_alive:
                        log(f"✅ {name} 重启成功")
                        return True
            
            log(f"❌ {name} 重启失败，已尝试 {max_retries} 次")
            return False
    
    return is_alive

def main():
    config = load_config()
    services = config.get("services", [])
    
    if not services:
        log("⚠️ 没有配置任何服务")
        return
    
    log("=" * 50)
    log(f"🔍 开始监控 {len(services)} 个服务")
    log("=" * 50)
    
    results = {}
    for service in services:
        name = service["name"]
        results[name] = monitor_service(service)
    
    # 汇总
    alive = sum(1 for v in results.values() if v)
    dead = len(results) - alive
    
    log("-" * 50)
    log(f"📊 监控完成: {alive} 个运行中, {dead} 个异常")
    log("-" * 50)

if __name__ == "__main__":
    main()
