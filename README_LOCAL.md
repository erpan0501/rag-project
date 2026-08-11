# RAG 本地演示说明

默认使用 `DEMO_MODE=1`，外部模型 Key 为空时采用本地哈希向量和本地回答，不会主动调用第三方模型接口。

根目录的 `启动.command` 会同时启动后端（8000）和独立静态前端（5174）；`关闭.command` 会停止它们。也可以在终端分别执行 `./启动.command` 与 `./关闭.command`。日志保存在 `.run/`。

```bash
uv sync
uv run uvicorn src.api.main:app --reload --port 8000
```

直接打开 `http://localhost:5174` 可进入前端；接口文档在 `http://localhost:8000/docs`。上传 Markdown、HTML、DOCX 或 PDF 后，可以在集合中检索并进行演示问答。

若要切换真实模型，在 `.env` 中关闭 `DEMO_MODE` 并填写对应 API Key。
