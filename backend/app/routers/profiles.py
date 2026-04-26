from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from ..database import get_db
from ..models import User
from ..schemas import UserProfile, UserProfileUpdate, OceanProfile
from ..routers.auth import get_current_user

router = APIRouter()

def _to_profile(user: User) -> UserProfile:
    return UserProfile(
        id=str(user.id), email=user.email, name=user.name, role=user.role,
        location=user.location, bio=user.bio, avatar_url=user.avatar_url,
        skills=user.skills or [], github_projects=user.github_projects or [],
        experience=user.experience or [],
        ocean=OceanProfile(
            openness=user.ocean_openness, conscientiousness=user.ocean_conscientiousness,
            extraversion=user.ocean_extraversion, agreeableness=user.ocean_agreeableness,
            neuroticism=user.ocean_neuroticism,
        ),
        created_at=user.created_at,
    )

@router.get("/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_profile(user)

@router.get("/", response_model=List[UserProfile])
async def list_profiles(skip: int = 0, limit: int = 50, role: str = None, db: AsyncSession = Depends(get_db)):
    query = select(User).offset(skip).limit(limit)
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query)
    return [_to_profile(u) for u in result.scalars().all()]

@router.put("/me", response_model=UserProfile)
async def update_profile(data: UserProfileUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items() if k != "ocean"}
    if data.ocean:
        update_data.update({
            "ocean_openness": data.ocean.openness,
            "ocean_conscientiousness": data.ocean.conscientiousness,
            "ocean_extraversion": data.ocean.extraversion,
            "ocean_agreeableness": data.ocean.agreeableness,
            "ocean_neuroticism": data.ocean.neuroticism,
        })
    await db.execute(update(User).where(User.id == current_user.id).values(**update_data))
    await db.commit()
    result = await db.execute(select(User).where(User.id == current_user.id))
    return _to_profile(result.scalar_one())
