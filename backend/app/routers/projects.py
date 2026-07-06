# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
# from sqlalchemy.orm import Session
# import os

# from app.database import get_db
# # 引入组员写好的 CRUD 逻辑
# from app.crud.projects_crud import create_project, get_project_by_id
# from app.crud.auth_crud import get_user_by_id
# from app.schemas.projects_schemas import ProjectCreate
# from app.services.orchestrator import step_orchestrator
# from app.utils.file_helper import file_helper

# router = APIRouter(prefix="/api/projects", tags=["projects"])

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
#     """
#     用户创建新项目。
#     写入数据库记录，并在磁盘创建物理项目文件夹后，异步启动产品经理（PM）工作流。
#     """
#     user = get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="未找到该用户")

#     # 调用 CRUD 写入数据库，参数顺序已修正
#     project = create_project(db, user_id, project_in)

#     # 异步调用 Dify 产品经理工作流，不阻塞前端
#     background_tasks.add_task(step_orchestrator.step_1_run_pm, db, project.id)

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
#     """
#     处理人机交互审批（批准进入开发，或驳回让 PM 重新规划）。
#     """
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="未找到该项目")

#     # 调用异步处理函数
#     await step_orchestrator.step_2_handle_approval(db, project_id, approved, feedback)

#     return {
#         "success": True,
#         "message": "审批指令已下达，流程开始流转。"
#     }


# # =========================================================
# # 【接口 3】：获取用户的所有项目列表（刷新不丢失 - 左侧列表）
# # =========================================================
# @router.get("/")
# async def api_get_user_projects(user_id: int, db: Session = Depends(get_db)):
#     """
#     获取用户的所有仿真项目列表。
#     用于前端在页面刷新后，重新加载左侧列表或历史看板。
#     """
#     from app.crud.projects_crud import get_projects_by_user
#     projects = get_projects_by_user(db, user_id)
    
#     # 按照创建时间倒序（最新的在最前）
#     return [
#         {
#             "id": p.id,
#             "title": p.title,
#             "status": p.status,
#             "zip_path": p.zip_path
#         } for p in reversed(projects)
#     ]


# # =========================================================
# # 【接口 4】：获取单个项目的完整详情（刷新不丢失 - 详情恢复 & 状态轮询）
# # =========================================================
# @router.get("/{project_id}")
# async def api_get_project_detail(project_id: int, db: Session = Depends(get_db)):
#     """
#     获取单个项目的完整详情。
#     前端在刷新页面后，根据项目 ID 调用此接口，恢复界面上的需求描述、标题、当前状态等信息。
#     同时也作为前端高频轮询项目最新状态的接口。
#     """
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
# # 【接口 5】：获取项目网页成果预览 URL
# # =========================================================
# @router.get("/{project_id}/preview-url")
# async def api_get_preview_url(project_id: int, request: Request, db: Session = Depends(get_db)):
#     """
#     前端 <iframe> 预览地址获取接口。
#     支持账号物理路径安全隔离，自动检索并生成前端 <iframe> 所需的访问 URL。
#     """
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     # 1. 🌟 修复：安全查询用户名，拼入隔离路径
#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     folder_name = f"project_{project.id}_{project.title}"
    
#     # 2. 传入 username 获取正确的隔离物理路径
#     project_dir = file_helper.get_project_dir(username, project.id, project.title)

#     if not os.path.exists(project_dir):
#         raise HTTPException(status_code=404, detail="该项目物理文件夹尚未生成")

#     base_url = str(request.base_url)

#     # 3. 在生成的静态预览 URL 中也拼入 username
#     if os.path.exists(os.path.join(project_dir, "src", "index.html")):
#         preview_url = f"{base_url}previews/{username}/{folder_name}/src/index.html"
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
# # 【接口 6】：获取项目的 PRD 纯文本 (Markdown)
# # =========================================================
# @router.get("/{project_id}/prd")
# async def api_get_project_prd_text(project_id: int, db: Session = Depends(get_db)):
#     """
#     获取项目的 PRD 需求文档纯文本 (Markdown)。
#     满足前端直接用 Markdown 渲染器展示需求文档的需求。
#     """
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     try:
#         # 传入 username 读取正确的隔离物理文件
#         prd_content = file_helper.read_prd(username, project.id, project.title)
#         return {
#             "success": True,
#             "project_id": project_id,
#             "prd_content": prd_content
#         }
#     except Exception:
#         raise HTTPException(status_code=404, detail="需求文档尚未生成或已丢失，请稍后再试")
    


# # =========================================================
# # 【接口 7】：获取项目的 QA 测试报告 (Markdown)
# # =========================================================
# @router.get("/{project_id}/qa-report")
# async def api_get_project_qa_report_text(project_id: int, db: Session = Depends(get_db)):
#     """
#     【接口 7】：获取项目的 QA 测试报告 (Markdown)。
#     用于前端在项目完成后，直接渲染并展示详细的测试报告。
#     """
#     project = get_project_by_id(db, project_id)
#     if not project:
#         raise HTTPException(status_code=404, detail="项目不存在")

#     user = get_user_by_id(db, project.user_id)
#     username = user.user_name if user else "default_user"

#     try:
#         # 调用文件助手读取本地的 Test_Report.md 文本
#         qa_content = file_helper.read_qa_report(username, project.id, project.title)
#         return {
#             "success": True,
#             "project_id": project_id,
#             "qa_report": qa_content  # 返回纯 Markdown 字符串
#         }
#     except Exception:
#         raise HTTPException(status_code=404, detail="测试报告尚未生成或已丢失，请稍后再试")

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.crud.projects_crud import (
    create_project, 
    get_project_by_id, 
    get_projects_by_user,
    delete_project_completely
)
from app.crud.auth_crud import get_user_by_id
from app.schemas.projects_schemas import ProjectCreate
from app.services.orchestrator import step_orchestrator
from app.utils.file_helper import file_helper
router = APIRouter(prefix="/api/projects", tags=["projects"])
from app.database import get_db
# 引入底层标准 CRUD 接口
from app.crud.projects_crud import get_project_by_id, get_projects_by_user, delete_project_completely
from app.crud.agents_crud import get_project_agents


# =========================================================
# 【接口 1】：创建项目并启动仿真
# =========================================================
@router.post("/create")
async def api_create_project(
    user_id: int, 
    project_in: ProjectCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="未找到该用户")

    project = create_project(db, user_id, project_in)
    background_tasks.add_task(step_orchestrator.step_1_run_pm, project.id)

    return {
        "success": True,
        "message": "项目创建成功，产品经理开始规划需求...",
        "project_id": project.id,
        "status": project.status
    }


# =========================================================
# 【接口 2】：人机协作审批
# =========================================================
@router.post("/{project_id}/approve")
async def api_approve_project(
    project_id: int, 
    approved: bool, 
    feedback: str = "", 
    db: Session = Depends(get_db)
):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="未找到该项目")

    await step_orchestrator.step_2_handle_approval(db, project_id, approved, feedback)

    return {
        "success": True,
        "message": "审批指令已下达，流程开始流转。"
    }


# =========================================================
# 【接口 3】：获取用户的所有项目列表（历史看板）
# =========================================================
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


# =========================================================
# 【接口 4】：获取单个项目的完整详情（状态轮询与恢复）
# =========================================================
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


# =========================================================
# 【接口 5（安全升级）】：获取项目网页成果预览 URL（数据库驱动检测）
# =========================================================
@router.get("/{project_id}/preview-url")
async def api_get_preview_url(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    user = get_user_by_id(db, project.user_id)
    username = user.user_name if user else "default_user"

    # 🌟 核心升级：先去数据库查询 DEV 角色登记的相对路径（如 "src/"）
    agents = get_project_agents(db, project_id)
    dev_agent = next((a for a in agents if a.role == "DEV"), None)
    
    # 如果没开发完或者没有登记路径，报 404
    if not dev_agent or not dev_agent.path:
        raise HTTPException(status_code=404, detail="代码尚未生成，请等待程序员开发完成")

    # 拿取真实的文件夹路径
    folder_name = f"project_{project.id}_{project.title}"
    project_dir = file_helper.get_project_dir(username, project.id, project.title)
    
    # 拼接真正的源码目录（来自数据库 path，如 "exports/.../src"）
    real_src_dir = os.path.join(project_dir, dev_agent.path)

    base_url = str(request.base_url)

    # 动态匹配实际物理文件
    if os.path.exists(os.path.join(real_src_dir, "index.html")):
        preview_url = f"{base_url}previews/{username}/{folder_name}/{dev_agent.path}index.html"
    elif os.path.exists(os.path.join(project_dir, "index.html")):
        preview_url = f"{base_url}previews/{username}/{folder_name}/index.html"
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


# =========================================================
# 【接口 6（安全升级）】：获取项目的 PRD 纯文本 (Markdown)（数据库驱动读取）
# =========================================================
@router.get("/{project_id}/prd")
async def api_get_project_prd_text(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    user = get_user_by_id(db, project.user_id)
    username = user.user_name if user else "default_user"

    # 🌟 核心升级：从数据库读取产品经理登记的真实路径 (如 "PRD.md")
    agents = get_project_agents(db, project_id)
    pm_agent = next((a for a in agents if a.role == "PM"), None)
    if not pm_agent or not pm_agent.path:
        raise HTTPException(status_code=404, detail="产品需求文档（PRD）尚未生成")

    try:
        # 使用数据库中的相对路径精准加载
        prd_content = file_helper.read_file_by_db_path(username, project.id, project.title, pm_agent.path)
        return {
            "success": True,
            "project_id": project_id,
            "prd_content": prd_content
        }
    except Exception:
        raise HTTPException(status_code=404, detail="物理文件已丢失，请稍后再试")


# =========================================================
# 【接口 7（安全升级）】：获取项目的 QA 测试报告 (Markdown)（数据库驱动读取）
# =========================================================
@router.get("/{project_id}/qa-report")
async def api_get_project_qa_report_text(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    user = get_user_by_id(db, project.user_id)
    username = user.user_name if user else "default_user"

    # 🌟 核心升级：从数据库读取测试工程师登记的真实路径 (如 "Test_Report.md")
    agents = get_project_agents(db, project_id)
    qa_agent = next((a for a in agents if a.role == "QA"), None)
    if not qa_agent or not qa_agent.path:
        raise HTTPException(status_code=404, detail="测试报告尚未生成")

    try:
        # 使用数据库中的相对路径精准加载
        qa_content = file_helper.read_file_by_db_path(username, project.id, project.title, qa_agent.path)
        return {
            "success": True,
            "project_id": project_id,
            "qa_report": qa_content
        }
    except Exception:
        raise HTTPException(status_code=404, detail="物理文件已丢失，请稍后再试")


# =========================================================
# 【接口 8】：一键彻底删除项目（数据库 + 物理文件）
# =========================================================
@router.delete("/{project_id}")
async def api_delete_project_by_id(project_id: int, db: Session = Depends(get_db)):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    user = get_user_by_id(db, project.user_id)
    username = user.user_name if user else "default_user"

    # 1. 物理删除打包在 exports/{username} 下的压缩包
    zip_file_path = os.path.join(file_helper.exports_dir, username, f"project_{project_id}.zip")
    if os.path.exists(zip_file_path):
        try:
            os.remove(zip_file_path)
        except Exception as e:
            print(f"⚠️ [WARNING] 物理 ZIP 删除失败: {e}")

    # 2. 调用 delete_project_completely 官方接口，抹除数据库和对应的物理源码目录
    success = delete_project_completely(db, project_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除项目失败，数据库接口运行异常")

    return {
        "success": True,
        "message": f"项目 ID: {project_id} 及其本地源码、打包 ZIP、关联 AI 记录已全部成功安全彻底清理！"
    }

# =========================================================
# 【接口 9】：代码迭代修改（重新提意见修改）
# =========================================================
@router.post("/{project_id}/revise")
async def api_revise_project_code(
    project_id: int, 
    feedback: str, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    【接口 9】：对现有代码不满意，提交修改意见重新迭代。
    接口会异步调用后台重构逻辑，完成后自动重新测试并重新打包。
    """
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 异步触发后台迭代重构任务
    background_tasks.add_task(step_orchestrator.step_3_revise_dev, project_id, feedback)

    return {
        "success": True,
        "message": "代码重构指令已下达，程序员正在根据您的建议修改代码，请耐心等待并轮询状态..."
    }


# =========================================================
# 【接口 10】：一键下载项目 ZIP 源码压缩包
# =========================================================
@router.get("/{project_id}/download")
async def api_download_project_zip(project_id: int, db: Session = Depends(get_db)):
    """
    【接口 10】：一键下载项目的全部成果 ZIP 包（包含 PRD, 源码, 测试报告）。
    """
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if not project.zip_path:
        raise HTTPException(status_code=404, detail="该项目尚未打包，无法下载")

    # 1. 计算 ZIP 在服务器上的绝对物理路径
    # project.zip_path 存储的是 "exports/{username}/project_{id}.zip"
    # file_helper.exports_dir 存储的是 "/home/.../backend/exports"
    # 我们退到 backend/ 目录下进行拼接
    backend_root = os.path.dirname(file_helper.exports_dir)
    absolute_zip_path = os.path.join(backend_root, project.zip_path)

    # 2. 物理校验压缩包是否存在
    if not os.path.exists(absolute_zip_path):
        raise HTTPException(status_code=404, detail="物理压缩包文件在服务器上未找到，请重新生成项目")

    # 3. 🌟 以物理文件流的形式向浏览器吐出下载，并重命名为下载时的文件名
    safe_title = "".join([c for c in project.title if c.isalnum() or c in ('_', '-')])
    download_filename = f"Project_{project_id}_{safe_title}.zip"

    return FileResponse(
        path=absolute_zip_path,
        media_type="application/octet-stream",
        filename=download_filename  # 浏览器中下载下来显示的文件名
    )