"""
数据库管理模块
处理数据库连接、初始化和 CRUD 操作
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import aiosqlite
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .models import Base, User, FearGreedData, VixData, MarketIndicator, PushLog, SystemConfig, UserDTO, FearGreedDataDTO
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# 创建数据库引擎
if DATABASE_URL.startswith('sqlite'):
    # 异步 SQLite 引擎
    async_engine = create_async_engine(
        DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///'),
        echo=False
    )
    # 同步 SQLite 引擎（用于初始化）
    sync_engine = create_engine(DATABASE_URL, echo=False)
else:
    # 其他数据库（PostgreSQL, MySQL 等）
    async_engine = create_async_engine(DATABASE_URL, echo=False)
    sync_engine = create_engine(DATABASE_URL, echo=False)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
SessionLocal = sessionmaker(bind=sync_engine)


async def init_database():
    """初始化数据库"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=sync_engine)
        logger.info("数据库表创建成功")
        
        # 初始化系统配置
        await init_system_config()
        logger.info("系统配置初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


async def init_system_config():
    """初始化系统配置"""
    default_configs = [
        {'key': 'bot_version', 'value': '1.0.0', 'description': 'Bot 版本号'},
        {'key': 'last_data_update', 'value': '', 'description': '最后数据更新时间'},
        {'key': 'total_users', 'value': '0', 'description': '总用户数'},
        {'key': 'active_subscribers', 'value': '0', 'description': '活跃订阅用户数'},
        {'key': 'daily_push_enabled', 'value': 'true', 'description': '是否启用每日推送'},
    ]
    
    async with AsyncSessionLocal() as session:
        for config in default_configs:
            existing = await session.get(SystemConfig, config['key'])
            if not existing:
                new_config = SystemConfig(**config)
                session.add(new_config)
        
        await session.commit()


@asynccontextmanager
async def get_db_session():
    """获取数据库会话的上下文管理器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            await session.close()


class UserRepository:
    """用户数据仓库"""
    
    @staticmethod
    async def create_user(user_dto: UserDTO) -> User:
        """创建新用户"""
        async with get_db_session() as session:
            # 检查用户是否已存在
            existing_user = await session.get(User, user_dto.telegram_id)
            if existing_user:
                return existing_user
            
            new_user = User(
                telegram_id=user_dto.telegram_id,
                username=user_dto.username,
                first_name=user_dto.first_name,
                last_name=user_dto.last_name,
                language_code=user_dto.language_code
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
    
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """根据 Telegram ID 获取用户"""
        async with get_db_session() as session:
            return await session.get(User, telegram_id)
    
    @staticmethod
    async def update_user_subscription(telegram_id: int, is_subscribed: bool) -> bool:
        """更新用户订阅状态"""
        async with get_db_session() as session:
            user = await session.get(User, telegram_id)
            if user:
                user.is_subscribed = is_subscribed
                user.updated_at = datetime.utcnow()
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def update_user_push_time(telegram_id: int, push_time: str, timezone: str = None) -> bool:
        """更新用户推送时间"""
        async with get_db_session() as session:
            user = await session.get(User, telegram_id)
            if user:
                user.push_time = push_time
                if timezone:
                    user.timezone = timezone
                user.updated_at = datetime.utcnow()
                await session.commit()
                return True
            return False
    
    @staticmethod
    async def get_subscribed_users() -> List[User]:
        """获取所有订阅用户"""
        async with get_db_session() as session:
            result = await session.execute(
                session.query(User).filter(User.is_subscribed == True)
            )
            return result.scalars().all()
    
    @staticmethod
    async def update_user_last_active(telegram_id: int):
        """更新用户最后活跃时间"""
        async with get_db_session() as session:
            user = await session.get(User, telegram_id)
            if user:
                user.last_active = datetime.utcnow()
                await session.commit()


# 便捷函数
async def get_user_or_create(telegram_user) -> User:
    """获取或创建用户"""
    user_dto = UserDTO.from_telegram_user(telegram_user)
    return await UserRepository.create_user(user_dto)


async def is_user_subscribed(telegram_id: int) -> bool:
    """检查用户是否订阅"""
    user = await UserRepository.get_user_by_telegram_id(telegram_id)
    return user.is_subscribed if user else False