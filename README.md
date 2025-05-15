# 周棋洛智能助手

本项目是一个本地可运行的多工具大语言模型助手，支持本地知识库检索、网络搜索、macOS 应用集成，并拥有美观的莫兰迪风格前端界面和多会话管理能力。

## 功能亮点

- **本地向量数据库检索**：可选开关，支持语义搜索本地知识库
- **网络搜索**：集成百度搜索
- **macOS 应用集成**：一键打开计算器、日历、备忘录等
- **多会话管理**：支持新建、切换、删除会话，历史自动保存
- **现代化前端**：莫兰迪灰黑色风格，气泡式聊天，支持头像、流畅体验
- **可扩展工具系统**：便于添加自定义工具

## 系统架构

- **前端**：HTML/CSS/JS，响应式聊天界面，支持会话管理和数据库检索开关
- **后端**：FastAPI 提供 RESTful API
- **RAG/Agent**：支持本地知识库、外部API、工具调用

## 安装与启动

1. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量（如需 OpenAI/阿里云API）

   ```
   OPENAI_API_KEY=your_api_key_here
   DASHSCOPE_API_KEY=your_dashscope_key
   ```

3. 启动应用

   ```bash
   python src/main.py
   ```

   默认会自动打开浏览器访问前端页面。

4. 命令行参数

   - `--no-browser`：不自动打开浏览器
   - `--frontend-port PORT`：指定前端端口（默认8080）
   - `--backend-port PORT`：指定后端端口（默认8000）

## 使用说明

- 聊天界面支持多会话，历史自动保存
- 输入框旁可切换"检索数据库"开关，决定是否启用本地知识库
- 支持发送多轮对话，AI助手可自动调用本地/网络工具
- 会话历史保存在 `resources/default_history/` 目录下

## 扩展工具

如需添加新工具，修改 `src/core/mcp_tools.py`，并在后端注册即可。

示例：

```python
# mcp_tools.py
@staticmethod
def new_tool(param1):
    # 工具实现
    return {"status": "success", "result": "xxx"}
```

## 界面示例

- 莫兰迪灰黑色输入区
- 气泡式对话，头像可自定义
- 支持会话切换与删除

## 贡献

欢迎提交 Issue 或 PR 参与改进！

## 许可证

MIT