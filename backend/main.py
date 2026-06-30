from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="AI多智能体系统后端 API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

app.mount("/previews", StaticFiles(directory=EXPORTS_DIR), name="previews")

@app.get("/")
def read_root():
    return {
        "status": "success", 
        "message": "AI多智能体公司后端 API 运行正常！",
        "docs_url": "/docs"
    }

# 🌟 新增：让 main.py 支持被 python3 直接运行
if __name__ == "__main__":
    import uvicorn
    # 监听 0.0.0.0 端口为 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)