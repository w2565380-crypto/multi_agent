import os
import shutil
from sqlalchemy.orm import Session
from app.models.projects_model import ProjectDB
from app.models.auth_model import UserDB  # 🌟 新增引入：用于做路径隔离的用户名查询
from app.schemas.projects_schemas import ProjectCreate

# 精准计算 backend/exports/ 物理路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 🌟 修复定位：使其退回到 backend/ 目录下，确保 exports/ 文件夹位置正确
EXPORTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "exports")

def create_project(db: Session, user_id: int, project_in: ProjectCreate) -> ProjectDB:
    """【增】创建新仿真项目，并在 exports/{username}/ 目录下物理创建对应的资产文件夹"""
    # 1. 🌟 新增：先查出当前用户的用户名，用于做物理路径隔离
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    username = user.user_name if user else "default_user"

    db_project = ProjectDB(
        user_id=user_id,
        title=project_in.title,
        description=project_in.description,
        status="INITIAL"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 2. 🌟 修改：物理创建专属资产文件夹时，拼入用户名 username
    safe_folder_name = f"project_{db_project.id}_{db_project.title}"
    project_folder_path = os.path.join(EXPORTS_DIR, username, safe_folder_name)
    try:
        os.makedirs(project_folder_path, exist_ok=True)
        print(f"📁 成功物理创建账号隔离的专属文件夹: {project_folder_path}")
    except Exception as e:
        print(f"❌ 物理文件夹创建失败: {e}")

    return db_project


def get_project_by_id(db: Session, project_id: int) -> ProjectDB:
    """【查】根据项目 ID 获取单条项目基础信息"""
    return db.query(ProjectDB).filter(ProjectDB.id == project_id).first()


def get_projects_by_user(db: Session, user_id: int) -> list[ProjectDB]:
    """【查】获取某个用户名下的所有仿真项目列表"""
    return db.query(ProjectDB).filter(ProjectDB.user_id == user_id).all()


def update_project_status_or_zip(db: Session, project_id: int, status: str = None, zip_path: str = None) -> ProjectDB:
    """【改】更新项目状态（如 RUNNING, COMPLETED）或代码压缩包网络路径"""
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    if status is not None:
        db_project.status = status
    if zip_path is not None:
        db_project.zip_path = zip_path
        
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project_completely(db: Session, project_id: int) -> bool:
    """【删】物理删除项目记录，并连带强制擦除本地对应的物理 exports/{username}/project_... 文件夹"""
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return False

    # 1. 🌟 新增：先查出当前用户的用户名，用于定位物理隔离路径
    user = db.query(UserDB).filter(UserDB.id == db_project.user_id).first()
    username = user.user_name if user else "default_user"

    # 2. 🌟 修改：获取对应的隔离物理文件夹路径
    safe_folder_name = f"project_{db_project.id}_{db_project.title}"
    project_folder_path = os.path.join(EXPORTS_DIR, username, safe_folder_name)

    # 3. 从数据库中物理抹除记录（由于建立了外键 ON DELETE CASCADE，绑定的 project_agents 数据会自动被 SQLite 清空）
    db.delete(db_project)
    db.commit()

    # 4. 擦除本地物理文件夹及其下的所有源码资产
    if os.path.exists(project_folder_path):
        try:
            shutil.rmtree(project_folder_path)
            print(f"🧹 已成功清理项目 {project_id} 的本地物理资产文件夹: {project_folder_path}")
        except Exception as e:
            print(f"⚠️ 数据库记录已删，但本地物理文件夹清理失败: {e}")

    return True