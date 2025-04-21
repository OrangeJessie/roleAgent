from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json
import os, re
from typing import List, Optional, Dict, Any, Tuple

class ChromaVectorStore:
    """
    使用 Hugging Face 模型和 Chroma 数据库管理文本向量的类。
    支持从文件加载长文本、按 chunk 切分、生成向量、存储到 Chroma，以及查询相似文本。
    配置通过 JSON 文件或参数指定。
    """
    
    def __init__(
        self,
        config_file: str = "config.json",
        collection_name: Optional[str] = None,
        model_name: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """
        初始化 ChromaVectorStore，加载配置并设置模型和数据库。

        参数:
            config_file (str): 配置文件路径，默认为 "config.json"。
            collection_name (Optional[str]): Chroma 集合名称，覆盖配置文件值。
            model_name (Optional[str]): Hugging Face 模型名称，覆盖配置文件值。
            db_path (Optional[str]): Chroma 数据库存储路径，覆盖配置文件值。
        """
        
        # 加载配置文件
        self.config = self._load_config(config_file)

        # 设置配置项，优先级：参数 > 配置文件 > 默认值
        self.collection_name = (
            collection_name
            or self.config.get("vector_store", {}).get("collection_name", "default_collection")
        )
        self.model_name = (
            model_name
            or self.config.get("vector_store", {}).get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
        )
        self.db_path = (
            db_path
            or self.config.get("vector_store", {}).get("db_path", "./chroma_db")
        )
        self.chunk_size = self.config.get("vector_store", {}).get("chunk_size", 500)
        self.chunk_overlap = self.config.get("vector_store", {}).get("chunk_overlap", 50)

        # 初始化 Hugging Face 嵌入模型
        self.model = SentenceTransformer(self.model_name)
        
        # 初始化 Chroma 数据库（本地持久化存储）
        self.client = chromadb.PersistentClient(path=self.db_path, settings=Settings())
        
        # 创建或获取集合
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            self.collection = self.client.create_collection(name=self.collection_name)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """
        加载 JSON 配置文件。如果文件不存在，返回空字典。
        """
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        print(f"Warning: Config file '{config_file}' not found. Using default values.")
        return {}

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        将长文本按指定大小切分为 chunks，支持重叠。
        参数: text (str): 输入文本。
        返回: List[str]: 切分后的 chunk 列表。
        """
        # 按段落（双换行）或句子（句号、叹号、问号）切分
        chunks = []
        current_chunk = ""
        sentences = re.split(r'([。！？\n])', text)  # 保留标点
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
            sentence_with_delimiter = sentence + delimiter
            if len(current_chunk) + len(sentence_with_delimiter) <= self.chunk_size:
                current_chunk += sentence_with_delimiter
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence_with_delimiter
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def store_texts_from_file(self, input_file: Optional[str] = None, add_batch_size: int = 500) -> int:
        """
        从文本文件读取长文本，按 chunk 切分，分批生成向量并分批存储到 Chroma 集合。

        参数:
            input_file (Optional[str]): 输入文本文件路径，默认为配置文件中的 default_input_file。
            add_batch_size (int): 存储到 Chroma 集合时的批处理大小。

        返回:
            int: 存储的 chunk 数量。
        """
        input_file = input_file or self.config.get("vector_store", {}).get("default_input_file", "book.txt")

        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                text = file.read()
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            return 0
        except UnicodeDecodeError:
            print(f"Error: File '{input_file}' is not UTF-8 encoded.")
            return 0

        if not text.strip():
            print("Warning: Input file is empty.")
            return 0

        chunks = self._split_text_into_chunks(text)
        num_chunks = len(chunks)
        if not chunks:
            print("Warning: No valid chunks generated.")
            return 0

        for i in range(0, num_chunks, add_batch_size):
            batch_chunks = chunks[i:i + add_batch_size]
            ids = [str(i + j + 1) for j in range(len(batch_chunks))]

            try:
                embeddings = self.model.encode(batch_chunks, batch_size=32).tolist()
                self.collection.add(
                    embeddings=embeddings,
                    documents=batch_chunks,
                    ids=ids
                )
                print(f"Processed and stored chunks {i+1} to {min(i + add_batch_size, num_chunks)}")
            except Exception as e:
                print(f"Error processing and storing batch {i // add_batch_size + 1}: {e}")
                return i  # 返回已成功存储的 chunk 数量

        print(f"Successfully stored {num_chunks} chunks in collection '{self.collection_name}' from '{input_file}'.")
        return num_chunks

    def query_similar_texts(self, query_text: str, n_results: int = 2) -> List[dict]:
        """
        查询与输入文本语义相似的 chunks。
        参数:
            query_text (str): 查询文本。
            n_results (int): 返回的相似 chunk 数量，默认为 2。
        返回:
            List[dict]: 包含相似 chunk、ID 和相似度分数的列表。
        """
        # 生成查询文本的向量
        try:
            query_embedding = self.model.encode([query_text]).tolist()[0]
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return []

        # 执行查询
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # 格式化查询结果
        formatted_results = [
            {
                "id": id,
                "text": doc,
                "similarity_score": distance  # 转换为相似度（1 - 余弦距离）
            }
            for id, doc, distance in zip(
                results["ids"][0], results["documents"][0], results["distances"][0]
            )
        ]

        return formatted_results