from langchain.prompts import PromptTemplate
from typing import List, Dict
from src.prompts.templates import SYSTEM_PROMPT, USER_PROMPTS, CONTEXT_TEMPLATE, QA_TEMPLATE, HISTORY_TEMPLATE
import os
import json
import datetime

class PromptManager:

    def __init__(self, user_id: int = 0):
        self.user_id = user_id
        self.history_dir = f"resources/history/{self.user_id}"
        self.current_history_file = os.path.join(self.history_dir, "current.json")
        self.history = self._load_history()
        
        # 初始化模板
        self.context_template = PromptTemplate(
            input_variables=["context"],
            template=CONTEXT_TEMPLATE
        )
        
        self.qa_template = PromptTemplate(
            input_variables=["system_prompt", "context_template", "question", "user_prompt"],
            template=QA_TEMPLATE
        )
        
        self.history_template = PromptTemplate(
            input_variables=["history", "question"],
            template=HISTORY_TEMPLATE
        )

    def _load_history(self):
        if os.path.exists(self.current_history_file):
            try:
                with open(self.current_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self):
        os.makedirs(self.history_dir, exist_ok=True)
        with open(self.current_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

        
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """格式化检索到的文档和用户信息"""
        context = ""
        if not retrieved_docs:
            return ""
        for doc in retrieved_docs:
            context += f"{doc['text']}\n\n"
            
        return self.context_template.format(
            context=context.strip(),
        )
        
    def get_user_prompt(self) -> str:
        """获取用户特定的提示词"""
        user_prompt = USER_PROMPTS.get(self.user_id, USER_PROMPTS[0])
        return "\n".join([
            user_prompt["style"],
            user_prompt["constraints"]
        ])
        
    def add_to_history(self, question: str, answer: str):
        """添加对话到历史记录，并持久化保存"""
        self.history.append(f"Q: {question}\nA: {answer}")
        # 保持历史记录长度
        if len(self.history) > 5:  # 只保留最近5轮对话
            self.history = self.history[-5:]
        self._save_history()
            
    def format_history(self, question: str) -> str:
        """格式化历史对话"""
        history_str = "\n\n".join(self.history)
        return self.history_template.format(
            history=history_str,
            question=question
        )
        
    def get_qa_prompt(
        self,
        retrieved_docs: List[Dict],
        question: str,
        use_history: bool = False
    ) -> str:
        """获取完整的问答prompt"""
        # 格式化上下文
        context_str = self.format_context(retrieved_docs)
        
        # 获取用户特定提示词
        user_prompt = self.get_user_prompt()
        # 如果需要使用历史对话
        if use_history and self.history:
            question = self.format_history(question)
            
        # 生成最终prompt
        return self.qa_template.format(
            system_prompt=SYSTEM_PROMPT,
            context_template=context_str,
            question=question,
            user_prompt=user_prompt
        )


    def clear_history(self):
        """清空历史对话并归档当前历史文件，新建空历史文件"""
        # 归档当前历史文件
        if os.path.exists(self.current_history_file):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = os.path.join(self.history_dir, f"{timestamp}.json")
            os.rename(self.current_history_file, archive_file)
        # 新建空历史
        self.history = []
        self._save_history()