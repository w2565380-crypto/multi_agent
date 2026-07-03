import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db, IMAGES_DIR
from app.schemas.auth_schemas import UserCreate, UserUpdate, UserResponse, UserLogin
from app.crud import auth_crud

router = APIRouter(prefix="/api/users", tags=["用户认证与管理"])

# 辅助函数：将数据库中的文件名动态拼装成让前端能直接访问的静态 URL 链接
def convert_to_accessible_user(user, base_url: str = "http://127.0.0.1:8000"):
    if user and user.avatar:
        # 如果数据库存的是 avatar.jpg，则拼装为 http://127.0.0.1:8000/avatars/avatar.jpg
        user.avatar = f"{base_url}/avatars/{user.avatar}"
    return user

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="创建用户")
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = auth_crud.get_user_by_name(db, user_name=user_in.user_name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户名已被占用"
        )
    db_user = auth_crud.create_user(db, user_in=user_in)
    return convert_to_accessible_user(db_user)


@router.get("", response_model=List[UserResponse], summary="获取所有用户列表")
def get_all_users(db: Session = Depends(get_db)):
    users = auth_crud.get_all_users(db)
    return [convert_to_accessible_user(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse, summary="根据ID获取指定用户")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = auth_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return convert_to_accessible_user(user)


@router.put("/{user_id}", response_model=UserResponse, summary="修改用户信息")
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = auth_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    if user_in.user_name and user_in.user_name != user.user_name:
        conflicting_user = auth_crud.get_user_by_name(db, user_name=user_in.user_name)
        if conflicting_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被其他人占用，请更换"
            )
            
    updated_user = auth_crud.update_user(db, db_user=user, user_in=user_in)
    return convert_to_accessible_user(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = auth_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    auth_crud.delete_user(db, db_user=user)
    return None


@router.post("/login", summary="用户登录校验")
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = auth_crud.authenticate_user(db, user_name=user_in.user_name, password=user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="用户名或密码错误"
        )
    # 登录成功后同样转换，保证前端能够直接拿到头像 URL 渲染
    accessible_user = convert_to_accessible_user(user)
    return {
        "status": "success", 
        "user_id": accessible_user.id, 
        "user_name": accessible_user.user_name,
        "avatar": accessible_user.avatar
    }


# 🌟 新增接口：专门提供给前端上传头像图片的独立物理文件接口
@router.post("/{user_id}/upload-avatar", summary="上传/更换用户头像")
async def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = auth_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    # 限制上传格式只能是图片
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
        
    # 提取文件后缀名，如 .jpg
    ext = os.path.splitext(file.filename)[1]
    # 头像文件名命名规范：user_用户ID_avatar.jpg (防止重名覆盖和汉字乱码)
    avatar_filename = f"user_{user_id}_avatar{ext}"
    file_save_path = os.path.join(IMAGES_DIR, avatar_filename)
    
    # 将前端传上来的文件流写入到 backend/data/images/ 下
    with open(file_save_path, "wb") as f:
        f.write(await file.read())
        
    # 更新数据库中的 avatar 属性为该文件名
    user_update_data = UserUpdate(avatar=avatar_filename)
    auth_crud.update_user(db, db_user=user, user_in=user_update_data)
    
    return {
        "status": "success", 
        "message": "头像上传成功", 
        "avatar_url": f"http://127.0.0.1:8000/avatars/{avatar_filename}"
    }