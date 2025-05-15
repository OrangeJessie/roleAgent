#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_server(port=8000):
    """启动后端 API 服务器"""
    try:
        print(f"正在启动后端服务器，端口: {port}...")
        uvicorn.run("src.backend.api:app", host="127.0.0.1", port=port, reload=True)
    except Exception as e:
        print(f"启动后端服务器时出错: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # 如果直接运行此脚本，则使用默认端口启动服务器
    run_server() 