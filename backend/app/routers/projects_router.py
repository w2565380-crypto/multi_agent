# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.schemas.projects_schemas import ProjectCreate, ProjectResponse
# from app.crud import projects_crud as crud

# router = APIRouter(prefix="/api/projects", tags=["项目管理"])

# def format_project_zip_url(project, base_url: str = "http://127.0.0.1:8000"):
#     """辅助函数：拼接代码压缩包的下载链接"""
#     if project and project.zip_path:
#         project.zip_path = f"{base_url}/previews/{project.zip_path}"
#     return project

# @router.post("/user/{user_id}", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="人类用户创建新仿真项目")
# def create_new_project(user_id: int, project_in: ProjectCreate, db: Session = Depends(get_db)):
#     # 🌟 增
#     return crud.create_project(db, user_id=user_id, project_in=project_in)


# @router.get("/user/{user_id}", response_model=List[ProjectResponse], summary="获取当前用户的所有仿真项目列表")
# def get_user_all_projects(user_id: int, db: Session = Depends(get_db)):
#     # 🌟 查列表
#     projects = crud.get_projects_by_user(db, user_id=user_id)
#     return [format_project_zip_url(p) for p in projects]