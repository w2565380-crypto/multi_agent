from typing import Optional
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    """前端创建项目入参（仅支持增操作需要的核心字段）"""
    title: str = Field(..., min_length=1, description="项目名称")
    description: str = Field(..., description="项目描述")

class ProjectResponse(BaseModel):
    """后端返回给前端的项目基础数据"""
    id: int
    user_id: int
    title: str
    description: str
    status: str
    zip_path: Optional[str] = None

    class Config:
        from_attributes = True