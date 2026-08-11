import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.api.routers import document
from src.api.routers import chat
from src.api.routers import health

app = FastAPI(
    title = 'FastAPI RAG系统',
    description = '基于FastAPI的RAG系统-纯Python实现',
    version = '0.1'
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / 'frontend'
app.mount('/js', StaticFiles(directory=FRONTEND_DIR / 'js'), name='frontend-js')
app.mount('/css', StaticFiles(directory=FRONTEND_DIR / 'css'), name='frontend-css')

# 追加跨域解决
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],    # 允许的源
    allow_credentials=True,
    allow_methods=['*'],    # 允许的方法
    allow_headers=['*'],    # 允许的请求头
)

app.include_router(document.router,prefix='/api')
app.include_router(chat.router,prefix='/api')
app.include_router(health.router,prefix='/api')

@app.get('/', response_class=FileResponse)
async def index():
    return FRONTEND_DIR / 'index.html'

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('src.api.main:app', port=8000,reload=True)
