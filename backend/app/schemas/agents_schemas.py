from typing import Optional, List
from pydantic import BaseModel
from app.schemas.projects_schemas import ProjectResponse # 🌟 跨文件引入项目规范

class ProjectAgentResponse(BaseModel):
    """后端返回的 AI 角色最终成果数据"""
    id: int
    project_id: int
    role: str
    agent_name: str
    elapsed_time: int
    final_output: Optional[str] = None
    path: Optional[str] = None

    class Config:
        from_attributes = True

class ProjectDetailResponse(BaseModel):
    """核心看板数据模型：一次性返回项目基础状态与全部智能体成果"""
    project: ProjectResponse
    agents: List[ProjectAgentResponse]