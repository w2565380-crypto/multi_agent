from sqlalchemy.orm import Session
from app.models.agents_model import ProjectAgentDB

def add_project_agent_result(db: Session, project_id: int, role: str, agent_name: str, elapsed_time: int, final_output: str = None, path: str = None) -> ProjectAgentDB:
    """【增】录入一个 AI 角色的初始仿真成果"""
    db_agent = ProjectAgentDB(
        project_id=project_id,
        role=role,
        agent_name=agent_name,
        elapsed_time=elapsed_time,
        final_output=final_output,
        path=path
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_project_agents(db: Session, project_id: int) -> list[ProjectAgentDB]:
    """【查】根据项目 ID 获取该项目下所有 AI 角色的成果列表"""
    return db.query(ProjectAgentDB).filter(ProjectAgentDB.project_id == project_id).all()


def get_agent_by_id(db: Session, agent_id: int) -> ProjectAgentDB:
    """【查】根据智能体单条记录的 ID 获取详情"""
    return db.query(ProjectAgentDB).filter(ProjectAgentDB.id == agent_id).first()


def update_agent_output(db: Session, agent_id: int, final_output: str = None, path: str = None, additional_time: int = 0) -> ProjectAgentDB:
    """【改】更新或追加智能体的最终文本资产、代码文件内容，并累加耗时"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return None
        
    if final_output is not None:
        db_agent.final_output = final_output
    if path is not None:
        db_agent.path = path
    if additional_time > 0:
        db_agent.elapsed_time += additional_time  # 累加研发耗时
        
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent_result(db: Session, agent_id: int) -> bool:
    """【删】单独物理删除某一个智能体的生成成果"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return False
        
    db.delete(db_agent)
    db.commit()
    return True