from retrieve_related import VectorRetriever
from src.core.rag_system import RAGSystem
import warnings
warnings.filterwarnings("ignore")


def main():
    """测试 VectorRetriever 类"""
    # 初始化检索器
    # retriever = VectorRetriever(config_path="./config/chinese_fiction.json")
    
    rs = RAGSystem()
    while True:
        user_input = input("请输入问题（输入 clear 清空历史）：")
        if user_input.lower() == 'clear':
            rs.prompt_manager.clear_history()
            print("历史已清空并归档！")
            continue
        response = rs.query(user_input, use_history=True)
        print(response)


if __name__ == "__main__":
    main()