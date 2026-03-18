"""
User Models
Модели пользователей и их профилей
"""

from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID, uuid4

from .big_five import BigFiveProfile


class SkillLevel(str, Enum):
    """Уровень владения навыком"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """Навык пользователя"""
    name: str
    level: SkillLevel
    years_experience: Optional[float] = 0.0
    
    def get_weight(self) -> float:
        """Вес навыка для алгоритма матчинга"""
        weights = {
            SkillLevel.BEGINNER: 1.0,
            SkillLevel.INTERMEDIATE: 2.0,
            SkillLevel.ADVANCED: 3.0,
            SkillLevel.EXPERT: 4.0
        }
        return weights.get(self.level, 1.0)


class UserGoal(str, Enum):
    """Цели пользователя на платформе"""
    FIND_COFOUNDER = "find_cofounder"
    JOIN_PROJECT = "join_project"
    FIND_TEAM = "find_team"
    NETWORKING = "networking"
    MENTORSHIP = "mentorship"
    HIRE_TALENT = "hire_talent"


class UserProfile(BaseModel):
    """Полный профиль пользователя Syndi"""
    
    # Основная информация
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = "UTC"
    
    # Профессиональная информация
    title: Optional[str] = None  # Например: "UX Designer", "Full-stack Developer"
    company: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    
    # Навыки и цели
    skills: List[Skill] = Field(default_factory=list)
    goals: List[UserGoal] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)  # Интересы/индустрии
    
    # Психометрический профиль
    big_five: Optional[BigFiveProfile] = None
    has_completed_test: bool = False
    
    # Настройки
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Модель создания пользователя"""
    email: EmailStr
    name: str
    title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: List[Skill] = Field(default_factory=list)
    goals: List[UserGoal] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Модель обновления профиля"""
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[Skill]] = None
    goals: Optional[List[UserGoal]] = None
    interests: Optional[List[str]] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None


class UserPublicProfile(BaseModel):
    """Публичный профиль пользователя (для матчинга)"""
    id: UUID
    name: str
    avatar_url: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: List[Skill]
    goals: List[UserGoal]
    interests: List[str]
    big_five: Optional[BigFiveProfile] = None
    compatibility_score: Optional[float] = None  # Добавляется при матчинге


class MatchPreferences(BaseModel):
    """Предпочтения для поиска совпадений"""
    min_skill_match: float = Field(default=0.3, ge=0, le=1)
    min_personality_match: float = Field(default=0.5, ge=0, le=1)
    location_preference: Optional[str] = None  # "local", "remote", "any"
    goals_filter: Optional[List[UserGoal]] = None
    skills_filter: Optional[List[str]] = None  # Навыки, которые должны быть у матча
