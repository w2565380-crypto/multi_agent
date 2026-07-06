from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.database import Base

class ProjectAgentDB(Base):
    """AI 角色生成表模型"""
    __tablename__ = "project_agents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)     
    agent_name = Column(String, nullable=False)   
    elapsed_time = Column(Integer, default=0)  
    final_output = Column(Text, nullable=True)      
    path = Column(String, nullable=True)           