# roleAgent

一个基于 RAG（检索增强生成）的智能问答系统，支持向量检索、LLM 生成、对话历史持久化和归档。

## 主要功能
- 支持基于 Chroma 向量数据库的文档检索
- 集成大语言模型（如 deepseek-r1-distill-qwen-32b）进行智能问答
- 支持多轮对话历史管理与持久化
- 历史记录可归档，便于溯源和分析
- 命令行交互，可随时清空历史并归档

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明
- 请在项目根目录下配置 `.env` 文件，填写 API KEY 等环境变量
- 默认使用 `config/chinese_fiction.json` 作为检索配置文件
- 向量数据库目录为 `chroma_db/`

## 使用方法

### 命令行交互

运行测试脚本：

```bash
python src/core/test.py
```

- 输入你的问题，系统会自动检索相关文档并生成回答
- 输入 `clear` 可清空当前历史并自动归档历史文件
- 历史文件保存在 `resources/history/{user_id}/` 目录下，每次清空自动归档为时间戳文件，当前历史为 `current.json`

### 代码调用

可通过 `RAGSystem` 和 `PromptManager` 进行自定义集成，示例见 `src/core/rag_system.py` 和 `src/core/test.py`

## 历史管理说明
- 历史记录自动持久化，支持多用户隔离
- 每次清空历史时，自动将当前历史归档为带时间戳的 JSON 文件
- 历史文件便于后续分析和追溯

## 目录结构简述
```
roleAgent/
├── src/
│   ├── core/
│   │   ├── rag_system.py
│   │   ├── retrieve_related.py
│   │   └── test.py
│   ├── prompts/
│   │   ├── manager.py
│   │   ├── templates.py
│   │   └── test.py
├── config/
│   └── chinese_fiction.json
├── resources/
│   └── history/
├── chroma_db/
├── requirements.txt
├── .env
└── README.md
```

## 相关依赖
- langchain
- chromadb
- sentence-transformers
- langchain-openai
- dotenv

## 贡献与反馈
如需定制功能、反馈 bug 或贡献代码，欢迎 issue 或 PR。