from sqlalchemy.orm import Session
from app.models.auth_model import UserDB
from app.schemas.auth_schemas import UserCreate, UserUpdate

def get_user_by_id(db: Session, user_id: int):
    """根据 ID 获取用户"""
    return db.query(UserDB).filter(UserDB.id == user_id).first()

def get_user_by_name(db: Session, user_name: str):
    """根据用户名获取用户（用于防重校验和登录）"""
    return db.query(UserDB).filter(UserDB.user_name == user_name).first()

def get_all_users(db: Session):
    """获取所有用户列表"""
    return db.query(UserDB).all()

def create_user(db: Session, user_in: UserCreate):
    """创建新用户"""
    db_user = UserDB(user_name=user_in.user_name, password=user_in.password, avatar=None)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: UserDB, user_in: UserUpdate):
    """升级为通用更新函数（支持改用户名、密码、头像）"""
    if user_in.user_name is not None:
        db_user.user_name = user_in.user_name
    if user_in.password is not None:
        db_user.password = user_in.password
    if user_in.avatar is not None:
        db_user.avatar = user_in.avatar
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: UserDB):
    """删除用户"""
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, user_name: str, password: str):
    """校验用户明文密码是否正确"""
    return db.query(UserDB).filter(
        UserDB.user_name == user_name, 
        UserDB.password == password
    ).first()