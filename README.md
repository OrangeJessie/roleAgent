# MCP Tools - 大语言模型工具集成系统

MCP Tools（Model Control Protocol Tools）是一个集成了多种工具的大语言模型助手，允许 AI 模型根据需要自动调用各种本地和网络工具，例如查询本地数据库、执行网络搜索以及操作 macOS 应用程序等。

## 功能特点

- **本地向量数据库查询**：可以在本地知识库中进行语义搜索
- **网络搜索**：使用百度搜索引擎检索网络信息
- **macOS 应用程序集成**：可以打开计算器、日历和备忘录等应用
- **类似 ChatGPT 的界面**：用户友好的聊天界面，支持历史会话管理
- **可扩展的工具系统**：易于添加新的工具和功能

## 系统架构

系统由三个主要部分组成：

1. **前端**：基于 HTML、CSS 和 JavaScript 的网页界面，类似 ChatGPT
2. **后端 API**：基于 FastAPI 的 RESTful API，处理请求和响应
3. **Agent**：负责与 OpenAI API 交互并调用工具

## 安装与设置

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件，添加您的 OpenAI API 密钥：

```
OPENAI_API_KEY=your_api_key_here
```

## 使用方法

### 启动应用

```bash
python src/main.py
```

这将同时启动前端和后端服务器，并自动在浏览器中打开应用。

### 命令行选项

- `--no-browser`：不自动打开浏览器
- `--frontend-port PORT`：指定前端服务器端口（默认：8080）
- `--backend-port PORT`：指定后端服务器端口（默认：8000）

示例：

```bash
python src/main.py --frontend-port 3000 --backend-port 5000
```

## 支持的工具

1. **search_local_database**：在本地向量数据库中查询信息
2. **baidu_search**：在百度搜索引擎中查询信息
3. **open_calculator**：打开 macOS 计算器应用
4. **open_calendar**：打开 macOS 日历应用
5. **open_notes**：打开 macOS 备忘录应用并可选择性地创建新笔记

## 扩展工具

要添加新的工具，请修改 `src/core/mcp_tools.py` 文件，添加新的静态方法，然后在 `src/backend/agent.py` 的 `_get_tools` 方法中添加对应的工具定义。

示例：

     ```python
# 在 mcp_tools.py 中添加新工具
@staticmethod
def new_tool(param1, param2):
    """工具的描述"""
    try:
        # 工具的实现
        return {"status": "success", "result": "..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 在 agent.py 的 _get_tools 方法中添加工具定义
{
    "type": "function",
    "function": {
        "name": "new_tool",
        "description": "工具的描述",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数1的描述"
                },
                "param2": {
                    "type": "integer",
                    "description": "参数2的描述"
                }
            },
            "required": ["param1"]
        }
    }
}
```

## 贡献

欢迎提交 Issues 和 Pull Requests 来帮助改进这个项目。

## 许可证

MIT