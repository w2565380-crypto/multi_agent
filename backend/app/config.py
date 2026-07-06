import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    # 数据库路径（默认为本地 sqlite）
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/project.db")
    
    # Dify 配置
    DIFY_BASE_URL: str = os.getenv("DIFY_BASE_URL", "")
    
    # 3 个 Agent 的 API Key
    DIFY_PM_API_KEY: str = os.getenv("DIFY_PM_API_KEY", "")
    DIFY_DEV_API_KEY: str = os.getenv("DIFY_DEV_API_KEY", "")
    DIFY_QA_API_KEY: str = os.getenv("DIFY_QA_API_KEY", "")

# 实例化配置对象供全局调用
settings = Settings()