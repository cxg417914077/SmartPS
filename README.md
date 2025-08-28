# SmartPS - AI 图像处理工具

SmartPS 是一个基于人工智能的图像处理工具，允许用户通过自然语言指令对图像进行各种编辑操作。该项目结合了大型语言模型（LLM）和图像处理工具，为用户提供直观的图像编辑体验。

## 项目结构

```
SmartPS/
├── backend/           # 后端服务
│   ├── main.py        # 主应用入口，包含 FastAPI 服务器和 LangChain Agent
│   ├── mcp/           # MCP 工具服务
│   │   └── server.py  # 图像处理工具（调整大小、裁剪、旋转等）
│   └── ...
├── frontend/          # 前端应用
│   ├── src/           # React + TypeScript 源代码
│   │   ├── pages/     # 页面组件
│   │   ├── components/ # 共享组件
│   │   └── ...
│   └── ...
└── ...
```

## 功能特点

- **AI 驱动的图像编辑**：通过自然语言指令对图像进行编辑，如调整大小、裁剪、旋转等
- **实时流式响应**：后端通过 Server-Sent Events (SSE) 实时返回 Agent 的处理步骤
- **可视化界面**：用户友好的前端界面，可预览输入和输出图像
- **模块化工具设计**：使用 MCP (Model Controller Protocol) 构建可扩展的工具集

## 技术栈

### 后端
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速（高性能）的 Python Web 框架
- [LangChain](https://www.langchain.com/) - 构建 LLM 应用的框架
- [Ollama](https://ollama.ai/) - 在本地运行大型语言模型
- [Pillow](https://python-pillow.org/) - Python 图像处理库
- [MCP](https://github.com/modelcontextprotocol/specification) - 模型上下文协议

### 前端
- [React](https://reactjs.org/) - JavaScript 库，用于构建用户界面
- [TypeScript](https://www.typescriptlang.org/) - JavaScript 的超集，添加了静态类型
- [Vite](https://vitejs.dev/) - 快速的构建工具

## 快速开始

### 后端设置

1. 确保已安装 Python 3.12+
2. 安装依赖：
   ```bash
   pip install -r backend/requirements.txt
   ```
   
3. 启动 MCP 工具服务：
   ```bash
   cd backend/mcp
   python server.py
   ```

4. 在另一个终端启动主应用：
   ```bash
   cd backend
   python main.py
   ```

### 前端设置

1. 确保已安装 Node.js (推荐使用最新 LTS 版本)
2. 安装依赖：
   ```bash
   cd frontend
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run dev
   ```

4. 打开浏览器访问 `http://localhost:5173`

## 使用方法

1. 访问应用主页
2. 点击"立即体验"进入图像处理页面
3. 上传一张图片
4. 输入处理指令，例如：
   - "将图片调整为 500x500 大小"
   - "旋转图片 90 度"
   - "裁剪图片的左上角区域"
5. 点击"运行智能体"开始处理
6. 在输出区域查看处理结果

## 开发

### 添加新工具

工具使用 MCP 协议定义在 [backend/mcp/server.py](backend/mcp/server.py) 中。要添加新工具，只需创建新的带有 `@mcp.tool()` 装饰器的函数。

### 扩展 Agent 功能

主应用在 [backend/main.py](backend/main.py) 中实现，其中包含了 LangChain Agent 的配置。可以通过修改 [hub.pull("hwchase17/react")](backend/main.py#L32) 中的提示词或添加更多工具来扩展 Agent 的功能。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。