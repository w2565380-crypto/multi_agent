import os
import sys

# 1. 确保 Python 能够正确找到 app 包 (将当前 backend 目录加入到环境变量中)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# 🌟 修改点：引入 text 函数来包裹原生 SQL 语句
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from ai_agent_company.backend.app.schemas.auth_schemas import UserCreate
from ai_agent_company.backend.app.crud import auth_crud

def run_database_tests():
    print("=================== 开始数据库功能测试 ===================")
    
    # 2. 初始化数据库连接（若表不存在则创建，并确保开启 SQLite 外键约束）
    with engine.connect() as con:
        # 🌟 修改点：使用 text() 转换字符串，解决 ObjectNotExecutableError 报错
        con.execute(text("PRAGMA foreign_keys = ON;"))
        # SqlAlchemy 2.0 显式连接需要手动 commit 或使用事务
        con.commit()
        
    Base.metadata.create_all(bind=engine)

    # 3. 创建测试专用的数据库 Session 会话
    db = SessionLocal()
    
    try:
        # ---------------------------------------------------------
        # 测试任务 2：插入一个 user_name：wzp1，password：123456 的用户
        # （先做插入，方便后续有数据可以查询）
        # ---------------------------------------------------------
        print("\n[测试任务 2] 正在尝试插入用户 wzp1...")
        
        # 检查是否已经存在 wzp1，防止重复插入触发 UNIQUE 唯一性报错
        existing_wzp1 = auth_crud.get_user_by_name(db, user_name="wzp1")
        if not existing_wzp1:
            # 构造 Pydantic 传输模型
            new_user_data = UserCreate(user_name="wzp1", password="123456")
            # 调用 crud.py 中的写入逻辑
            inserted_user = auth_crud.create_user(db, user_in=new_user_data)
            print(f"✅ 成功插入新用户！ID: {inserted_user.id}, 用户名: {inserted_user.user_name}, 密码: {inserted_user.password}")
        else:
            print(f"ℹ️ 用户 wzp1 已经存在于数据库中，无需重复插入。当前ID为: {existing_wzp1.id}")


        # ---------------------------------------------------------
        # 测试任务 1：查询 user_name 为 fbw 的用户
        # ---------------------------------------------------------
        print("\n[测试任务 1] 正在查询 user_name 为 fbw 的用户...")
        user_fbw = auth_crud.get_user_by_name(db, user_name="fbw")
        
        if user_fbw:
            print(f"✅ 成功查询到用户 fbw！用户详情 -> ID: {user_fbw.id}, 用户名: {user_fbw.user_name}, 密码: {user_fbw.password}")
        else:
            print("❌ 未查询到用户 fbw。")
            
            # 【可选补充测试】：如果没找到，我们现场帮他注册一个，以便观察查到的效果
            print("💡 提示：为了验证查询成功后的效果，现在为你现场创建一个 fbw 用户...")
            fbw_data = UserCreate(user_name="fbw", password="password_fbw")
            auth_crud.create_user(db, user_in=fbw_data)
            
            # 再次查询
            user_fbw_retry = auth_crud.get_user_by_name(db, user_name="fbw")
            print(f"✅ 再次查询成功！ID: {user_fbw_retry.id}, 用户名: {user_fbw_retry.user_name}, 密码: {user_fbw_retry.password}")

    except Exception as e:
        print(f"💥 测试过程中发生异常错误: {e}")
        db.rollback()
    finally:
        # 4. 关闭测试数据库会话，释放文件锁
        db.close()
        print("\n=================== 数据库功能测试结束 ===================")

if __name__ == "__main__":
    run_database_tests()