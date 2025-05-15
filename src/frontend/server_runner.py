#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.server
import socketserver
from pathlib import Path

def run_server(port=8080):
    """启动前端静态文件服务器"""
    # 获取前端目录的绝对路径
    current_dir = Path(__file__).parent.absolute()
    os.chdir(current_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"前端服务器已启动: http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n正在关闭前端服务器...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server() 