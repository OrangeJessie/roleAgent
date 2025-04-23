
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.prompts.manager import PromptManager
from retrieve_related import VectorRetriever
import os


# 加载环境变量
load_dotenv()

class RAGSystem:
    def __init__(self, config_path="./config/chinese_fiction.json", user_id=0):
        # 初始化模型
        self.llm = ChatOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="deepseek-r1-distill-qwen-32b"
        )
        
        # 初始化向量数据库
        self.retriever = VectorRetriever(config_path=config_path)
        
        # 初始化prompt管理器
        self.prompt_manager = PromptManager(user_id)
        
    def query(self, question: str, use_history: bool = False):
        """查询系统"""

        # 检索相关文档
        retrieved_docs = self.retriever.retrieve(question)
        
        # 使用prompt管理器格式化prompt
        prompt = self.prompt_manager.get_qa_prompt(
            retrieved_docs=retrieved_docs,
            question=question,
            use_history=use_history
        )
        # print(prompt)
        # self.prompt_manager.add_to_history(question, "测试回答")
        
        调用模型生成回答
        response = self.llm.invoke(prompt)
        
        添加到历史记录
        self.prompt_manager.add_to_history(question, response.content)
        
        return response.content
        