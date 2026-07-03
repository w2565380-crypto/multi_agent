# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.schemas.projects_schemas import ProjectResponse
# from app.schemas.agents_schemas import ProjectAgentResponse, ProjectDetailResponse

# # 🌟 关键修改：分别引入两套干净解耦的 CRUD 原子操作
# from app.crud import projects_crud as project_crud
# from app.crud import agents_crud as agent_crud

# router = APIRouter(prefix="/api/project-agents", tags=["AI 智能体成果查询"])

# def format_project_zip_url(project, base_url: str = "http://127.0.0.1:8000"):
#     if project and project.zip_path:
#         project.zip_path = f"{base_url}/previews/{project.zip_path}"
#     return project

# @router.get("/{project_id}/detail", response_model=ProjectDetailResponse, summary="前端核心看板：一键获取项目及全体AI最终代码资产")
# def get_project_agents_full_detail(project_id: int, db: Session = Depends(get_db)):
#     # 1. 跨模块调用：通过项目 CRUD 去查项目基本信息
#     project = project_crud.get_project_by_id(db, project_id=project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="该项目不存在")
        
#     formatted_project = format_project_zip_url(project)
    
#     # 2. 跨模块调用：通过智能体 CRUD 去查对应的角色成果
#     agents_results = agent_crud.get_project_agents(db, project_id=project_id)
    
#     return {
#         "project": ProjectResponse.model_validate(formatted_project),
#         "agents": [ProjectAgentResponse.model_validate(a) for a in agents_results]
#     }