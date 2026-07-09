import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.routers.auth_router import router as auth_router  
from app.routers.projects import router as projects_router, user_router as user_router          
     
from app.database import engine, Base, IMAGES_DIR


# 新增：使用最新的 lifespan 统一管理数据库初始化逻辑
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    生命周期管理器：在后端服务启动时自动初始化数据库配置
    """
    with engine.connect() as con:
        # 显式开启 SQLite 的外键级联检查（确保 ON DELETE CASCADE 生效）
        # 🌟 修改点：此处同样使用 text() 包裹，确保符合 SqlAlchemy 2.0 规范
        con.execute(text("PRAGMA foreign_keys = ON;"))
        con.commit()

    Base.metadata.create_all(bind=engine)
    
    yield  # 服务在此处挂起并正常运行
    
    print("AI多智能体公司模拟系统后端正在平稳关闭...")

# 传入 lifespan 参数
app = FastAPI(title="AI多智能体系统后端 API", lifespan=lifespan)

# 开启 CORS 跨域支持，允许前端（Vue/Streamlit）无阻碍调用接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# 挂载静态文件目录
app.mount("/previews", StaticFiles(directory=EXPORTS_DIR), name="previews")

# 挂载用户头像静态文件目录，把物理路径 IMAGES_DIR 映射到网络路径 /avatars
app.mount("/avatars", StaticFiles(directory=IMAGES_DIR), name="avatars")

# 注册项目管理相关的 API 接口
app.include_router(projects_router)
app.include_router(user_router)  

# 注册用户认证与管理相关的 API 接口（来自 routers/auth.py）
app.include_router(auth_router)

# # 注册针对新 projects 表的纯数据增查接口
# app.include_router(db_projects_router)

# # 注册针对新 project_agents 表的纯数据查询看板接口
# app.include_router(db_agents_router)

@app.get("/")
def read_root():
    return {
        "status": "success", 
        "message": "AI多智能体公司后端 API 运行正常！",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)