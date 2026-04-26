from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class OceanProfile(BaseModel):
    openness: int = Field(50, ge=0, le=100)
    conscientiousness: int = Field(50, ge=0, le=100)
    extraversion: int = Field(50, ge=0, le=100)
    agreeableness: int = Field(50, ge=0, le=100)
    neuroticism: int = Field(50, ge=0, le=100)

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: List[str] = []
    github_projects: List[str] = []
    experience: List[str] = []
    ocean: OceanProfile
    created_at: datetime
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[str]] = None
    ocean: Optional[OceanProfile] = None

class MatchCard(BaseModel):
    id: str
    name: str
    role: str
    location: Optional[str]
    bio: Optional[str]
    skills: List[str]
    compatibility: float
    avatar_url: Optional[str] = None
    ocean: OceanProfile

class MatchAction(BaseModel):
    matched_user_id: str
    action: str

class MatchResult(BaseModel):
    match_id: str
    status: str
    is_mutual: bool

class MessageCreate(BaseModel):
    receiver_id: str
    text: str = Field(..., min_length=1, max_length=2000)

class MessageOut(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    text: str
    is_ai_suggestion: bool
    created_at: datetime
    class Config:
        from_attributes = True

class ConversationOut(BaseModel):
    id: str
    partner_id: str
    partner_name: str
    partner_avatar: Optional[str]
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int

class HealthCheck(BaseModel):
    status: str
    version: str
    database: str
    redis: Optional[str] = None
    qdrant: Optional[str] = None
