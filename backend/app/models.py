import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False, default="Founder")
    location = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(500))
    skills = Column(JSON, default=list)
    github_projects = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ocean_openness = Column(Integer, default=50)
    ocean_conscientiousness = Column(Integer, default=50)
    ocean_extraversion = Column(Integer, default=50)
    ocean_agreeableness = Column(Integer, default=50)
    ocean_neuroticism = Column(Integer, default=50)

class Match(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    matched_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("idx_matches_user_pair", "user_id", "matched_user_id", unique=True),)

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_ai_suggestion = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("idx_messages_conversation", "sender_id", "receiver_id"),)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    last_message = Column(Text)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    unread_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (Index("idx_conversations_pair", "user_id", "partner_id", unique=True),)
