#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import traceback
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
from src.core.rag_system import RAGSystem
from src.core.session_manager import SessionManager

# 创建 FastAPI 应用
app = FastAPI(title="周棋洛 AI 助手 API", description="API for 周棋洛 AI 助手")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 RAGSystem 实例
rag_system = RAGSystem()

# 创建会话管理器
session_manager = SessionManager()

# 请求模型
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    stream: bool = False
    session_id: Optional[str] = None

# 响应模型
class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    session_id: str

# 会话请求模型
class SessionRequest(BaseModel):
    session_id: Optional[str] = None

# 会话列表响应模型
class SessionListResponse(BaseModel):
    sessions: List[Dict[str, Any]]
    current_session_id: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "周棋洛 AI 助手 API 已启动"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 获取或创建会话
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.get_current_session_id()
            if not session_id:
                session_id = session_manager.create_session()
        session_manager.set_current_session(session_id)
        
        # 提取用户最后一条消息
        user_messages = [msg for msg in request.messages if msg.get('role') == 'user']
        if not user_messages:
            return JSONResponse(
                status_code=200,
                content={
                    "response": "未找到用户消息", 
                    "tool_calls": None,
                    "session_id": session_id
                }
            )
        
        user_input = user_messages[-1].get('content', '')
        print(f"处理用户输入: {user_input}")
        
        # 保存用户消息到会话
        last_message = user_messages[-1]
        session_manager.save_message(session_id, last_message)
        
        # 直接使用 try-except 调用 RAG 系统处理用户查询
        try:
            # 调用 RAG 系统并捕获输出
            import io
            from contextlib import redirect_stdout
            
            # 捕获标准输出
            f = io.StringIO()
            with redirect_stdout(f):
                result = rag_system.query(user_input, use_history=True)
            
            # 获取标准输出内容
            output = f.getvalue()
            
            # 如果 result 为 None，但有打印输出，则使用打印的内容
            if result is None and output:
                response = output
            else:
                response = str(result) if result is not None else "RAG 系统没有返回答案"
                
            print(f"RAG 系统返回: {response}")
            
            # 保存助手回复到会话
            assistant_message = {
                "role": "assistant",
                "content": response
            }
            session_manager.save_message(session_id, assistant_message)
            
            return JSONResponse(
                status_code=200,
                content={
                    "response": response, 
                    "tool_calls": None,
                    "session_id": session_id
                }
            )
        except Exception as e:
            # 获取详细的错误堆栈
            error_details = traceback.format_exc()
            error_msg = f"调用 RAG 系统时出错: {str(e)}\n{error_details}"
            print(error_msg, file=sys.stderr)
            
            return JSONResponse(
                status_code=200,  # 使用 200 而不是 500，以便前端能够正常显示错误消息
                content={
                    "response": error_msg, 
                    "tool_calls": None,
                    "session_id": session_id
                }
            )
            
    except Exception as e:
        # 获取详细的错误堆栈
        error_details = traceback.format_exc()
        error_msg = f"处理请求时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        
        return JSONResponse(
            status_code=200,  # 使用 200 而不是 500，以便前端能够正常显示错误消息
            content={
                "response": error_msg, 
                "tool_calls": None,
                "session_id": session_manager.get_current_session_id() or ""
            }
        )

@app.post("/sessions/create")
async def create_session():
    """创建新会话"""
    try:
        session_id = session_manager.create_session()
        return {
            "status": "success", 
            "session_id": session_id,
            "session": {
                "id": session_id,
                "title": "新会话",
                "messages": []
            }
        }
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"创建会话时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": error_msg}
        )

@app.post("/sessions/list", response_model=SessionListResponse)
async def list_sessions():
    """获取会话列表"""
    try:
        sessions = session_manager.get_sessions()
        current_session_id = session_manager.get_current_session_id()
        return {
            "sessions": sessions,
            "current_session_id": current_session_id
        }
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"获取会话列表时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        return JSONResponse(
            status_code=200,
            content={"sessions": [], "current_session_id": None}
        )

@app.post("/sessions/get")
async def get_session(request: SessionRequest):
    """获取指定会话的消息"""
    try:
        session_id = request.session_id
        if not session_id:
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "未提供会话ID"}
            )
        
        messages = session_manager.get_session(session_id)
        return {
            "status": "success", 
            "session_id": session_id,
            "messages": messages
        }
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"获取会话消息时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": error_msg}
        )

@app.post("/sessions/delete")
async def delete_session(request: SessionRequest):
    """删除会话"""
    try:
        session_id = request.session_id
        if not session_id:
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "未提供会话ID"}
            )
        
        success = session_manager.delete_session(session_id)
        if success:
            return {"status": "success", "message": "会话已删除"}
        else:
            return {"status": "error", "message": "删除会话失败"}
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"删除会话时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": error_msg}
        )

@app.post("/sessions/set_current")
async def set_current_session(request: SessionRequest):
    """设置当前会话"""
    try:
        session_id = request.session_id
        if not session_id:
            return JSONResponse(
                status_code=200,
                content={"status": "error", "message": "未提供会话ID"}
            )
        
        success = session_manager.set_current_session(session_id)
        if success:
            return {"status": "success", "message": "当前会话已设置"}
        else:
            return {"status": "error", "message": "设置当前会话失败"}
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"设置当前会话时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": error_msg}
        )

@app.post("/clear_history")
async def clear_history():
    """清空对话历史"""
    try:
        # 创建新会话而不是清空当前会话
        session_id = session_manager.create_session()
        return {"status": "success", "message": "新会话已创建", "session_id": session_id}
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = f"清空历史时出错: {str(e)}\n{error_details}"
        print(error_msg, file=sys.stderr)
        
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": error_msg}
        )

@app.get("/tools")
async def get_tools():
    """获取所有可用工具的列表"""
    return {"tools": []}

def start_server():
    """启动 API 服务器"""
    uvicorn.run("src.backend.api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    start_server() 