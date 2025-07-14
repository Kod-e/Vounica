"""
数据库初始化脚本
用于创建数据库表结构和初始数据
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.user import User
from app.services.user_service import UserService

# 加载环境变量
load_dotenv()

# 数据库连接 URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/vounica")

async def init_db():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    # 创建引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True  # 显示 SQL 语句
    )
    
    # 创建会话工厂
    async_session_maker = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    async with engine.begin() as conn:
        # 创建所有表
        from app.core.db.base import Base
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建初始管理员用户
    await create_initial_admin(async_session_maker)
    
    # 关闭引擎
    await engine.dispose()
    
    print("数据库初始化完成！")

async def create_initial_admin(session_maker):
    """创建初始管理员用户"""
    async with session_maker() as session:
        try:
            # 检查是否已存在管理员用户
            user_service = UserService()
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            admin_password = os.getenv("ADMIN_PASSWORD", "password123")
            
            # 检查用户名是否已被占用
            if await user_service.repository.is_username_taken(session, admin_username):
                print(f"管理员用户 '{admin_username}' 已存在，跳过创建")
                return
            
            # 创建管理员用户
            print(f"正在创建管理员用户 '{admin_username}'...")
            await user_service.create_user(
                db=session,
                username=admin_username,
                email=admin_email,
                password=admin_password,
                is_admin=True
            )
            await session.commit()
            print(f"管理员用户 '{admin_username}' 创建成功！")
        except Exception as e:
            await session.rollback()
            print(f"创建管理员用户失败: {e}")
            raise

if __name__ == "__main__":
    # 运行初始化函数
    asyncio.run(init_db()) 