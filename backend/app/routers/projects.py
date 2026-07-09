# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# import os

# from app.database import get_db
# from app.crud.projects_crud import (
#     create_project, 
#     get_project_by_id, 
#     get_projects_by_user,
#     delete_project_completely
# )
# from app.crud.auth_crud import get_user_by_id
# from app.schemas.projects_schemas import ProjectCreate
# from app.services.orchestrator import step_orchestrator
# from app.utils.file_helper import file_helper
# router = APIRouter(prefix="/api/projects", tags=["projects"])
# from app.database import get_db
# # 引入底层标准 CRUD 接口
# from app.crud.projects_crud import get_project_by_id, get_projects_by_user, delete_project_completely
# from app.crud.agents_crud import get_project_agents


# # =========================================================
# # 【接口 1】：创建项目并启动仿真
# # =========================================================
# @router.post("/create")
# async def api_create_project(
#     user_id: int, 
#     project_in: ProjectCreate, 
#     background_tasks: BackgroundTasks, 
#     db: Session = Depends(get_db)
# ):
#     user = get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="未找到该用户")

#     project = create_project(db, user_id, project_in)
#     background_tasks.add_task(step_orchestrator.step_1_run_pm, project.id)

#     return {
#         "success": True,
#         "message": "项目创建成功，产品经理开始规划需求...",
#         "project_id": project.id,
#         "status": project.status
#     }


# # =========================================================
# # 【接口 2】：人机协作审批
# # =========================================================
# @router.post("/{project_id}/approve")
# async def api_approve_project(
#     project_id: int, 
#     approved: bool, 
#     feedback: str = "", 
#     db: Session = Depends(get_db)
# ):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="未找到该项目")

#     await step_orchestrator.step_2_handle_approval(db, project_id, approved, feedback)

#     return {
#         "success": True,
#         "message": "审批指令已下达，流程开始流转。"
#     }


# # =========================================================
# # 【接口 3】：获取用户的所有项目列表（历史看板）
# # =========================================================
# @router.get("/")
# async def api_get_user_projects(user_id: int, db: Session = Depends(get_db)):
#     projects = get_projects_by_user(db, user_id)
#     return [
#         {
#             "id": p.id,
#             "title": p.title,
#             "status": p.status,
#             "zip_path": p.zip_path
#         } for p in reversed(projects)
#     ]


# # =========================================================
# # 【接口 4】：获取单个项目的完整详情（状态轮询与恢复）
# # =========================================================
# @router.get("/{project_id}")
# async def api_get_project_detail(project_id: int, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     return {
#         "id": project.id,
#         "user_id": project.user_id,
#         "title": project.title,
#         "description": project.description,
#         "status": project.status,
#         "zip_path": project.zip_path
#     }


# # =========================================================
# # 【接口 5（安全升级）】：获取项目网页成果预览 URL（数据库驱动检测）
# # =========================================================
# @router.get("/{project_id}/preview-url")
# async def api_get_preview_url(project_id: int, request: Request, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     # 🌟 核心升级：先去数据库查询 DEV 角色登记的相对路径（如 "src/"）
#     agents = get_project_agents(db, project_id)
#     dev_agent = next((a for a in agents if a.role == "DEV"), None)
    
#     # 如果没开发完或者没有登记路径，报 404
#     if not dev_agent or not dev_agent.path:
#         raise HTTPException(status_code=404, detail="代码尚未生成，请等待程序员开发完成")

#     # 拿取真实的文件夹路径
#     folder_name = f"project_{project.id}_{project.title}"
#     project_dir = file_helper.get_project_dir(username, project.id, project.title)
    
#     # 拼接真正的源码目录（来自数据库 path，如 "exports/.../src"）
#     real_src_dir = os.path.join(project_dir, dev_agent.path)

#     base_url = str(request.base_url)

#     # 动态匹配实际物理文件
#     if os.path.exists(os.path.join(real_src_dir, "index.html")):
#         preview_url = f"{base_url}previews/{username}/{folder_name}/{dev_agent.path}index.html"
#     elif os.path.exists(os.path.join(project_dir, "index.html")):
#         preview_url = f"{base_url}previews/{username}/{folder_name}/index.html"
#     else:
#         return {
#             "success": True,
#             "is_web_project": False,
#             "preview_url": None,
#             "message": "此项目无 HTML 文件，仅支持查看源码。"
#         }

#     return {
#         "success": True,
#         "is_web_project": True,
#         "preview_url": preview_url
#     }


# # =========================================================
# # 【接口 6（安全升级）】：获取项目的 PRD 纯文本 (Markdown)（数据库驱动读取）
# # =========================================================
# @router.get("/{project_id}/prd")
# async def api_get_project_prd_text(project_id: int, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     # 🌟 核心升级：从数据库读取产品经理登记的真实路径 (如 "PRD.md")
#     agents = get_project_agents(db, project_id)
#     pm_agent = next((a for a in agents if a.role == "PM"), None)
#     if not pm_agent or not pm_agent.path:
#         raise HTTPException(status_code=404, detail="产品需求文档（PRD）尚未生成")

#     try:
#         # 使用数据库中的相对路径精准加载
#         prd_content = file_helper.read_file_by_db_path(username, project.id, project.title, pm_agent.path)
#         return {
#             "success": True,
#             "project_id": project_id,
#             "prd_content": prd_content
#         }
#     except Exception:
#         raise HTTPException(status_code=404, detail="物理文件已丢失，请稍后再试")


# # =========================================================
# # 【接口 7（安全升级）】：获取项目的 QA 测试报告 (Markdown)（数据库驱动读取）
# # =========================================================
# @router.get("/{project_id}/qa-report")
# async def api_get_project_qa_report_text(project_id: int, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     # 🌟 核心升级：从数据库读取测试工程师登记的真实路径 (如 "Test_Report.md")
#     agents = get_project_agents(db, project_id)
#     qa_agent = next((a for a in agents if a.role == "QA"), None)
#     if not qa_agent or not qa_agent.path:
#         raise HTTPException(status_code=404, detail="测试报告尚未生成")

#     try:
#         # 使用数据库中的相对路径精准加载
#         qa_content = file_helper.read_file_by_db_path(username, project.id, project.title, qa_agent.path)
#         return {
#             "success": True,
#             "project_id": project_id,
#             "qa_report": qa_content
#         }
#     except Exception:
#         raise HTTPException(status_code=404, detail="物理文件已丢失，请稍后再试")


# # =========================================================
# # 【接口 8】：一键彻底删除项目（数据库 + 物理文件）
# # =========================================================
# @router.delete("/{project_id}")
# async def api_delete_project_by_id(project_id: int, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     # 1. 物理删除打包在 exports/{username} 下的压缩包
#     zip_file_path = os.path.join(file_helper.exports_dir, username, f"project_{project_id}.zip")
#     if os.path.exists(zip_file_path):
#         try:
#             os.remove(zip_file_path)
#         except Exception as e:
#             print(f"⚠️ [WARNING] 物理 ZIP 删除失败: {e}")

#     # 2. 调用 delete_project_completely 官方接口，抹除数据库和对应的物理源码目录
#     success = delete_project_completely(db, project_id)
#     if not success:
#         raise HTTPException(status_code=500, detail="删除项目失败，数据库接口运行异常")

#     return {
#         "success": True,
#         "message": f"项目 ID: {project_id} 及其本地源码、打包 ZIP、关联 AI 记录已全部成功安全彻底清理！"
#     }

# # =========================================================
# # 【接口 9】：代码迭代修改（重新提意见修改）
# # =========================================================
# @router.post("/{project_id}/revise")
# async def api_revise_project_code(
#     project_id: int, 
#     feedback: str, 
#     background_tasks: BackgroundTasks, 
#     db: Session = Depends(get_db)
# ):
#     """
#     【接口 9】：对现有代码不满意，提交修改意见重新迭代。
#     接口会异步调用后台重构逻辑，完成后自动重新测试并重新打包。
#     """
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     # 异步触发后台迭代重构任务
#     background_tasks.add_task(step_orchestrator.step_3_revise_dev, project_id, feedback)

#     return {
#         "success": True,
#         "message": "代码重构指令已下达，程序员正在根据您的建议修改代码，请耐心等待并轮询状态..."
#     }


# # =========================================================
# # 【接口 10】：一键下载项目 ZIP 源码压缩包
# # =========================================================
# @router.get("/{project_id}/download")
# async def api_download_project_zip(project_id: int, db: Session = Depends(get_db)):
#     """
#     【接口 10】：一键下载项目的全部成果 ZIP 包（包含 PRD, 源码, 测试报告）。
#     """
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     if not project.zip_path:
#         raise HTTPException(status_code=404, detail="该项目尚未打包，无法下载")

#     # 1. 计算 ZIP 在服务器上的绝对物理路径
#     # project.zip_path 存储的是 "exports/{username}/project_{id}.zip"
#     # file_helper.exports_dir 存储的是 "/home/.../backend/exports"
#     # 我们退到 backend/ 目录下进行拼接
#     backend_root = os.path.dirname(file_helper.exports_dir)
#     absolute_zip_path = os.path.join(backend_root, project.zip_path)

#     # 2. 物理校验压缩包是否存在
#     if not os.path.exists(absolute_zip_path):
#         raise HTTPException(status_code=404, detail="物理压缩包文件在服务器上未找到，请重新生成项目")

#     # 3. 🌟 以物理文件流的形式向浏览器吐出下载，并重命名为下载时的文件名
#     safe_title = "".join([c for c in project.title if c.isalnum() or c in ('_', '-')])
#     download_filename = f"Project_{project_id}_{safe_title}.zip"

#     return FileResponse(
#         path=absolute_zip_path,
#         media_type="application/octet-stream",
#         filename=download_filename  # 浏览器中下载下来显示的文件名
#     )


# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# import os

# from app.database import get_db
# # 引入标准底层 CRUD 接口
# from app.crud.projects_crud import (
#     create_project, 
#     get_project_by_id, 
#     get_projects_by_user,
#     delete_project_completely
# )
# from app.crud.agents_crud import get_project_agents
# from app.crud.auth_crud import get_user_by_id
# from app.schemas.projects_schemas import ProjectCreate
# from app.services.orchestrator import step_orchestrator
# from app.utils.file_helper import file_helper

# # 1. 🌟 原有的项目控制路由器
# router = APIRouter(prefix="/api/projects", tags=["projects"])

# # 2. 🌟 新增：用户维度资产汇总路由器（完全匹配前端要求的 /api/users 前缀）
# user_router = APIRouter(prefix="/api/users", tags=["users"])


# # ==============================================================================
# # 第一部分：项目生命周期与流转控制 (Life Cycle & Orchestration)
# # ==============================================================================

# # 【接口 1】：创建项目并启动仿真
# @router.post("/create")
# async def api_create_project(
#     user_id: int, 
#     project_in: ProjectCreate, 
#     background_tasks: BackgroundTasks, 
#     db: Session = Depends(get_db)
# ):
#     print(f"\n📥 [API - CREATE] 接收到创建项目请求, 用户 ID: {user_id}, 标题: '{project_in.title}'")
#     user = get_user_by_id(db, user_id)
#     if not user:
#         print(f"❌ [API - CREATE] 错误：未找到用户账号: {user_id}")
#         raise HTTPException(status_code=404, detail="未找到该用户")

#     project = create_project(db, user_id, project_in)
#     print(f"💾 [API - CREATE] 数据库记录创建成功, 项目 ID: {project.id}, 初始状态: {project.status}")

#     background_tasks.add_task(step_orchestrator.step_1_run_pm, project.id)

#     return {
#         "success": True,
#         "message": "项目创建成功，产品经理开始规划需求...",
#         "project_id": project.id,
#         "status": project.status
#     }


# # 【接口 2】：人机协作审批控制
# @router.post("/{project_id}/approve")
# async def api_approve_project(
#     project_id: int, 
#     approved: bool, 
#     feedback: str = "", 
#     db: Session = Depends(get_db)
# ):
#     print(f"\n📥 [API - APPROVE] 接收到审批指令, 项目 ID: {project_id}, 批准状态: {approved}")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         print(f"❌ [API - APPROVE] 错误：未找到项目: {project_id}")
#         raise HTTPException(status_code=404, detail="未找到该项目")

#     await step_orchestrator.step_2_handle_approval(db, project_id, approved, feedback)

#     return {
#         "success": True,
#         "message": "审批指令已下达，流程开始流转。"
#     }


# # 【接口 3】：代码不满意打回重新修改
# @router.post("/{project_id}/revise")
# async def api_revise_project_code(
#     project_id: int, 
#     feedback: str, 
#     background_tasks: BackgroundTasks, 
#     db: Session = Depends(get_db)
# ):
#     print(f"\n📥 [API - REVISE] 接收到代码重构指令, 项目 ID: {project_id}")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         print(f"❌ [API - REVISE] 错误：未找到项目: {project_id}")
#         raise HTTPException(status_code=404, detail="项目不存在")

#     background_tasks.add_task(step_orchestrator.step_3_revise_dev, project_id, feedback)

#     return {
#         "success": True,
#         "message": "代码重构指令已下达，程序员正在根据您的建议修改代码，请耐心等待并轮询状态..."
#     }


# # 【接口 4】：一键彻底物理删除项目
# @router.delete("/{project_id}")
# async def api_delete_project_by_id(project_id: int, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"
#     project_title = project.title

#     zip_file_path = os.path.join(file_helper.exports_dir, username, f"project_{project_id}.zip")
#     if os.path.exists(zip_file_path):
#         try:
#             os.remove(zip_file_path)
#             print(f"   🧹 [API - DELETE] 物理删除压缩包成功: {zip_file_path}")
#         except Exception as e:
#             print(f"   ⚠️ [API - DELETE] 物理 ZIP 删除失败: {e}")

#     success = delete_project_completely(db, project_id)
#     if not success:
#         raise HTTPException(status_code=500, detail="删除项目失败，数据库底层接口运行异常")

#     return {
#         "success": True,
#         "message": f"项目 ID: {project_id} 及其所有关联的 AI 记录、本地资产文件夹已全部安全擦除清理！"
#     }


# # ==============================================================================
# # 第二部分：项目列表与状态恢复 (State & History Recovery)
# # ==============================================================================

# # 【接口 5】：获取用户的所有项目列表（历史记录）
# @router.get("/")
# async def api_get_user_projects(user_id: int, db: Session = Depends(get_db)):
#     print(f"📥 [API - LIST] 获取用户 {user_id} 的历史项目列表")
#     projects = get_projects_by_user(db, user_id)
#     return [
#         {
#             "id": p.id,
#             "title": p.title,
#             "status": p.status,
#             "zip_path": p.zip_path
#         } for p in reversed(projects)
#     ]


# # 【接口 6】：获取单个项目最新状态与详情
# @router.get("/{project_id}")
# async def api_get_project_detail(project_id: int, db: Session = Depends(get_db)):
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     return {
#         "id": project.id,
#         "user_id": project.user_id,
#         "title": project.title,
#         "description": project.description,
#         "status": project.status,
#         "zip_path": project.zip_path
#     }


# # ==============================================================================
# # 第三部分：智能体成果物理精准调取
# # ==============================================================================

# # 【接口 7】：【PM成果】获取 PRD 说明书 Markdown
# @router.get("/{project_id}/prd")
# async def api_get_project_prd_text(project_id: int, db: Session = Depends(get_db)):
#     print(f"📥 [API - PRD] 正在读取项目 {project_id} 的需求说明书...")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     agents = get_project_agents(db, project_id)
#     pm_agent = next((a for a in agents if a.role == "PM"), None)
#     if not pm_agent or not pm_agent.path:
#         raise HTTPException(status_code=404, detail="产品需求文档（PRD）尚未生成")

#     try:
#         prd_content = file_helper.read_file_by_db_path(username, project.id, project.title, pm_agent.path)
#         return {
#             "success": True,
#             "project_id": project_id,
#             "prd_content": prd_content
#         }
#     except Exception:
#         raise HTTPException(status_code=404, detail="物理 PRD.md 文件已丢失或损坏")


# # 【接口 8】：【QA成果】获取 QA 测试报告 Markdown
# @router.get("/{project_id}/qa-report")
# async def api_get_project_qa_report_text(project_id: int, db: Session = Depends(get_db)):
#     print(f"📥 [API - QA] 正在读取项目 {project_id} 的测试报告...")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     agents = get_project_agents(db, project_id)
#     qa_agent = next((a for a in agents if a.role == "QA"), None)
#     if not qa_agent or not qa_agent.path:
#         raise HTTPException(status_code=404, detail="测试报告尚未生成")

#     try:
#         qa_content = file_helper.read_file_by_db_path(username, project.id, project.title, qa_agent.path)
#         return {
#             "success": True,
#             "project_id": project_id,
#             "qa_report": qa_content
#         }
#     except Exception:
#         raise HTTPException(status_code=404, detail="物理 Test_Report.md 文件已丢失或损坏")


# # 【接口 9】：【Dev成果】获取源码文件树列表与内容
# @router.get("/{project_id}/code-files")
# async def api_get_project_code_files(project_id: int, db: Session = Depends(get_db)):
#     print(f"📥 [API - CODES] 正在扫描项目 {project_id} 的代码树结构...")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     agents = get_project_agents(db, project_id)
#     dev_agent = next((a for a in agents if a.role == "DEV"), None)
#     if not dev_agent or not dev_agent.path:
#         raise HTTPException(status_code=404, detail="程序员尚未生成代码")

#     project_dir = file_helper.get_project_dir(username, project.id, project.title)
#     src_dir = os.path.join(project_dir, dev_agent.path)

#     if not os.path.exists(src_dir):
#         raise HTTPException(status_code=404, detail="源码磁盘文件夹不存在")

#     files_data = []
#     for root, _, files in os.walk(src_dir):
#         for file in files:
#             file_path = os.path.join(root, file)
#             rel_path = os.path.relpath(file_path, src_dir)
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                 files_data.append({
#                     "file_name": file,
#                     "file_path": rel_path,
#                     "code_content": content
#                 })
#             except Exception as e:
#                 print(f"⚠️ [WARNING] 读取代码文件 {file} 异常: {e}")

#     return {
#         "success": True,
#         "project_id": project_id,
#         "files": files_data
#     }


# # 【接口 10】：【成果运行】获取网页的预览渲染地址
# @router.get("/{project_id}/preview-url")
# async def api_get_preview_url(project_id: int, request: Request, db: Session = Depends(get_db)):
#     print(f"📥 [API - PREVIEW] 正在为项目 {project_id} 获取预览链接...")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     agents = get_project_agents(db, project_id)
#     dev_agent = next((a for a in agents if a.role == "DEV"), None)
#     if not dev_agent or not dev_agent.path:
#         raise HTTPException(status_code=404, detail="代码尚未生成")

#     folder_name = f"project_{project.id}_{project.title}"
#     project_dir = file_helper.get_project_dir(username, project.id, project.title)
    
#     real_src_dir = os.path.join(project_dir, dev_agent.path)
#     base_url = str(request.base_url)

#     if os.path.exists(os.path.join(real_src_dir, "index.html")):
#         preview_url = f"{base_url}previews/{username}/{folder_name}/{dev_agent.path}index.html"
#     elif os.path.exists(os.path.join(project_dir, "index.html")):
#         preview_url = f"{base_url}previews/{username}/{folder_name}/index.html"
#     else:
#         return {
#             "success": True,
#             "is_web_project": False,
#             "preview_url": None,
#             "message": "此项目无 HTML 文件，仅支持查看源码。"
#         }

#     return {
#         "success": True,
#         "is_web_project": True,
#         "preview_url": preview_url
#     }


# # 【接口 11】：【物理交付】一键下载成果 ZIP 包
# @router.get("/{project_id}/download")
# async def api_download_project_zip(project_id: int, db: Session = Depends(get_db)):
#     print(f"📥 [API - DOWNLOAD] 用户触发项目 {project_id} 成果物包下载...")
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     if not project.zip_path:
#         raise HTTPException(status_code=404, detail="该项目尚未完成，暂时无法下载成果物")

#     backend_root = os.path.dirname(file_helper.exports_dir)
#     absolute_zip_path = os.path.join(backend_root, project.zip_path)

#     if not os.path.exists(absolute_zip_path):
#         raise HTTPException(status_code=404, detail="物理压缩包文件在服务器上未找到，请重新生成项目")

#     safe_title = "".join([c for c in project.title if c.isalnum() or c in ('_', '-')])
#     download_filename = f"Project_{project_id}_{safe_title}.zip"

#     return FileResponse(
#         path=absolute_zip_path,
#         media_type="application/octet-stream",
#         filename=download_filename
#     )


# # ==============================================================================
# # 第四部分（增量）：【用户资产看板】按用户和产物类型一键汇总文档
# # ==============================================================================

# # 🌟 【接口 12】：获取该用户所有项目下该类型的所有文件列表
# @user_router.get("/{user_id}/files")
# async def api_get_user_files_by_type(user_id: int, type: str, db: Session = Depends(get_db)):
#     """
#     按用户和产物类型（PM的PRD 或 QA的测试报告）进行全项目合并汇总。
#     支持 type=pm 或 type=qa (不区分大小写)。
#     """
#     print(f"📥 [API - USER SUMMARY] 正在为用户 {user_id} 汇总类型为 '{type}' 的所有历史文档...")
    
#     # 1. 校验用户是否存在
#     user = get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="用户账号不存在")

#     username = user.user_name
    
#     # 2. 获取该用户的所有项目
#     projects = get_projects_by_user(db, user_id)
    
#     # 3. 确定要筛选的 AI 角色
#     target_role = "PM" if type.lower() == "pm" else "QA"
#     result_files = []

#     # 4. 遍历所有项目，安全调取已登记的物理文件
#     for p in projects:
#         agents = get_project_agents(db, p.id)
#         agent = next((a for a in agents if a.role == target_role), None)
        
#         # 如果该智能体已经工作完成且登记了物理路径
#         if agent and agent.path:
#             try:
#                 # 使用数据库路径驱动，安全读取硬盘文本
#                 content = file_helper.read_file_by_db_path(username, p.id, p.title, agent.path)
#                 result_files.append({
#                     "project_id": p.id,
#                     "project_title": p.title,
#                     "file_name": os.path.basename(agent.path),
#                     "content": content
#                 })
#             except Exception as e:
#                 # 容错：物理文件若有损坏，跳过该项目，保证整体列表顺利返回
#                 print(f"⚠️ [WARNING] 物理文件读取失败: {e}")
#                 continue

#     return {
#         "success": True,
#         "files": result_files
#     }


from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
# 引入底层标准 CRUD 接口
from app.crud.projects_crud import (
    create_project, 
    get_project_by_id, 
    get_projects_by_user,
    delete_project_completely
)
from app.crud.agents_crud import get_project_agents
from app.crud.auth_crud import get_user_by_id
from app.schemas.projects_schemas import ProjectCreate
from app.services.orchestrator import step_orchestrator
from app.utils.file_helper import file_helper

# 1. 项目控制路由器
router = APIRouter(prefix="/api/projects", tags=["projects"])

# 2. 用户维度资产汇总路由器
user_router = APIRouter(prefix="/api/users", tags=["users"])


# ==============================================================================
# 第一部分：项目生命周期与流转控制 (Life Cycle & Orchestration)
# ==============================================================================

# 【接口 1】：创建项目并启动仿真
@router.post("/create")
async def api_create_project(
    user_id: int, 
    project_in: ProjectCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    print(f"\n📥 [API - CREATE] 接收到创建项目请求, 用户 ID: {user_id}, 标题: '{project_in.title}'")
    user = get_user_by_id(db, user_id)
    if not user:
        print(f"❌ [API - CREATE] 错误：未找到用户账号: {user_id}")
        raise HTTPException(status_code=404, detail="未找到该用户")

    # 1. 🌟 调用官方创建接口（其内部现在自动使用 user_id 隔离路径）
    project = create_project(db, user_id, project_in)
    print(f"💾 [API - CREATE] 数据库记录创建成功, 项目 ID: {project.id}, 初始状态: {project.status}")

    # 2. 异步触发第一步：PM 启动
    background_tasks.add_task(step_orchestrator.step_1_run_pm, project.id)

    return {
        "success": True,
        "message": "项目创建成功，产品经理开始规划需求...",
        "project_id": project.id,
        "status": project.status
    }


# 【接口 2】：人机协作审批控制
@router.post("/{project_id}/approve")
async def api_approve_project(
    project_id: int, 
    approved: bool, 
    feedback: str = "", 
    db: Session = Depends(get_db)
):
    print(f"\n📥 [API - APPROVE] 接收到审批指令, 项目 ID: {project_id}, 批准状态: {approved}")
    project = get_project_by_id(db, project_id)
    if not project:
        print(f"❌ [API - APPROVE] 错误：未找到项目: {project_id}")
        raise HTTPException(status_code=404, detail="未找到该项目")

    await step_orchestrator.step_2_handle_approval(db, project_id, approved, feedback)

    return {
        "success": True,
        "message": "审批指令已下达，流程开始流转。"
    }


# 【接口 3】：代码不满意打回重新修改
@router.post("/{project_id}/revise")
async def api_revise_project_code(
    project_id: int, 
    feedback: str, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    print(f"\n📥 [API - REVISE] 接收到代码重构指令, 项目 ID: {project_id}")
    project = get_project_by_id(db, project_id)
    if not project:
        print(f"❌ [API - REVISE] 错误：未找到项目: {project_id}")
        raise HTTPException(status_code=404, detail="项目不存在")

    background_tasks.add_task(step_orchestrator.step_3_revise_dev, project_id, feedback)

    return {
        "success": True,
        "message": "代码重构指令已下达，程序员正在根据您的建议修改代码，请耐心等待并轮询状态..."
    }


# 【接口 4】：一键彻底物理删除项目
@router.delete("/{project_id}")
async def api_delete_project_by_id(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 🌟 核心修改：使用固定的 project.user_id 计算物理路径
    zip_file_path = os.path.join(file_helper.exports_dir, str(project.user_id), f"project_{project_id}.zip")
    if os.path.exists(zip_file_path):
        try:
            os.remove(zip_file_path)
            print(f"   🧹 [API - DELETE] 物理删除压缩包成功: {zip_file_path}")
        except Exception as e:
            print(f"   ⚠️ [API - DELETE] 物理 ZIP 删除失败: {e}")

    # 调用底层级联擦除
    success = delete_project_completely(db, project_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除项目失败，数据库底层接口运行异常")

    return {
        "success": True,
        "message": f"项目 ID: {project_id} 及其所有关联的 AI 记录、本地资产文件夹已全部安全擦除清理！"
    }


# ==============================================================================
# 第二部分：项目列表与状态恢复 (State & History Recovery)
# ==============================================================================

# 【接口 5】：获取用户的所有项目列表（历史记录）
@router.get("/")
async def api_get_user_projects(user_id: int, db: Session = Depends(get_db)):
    projects = get_projects_by_user(db, user_id)
    return [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "zip_path": p.zip_path
        } for p in reversed(projects)
    ]


# 【接口 6】：获取单个项目的完整详情
@router.get("/{project_id}")
async def api_get_project_detail(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {
        "id": project.id,
        "user_id": project.user_id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "zip_path": project.zip_path
    }


# ==============================================================================
# 第三部分：智能体成果物理精准调取
# ==============================================================================

# 【接口 7】：【PM成果】获取 PRD 说明书 Markdown
@router.get("/{project_id}/prd")
async def api_get_project_prd_text(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    agents = get_project_agents(db, project_id)
    pm_agent = next((a for a in agents if a.role == "PM"), None)
    if not pm_agent or not pm_agent.path:
        raise HTTPException(status_code=404, detail="产品需求文档（PRD）尚未生成")

    try:
        # 🌟 核心修改：使用 project.user_id 获取隔离的物理路径
        prd_content = file_helper.read_file_by_db_path(project.user_id, project.id, project.title, pm_agent.path)
        return {
            "success": True,
            "project_id": project_id,
            "prd_content": prd_content
        }
    except Exception:
        raise HTTPException(status_code=404, detail="物理 PRD.md 文件已丢失")


# 【接口 8】：【QA成果】获取 QA 测试报告 Markdown
@router.get("/{project_id}/qa-report")
async def api_get_project_qa_report_text(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    agents = get_project_agents(db, project_id)
    qa_agent = next((a for a in agents if a.role == "QA"), None)
    if not qa_agent or not qa_agent.path:
        raise HTTPException(status_code=404, detail="测试报告尚未生成")

    try:
        # 🌟 核心修改：使用 project.user_id 精准加载
        qa_content = file_helper.read_file_by_db_path(project.user_id, project.id, project.title, qa_agent.path)
        return {
            "success": True,
            "project_id": project_id,
            "qa_report": qa_content
        }
    except Exception:
        raise HTTPException(status_code=404, detail="物理 Test_Report.md 文件已丢失")


# 【接口 9】：【Dev成果】获取源码文件树列表与内容
@router.get("/{project_id}/code-files")
async def api_get_project_code_files(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    agents = get_project_agents(db, project_id)
    dev_agent = next((a for a in agents if a.role == "DEV"), None)
    if not dev_agent or not dev_agent.path:
        raise HTTPException(status_code=404, detail="程序员尚未生成代码")

    # 🌟 核心修改：使用 project.user_id 定位
    project_dir = file_helper.get_project_dir(project.user_id, project.id, project.title)
    src_dir = os.path.join(project_dir, dev_agent.path)

    if not os.path.exists(src_dir):
        raise HTTPException(status_code=404, detail="源码磁盘文件夹不存在")

    files_data = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, src_dir)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                files_data.append({
                    "file_name": file,
                    "file_path": rel_path,
                    "code_content": content
                })
            except Exception as e:
                print(f"⚠️ [WARNING] 读取代码文件 {file} 异常: {e}")

    return {
        "success": True,
        "project_id": project_id,
        "files": files_data
    }


# 【接口 10】：【成果运行】获取网页的预览渲染地址
@router.get("/{project_id}/preview-url")
async def api_get_preview_url(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    agents = get_project_agents(db, project_id)
    dev_agent = next((a for a in agents if a.role == "DEV"), None)
    if not dev_agent or not dev_agent.path:
        raise HTTPException(status_code=404, detail="代码尚未生成")

    folder_name = f"project_{project.id}_{project.title}"
    # 🌟 核心修改：使用 project.user_id
    project_dir = file_helper.get_project_dir(project.user_id, project.id, project.title)
    
    real_src_dir = os.path.join(project_dir, dev_agent.path)
    base_url = str(request.base_url)

    if os.path.exists(os.path.join(real_src_dir, "index.html")):
        # 🌟 核心修改：网络托管前缀也统一对齐为 user_id 格式
        preview_url = f"{base_url}previews/{project.user_id}/{folder_name}/{dev_agent.path}index.html"
    elif os.path.exists(os.path.join(project_dir, "index.html")):
        preview_url = f"{base_url}previews/{project.user_id}/{folder_name}/index.html"
    else:
        return {
            "success": True,
            "is_web_project": False,
            "preview_url": None,
            "message": "此项目无 HTML 文件，仅支持查看源码。"
        }

    return {
        "success": True,
        "is_web_project": True,
        "preview_url": preview_url
    }


# 【接口 11】：【物理交付】一键下载成果 ZIP 包
@router.get("/{project_id}/download")
async def api_download_project_zip(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if not project.zip_path:
        raise HTTPException(status_code=404, detail="该项目尚未完成，暂时无法下载成果物")

    backend_root = os.path.dirname(file_helper.exports_dir)
    absolute_zip_path = os.path.join(backend_root, project.zip_path)

    if not os.path.exists(absolute_zip_path):
        raise HTTPException(status_code=404, detail="物理压缩包文件在服务器上未找到，请重新生成项目")

    safe_title = "".join([c for c in project.title if c.isalnum() or c in ('_', '-')])
    download_filename = f"Project_{project_id}_{safe_title}.zip"

    return FileResponse(
        path=absolute_zip_path,
        media_type="application/octet-stream",
        filename=download_filename
    )


# ==============================================================================
# 第四部分：【用户资产看板】按用户和产物类型一键汇总文档
# ==============================================================================

# 【接口 12】：获取该用户所有项目下该类型的所有文件列表
@user_router.get("/{user_id}/files")
async def api_get_user_files_by_type(user_id: int, type: str, db: Session = Depends(get_db)):
    print(f"📥 [API - USER SUMMARY] 正在为用户 {user_id} 汇总类型为 '{type}' 的所有历史文档...")
    
    projects = get_projects_by_user(db, user_id)
    target_role = "PM" if type.lower() == "pm" else "QA"
    result_files = []

    for p in projects:
        agents = get_project_agents(db, p.id)
        agent = next((a for a in agents if a.role == target_role), None)
        
        if agent and agent.path:
            try:
                # 🌟 核心修改：使用 p.user_id (即 user_id) 磁盘路径精准驱动
                content = file_helper.read_file_by_db_path(p.user_id, p.id, p.title, agent.path)
                result_files.append({
                    "project_id": p.id,
                    "project_title": p.title,
                    "file_name": os.path.basename(agent.path),
                    "content": content
                })
            except Exception as e:
                print(f"⚠️ [WARNING] 物理文件读取失败: {e}")
                continue

    return {
        "success": True,
        "files": result_files
    }