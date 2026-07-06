from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.database import Base

class ProjectDB(Base):
    """项目主表模型"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="INITIAL")  # INITIAL, RUNNING, COMPLETED, FAILED
    zip_path = Column(String, nullable=True)