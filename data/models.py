"""
数据模型
定义数据库表结构
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default='zh')
    is_subscribed = Column(Boolean, default=False)
    push_time = Column(String(5), default='09:00')  # HH:MM 格式
    timezone = Column(String(50), default='Asia/Shanghai')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class FearGreedData(Base):
    """恐慌贪婪指数数据表"""
    __tablename__ = 'fear_greed_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    current_value = Column(Integer, nullable=False)
    rating = Column(String(50), nullable=False)
    previous_close = Column(Integer, nullable=True)
    week_ago = Column(Integer, nullable=True)
    month_ago = Column(Integer, nullable=True)
    year_ago = Column(Integer, nullable=True)
    source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FearGreedData(date={self.date}, value={self.current_value}, rating={self.rating})>"


class VixData(Base):
    """VIX 波动率指数数据表"""
    __tablename__ = 'vix_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    current_value = Column(Float, nullable=False)
    previous_close = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VixData(date={self.date}, value={self.current_value})>"


class MarketIndicator(Base):
    """市场指标数据表"""
    __tablename__ = 'market_indicators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False)  # put_call, market_breadth 等
    data = Column(Text, nullable=False)  # JSON 格式存储具体数据
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketIndicator(date={self.date}, type={self.indicator_type})>"


class PushLog(Base):
    """推送日志表"""
    __tablename__ = 'push_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 关联 User.id
    telegram_id = Column(Integer, nullable=False)
    message_type = Column(String(50), nullable=False)  # daily, manual, alert 等
    message_content = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # success, failed, pending
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PushLog(user_id={self.user_id}, type={self.message_type}, status={self.status})>"


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemConfig(key={self.key}, value={self.value})>"


# 数据传输对象 (DTOs)
class UserDTO:
    """用户数据传输对象"""
    
    def __init__(self, telegram_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language_code: str = 'zh'):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language_code = language_code
        
    @classmethod
    def from_telegram_user(cls, telegram_user):
        """从 Telegram User 对象创建 DTO"""
        return cls(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language_code=telegram_user.language_code or 'zh'
        )


class FearGreedDataDTO:
    """恐慌贪婪指数数据传输对象"""
    
    def __init__(self, current_value: int, rating: str, 
                 previous_close: int = None, week_ago: int = None,
                 month_ago: int = None, year_ago: int = None,
                 source: str = 'Unknown'):
        self.current_value = current_value
        self.rating = rating
        self.previous_close = previous_close
        self.week_ago = week_ago
        self.month_ago = month_ago
        self.year_ago = year_ago
        self.source = source
        self.date = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'current_value': self.current_value,
            'rating': self.rating,
            'previous_close': self.previous_close,
            'week_ago': self.week_ago,
            'month_ago': self.month_ago,
            'year_ago': self.year_ago,
            'source': self.source,
            'date': self.date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建 DTO"""
        return cls(
            current_value=data.get('current_value', 0),
            rating=data.get('rating', 'Unknown'),
            previous_close=data.get('previous_close'),
            week_ago=data.get('week_ago'),
            month_ago=data.get('month_ago'),
            year_ago=data.get('year_ago'),
            source=data.get('source', 'Unknown')
        ) 