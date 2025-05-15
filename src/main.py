#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import threading
import webbrowser
import time
import http.server
import socketserver
import uvicorn
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_env():
    """检查必要的环境变量是否设置"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("错误: 未设置 OPENAI_API_KEY 环境变量")
        print("请在项目根目录下创建 .env 文件并设置 OPENAI_API_KEY=your_api_key_here")
        return False
    return True

def start_frontend_server(frontend_dir, port=8080):
    """启动前端静态文件服务器"""
    os.chdir(frontend_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"前端服务器已启动: http://localhost:{port}")
        httpd.serve_forever()

def start_backend_server(port=8000):
    """启动后端 API 服务器"""
    # 不再直接在当前线程启动 uvicorn
    # 而是启动一个单独的进程运行后端服务器
    try:
        # 使用 Python 的 subprocess 模块启动一个新进程
        cmd = [sys.executable, "-m", "src.backend.server_runner"]
        backend_process = subprocess.Popen(cmd)
        print(f"后端服务器已启动: http://localhost:{port}")
        return backend_process
    except Exception as e:
        print(f"启动后端服务器时出错: {e}")
        sys.exit(1)

def open_browser(url, delay=1.5):
    """延迟打开浏览器"""
    time.sleep(delay)
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="小松 AI 助手启动器")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--frontend-port", type=int, default=8080, help="前端服务器端口")
    parser.add_argument("--backend-port", type=int, default=8000, help="后端服务器端口")
    args = parser.parse_args()
    
    # 检查环境变量
    if not check_env():
        sys.exit(1)
    
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.absolute()
    frontend_dir = root_dir / "src" / "frontend"
    
    # 确保目录存在
    if not frontend_dir.exists():
        print(f"错误: 前端目录不存在: {frontend_dir}")
        sys.exit(1)
    
    print(f"项目根目录: {root_dir}")
    print(f"前端目录: {frontend_dir}")
    
    # 启动后端服务器（在单独的进程中）
    backend_process = start_backend_server(args.backend_port)
    
    # 启动前端服务器（在新线程中）
    frontend_thread = threading.Thread(target=start_frontend_server, args=(frontend_dir, args.frontend_port), daemon=True)
    frontend_thread.start()
    
    # 打开浏览器
    if not args.no_browser:
        browser_thread = threading.Thread(target=open_browser, args=(f"http://localhost:{args.frontend_port}",), daemon=True)
        browser_thread.start()
    
    print("小松 AI 助手已启动")
    print(f"前端地址: http://localhost:{args.frontend_port}")
    print(f"后端地址: http://localhost:{args.backend_port}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        # 终止后端服务器进程
        if backend_process:
            backend_process.terminate()
            backend_process.wait()  # 等待进程结束
        sys.exit(0)

if __name__ == "__main__":
    main() 