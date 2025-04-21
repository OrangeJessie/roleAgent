from retrieve_related import VectorRetriever
from src.core.rag_system import RAGSystem

def main():
    """测试 VectorRetriever 类"""
    # 初始化检索器
    # retriever = VectorRetriever(config_path="./config/chinese_fiction.json")
    
    # 示例查询
    # query = "诗社成立" 
    # results = retriever.retrieve(query)
    # print(results)
    
    rs = RAGSystem()
    rs.query("林黛玉什么时候第一次进贾府")


if __name__ == "__main__":
    main()