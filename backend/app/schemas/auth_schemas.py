from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    """创建用户请求体"""
    user_name: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")

class UserUpdate(BaseModel):
    """
    🌟 修改点：允许前端修改用户名和密码
    使用 Optional 表示这两个字段都是可选的，可以只改用户名，也可以只改密码
    """
    user_name: Optional[str] = Field(None, min_length=2, max_length=50, description="新用户名")
    password: Optional[str] = Field(None, min_length=1, description="新密码")
    avatar: Optional[str] = Field(None, description="头像图片文件名或路径")

class UserResponse(BaseModel):
    """返回给前端的用户数据（包含明文密码以便开发联调）"""
    id: int
    user_name: str
    password: str
    avatar: Optional[str] = None
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录请求体"""
    user_name: str
    password: str