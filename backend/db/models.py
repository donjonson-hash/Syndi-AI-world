"""
SQLAlchemy Database Models - SQLite version
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, JSON
from db.database import Base


class UserDB(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    title = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    skills = Column(JSON, default=list)  # Добавлено
    goals = Column(JSON, default=list)   # Добавлено
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BigFiveResultDB(Base):
    __tablename__ = 'big_five_results'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    openness = Column(Float, nullable=False)
    conscientiousness = Column(Float, nullable=False)
    extraversion = Column(Float, nullable=False)
    agreeableness = Column(Float, nullable=False)
    neuroticism = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
