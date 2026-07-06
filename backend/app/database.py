import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 动态计算绝对路径：当前文件是 database.py (在 backend/app/ 下)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # backend/app
APP_DIR = CURRENT_DIR                                    # backend/app
BACKEND_DIR = os.path.dirname(APP_DIR)                   # backend
DATA_DIR = os.path.join(BACKEND_DIR, "data")             # backend/data
IMAGES_DIR = os.path.join(DATA_DIR, "images")            # backend/data/images

# 2. 确保 data 和 images 文件夹存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# 3. 拼接 SQLite 绝对路径
DB_FILE_PATH = os.path.join(DATA_DIR, "project.db")
DATABASE_URL = f"sqlite:///{DB_FILE_PATH}"

# 4. 创建引擎与 Session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()