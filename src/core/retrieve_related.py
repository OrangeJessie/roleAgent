import json
import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorRetriever:
    """从 Chroma 向量数据库检索相关内容的类"""
    
    def __init__(self, config_path: str = "./config.json"):
        """
        初始化 VectorRetriever，加载配置并连接 Chroma 数据库
        
        Args:
            config_path (str): 配置文件路径，默认为 ./config.json
        """
        # 加载配置文件
        self.config = self._load_config(config_path)
        
        # 获取配置参数
        self.db_path = self.config["chroma_db_path"]
        self.collection_name = self.config["collection_name"]
        self.embedding_model = self.config["embedding_model"]
        self.max_results = self.config["max_results"]
        
        # 初始化嵌入函数
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model
        )
        # logger.info(f"初始化嵌入模型: {self.embedding_model}")
        
        # 连接 Chroma 数据库
        self.client = self._connect_to_chroma()
        
        # 获取集合
        self.collection = self._get_collection()

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            # logger.info(f"成功加载配置文件: {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"配置文件格式错误: {config_path}")
            raise

    def _connect_to_chroma(self) -> chromadb.Client:
        """连接到 Chroma 数据库"""
        try:
            client = chromadb.PersistentClient(path=self.db_path)
            # logger.info(f"成功连接到 Chroma 数据库: {self.db_path}")
            return client
        except Exception as e:
            logger.error(f"连接 Chroma 数据库失败: {e}")
            raise

    def _get_collection(self) -> chromadb.Collection:
        """获取 Chroma 集合"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            # logger.info(f"成功获取集合: {self.collection_name}")
            return collection
        except Exception as e:
            logger.error(f"获取集合失败: {e}")
            raise

    def retrieve(self, query: str) -> list:
        """
        从 Chroma 数据库检索与查询相关的文本内容
        
        Args:
            query (str): 查询文本
            
        Returns:
            list: 包含检索结果的列表，每个元素为 dict，包含 text、metadata、distance
        """
        try:
            # 生成查询嵌入
            model = SentenceTransformer(self.embedding_model)
            query_embedding = model.encode([query])[0].tolist()
            # logger.info(f"生成查询嵌入，维度: {len(query_embedding)}")

            # 执行检索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=self.max_results,
                include=["documents", "metadatas", "distances"]
            )

            # 格式化结果
            retrieved_content = []
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                retrieved_content.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": dist
                })
            
            # logger.info(f"检索到 {len(retrieved_content)} 条相关内容")
            return retrieved_content

        except Exception as e:
            logger.error(f"检索失败: {e}")
            raise
