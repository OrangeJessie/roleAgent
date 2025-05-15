#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class SessionManager:
    """管理用户对话会话"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.base_dir = Path("resources/default_history")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id = None
        self.sessions = self._load_sessions()
    
    def _load_sessions(self) -> List[Dict[str, Any]]:
        """加载所有现有会话"""
        sessions = []
        for file_path in sorted(self.base_dir.glob("*.json"), reverse=True):
            try:
                session_id = file_path.stem
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    
                # 提取标题 (第一个用户消息，如果存在的话)
                title = "新会话"
                if content and len(content) > 0:
                    for msg in content:
                        if msg.get('role') == 'user':
                            title = msg.get('content', '')[:30]
                            if len(msg.get('content', '')) > 30:
                                title += "..."
                            break
                
                # 格式化时间作为可读的会话时间
                try:
                    timestamp = int(session_id.split('_')[0])
                    formatted_time = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                except (ValueError, IndexError):
                    formatted_time = file_path.stem  # 回退到文件名
                
                sessions.append({
                    "id": session_id,
                    "title": title,
                    "time": formatted_time,
                    "path": str(file_path)
                })
            except Exception as e:
                print(f"加载会话 {file_path} 时出错: {e}")
                
        return sessions
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话的列表"""
        return self.sessions
    
    def create_session(self) -> str:
        """创建新的会话"""
        timestamp = int(time.time())
        session_id = f"{timestamp}_{os.urandom(4).hex()}"
        file_path = self.base_dir / f"{session_id}.json"
        
        # 初始化空会话
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        # 添加到会话列表
        self.sessions.insert(0, {
            "id": session_id,
            "title": "新会话",
            "time": datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M"),
            "path": str(file_path)
        })
        
        self.current_session_id = session_id
        return session_id
    
    def get_session(self, session_id: str) -> List[Dict[str, str]]:
        """获取指定会话的内容"""
        for session in self.sessions:
            if session["id"] == session_id:
                file_path = Path(session["path"])
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"读取会话 {session_id} 时出错: {e}")
                    return []
        return []
    
    def save_message(self, session_id: str, message: Dict[str, str]) -> bool:
        """保存消息到会话"""
        # 查找会话
        session_path = None
        for session in self.sessions:
            if session["id"] == session_id:
                session_path = Path(session["path"])
                break
        
        if not session_path:
            print(f"未找到会话 {session_id}")
            return False
        
        # 读取当前消息
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except Exception:
            messages = []
        
        # 添加新消息
        messages.append(message)
        
        # 保存回文件
        try:
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # 如果这是第一条用户消息，更新标题
            if message.get('role') == 'user' and (len(messages) <= 2):
                for i, session in enumerate(self.sessions):
                    if session["id"] == session_id:
                        content = message.get('content', '')
                        title = content[:30] + ("..." if len(content) > 30 else "")
                        self.sessions[i]["title"] = title
                        break
            
            return True
        except Exception as e:
            print(f"保存消息到会话 {session_id} 时出错: {e}")
            return False
    
    def set_current_session(self, session_id: str) -> bool:
        """设置当前会话"""
        for session in self.sessions:
            if session["id"] == session_id:
                self.current_session_id = session_id
                return True
        return False
    
    def get_current_session_id(self) -> Optional[str]:
        """获取当前会话ID"""
        return self.current_session_id
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        for i, session in enumerate(self.sessions):
            if session["id"] == session_id:
                file_path = Path(session["path"])
                try:
                    if file_path.exists():
                        file_path.unlink()
                    self.sessions.pop(i)
                    
                    # 如果删除的是当前会话，重置当前会话
                    if self.current_session_id == session_id:
                        self.current_session_id = None
                    
                    return True
                except Exception as e:
                    print(f"删除会话 {session_id} 时出错: {e}")
                    return False
        return False 