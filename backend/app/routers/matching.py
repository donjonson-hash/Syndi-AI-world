from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from ..database import get_db
from ..models import User, Match
from ..schemas import MatchCard, MatchAction, MatchResult, OceanProfile
from ..routers.auth import get_current_user

router = APIRouter()

def _compat(u: OceanProfile, m: OceanProfile) -> float:
    w = {"openness": 1, "conscientiousness": 1, "extraversion": 1.2, "agreeableness": 1, "neuroticism": 0.8}
    total = max_total = 0
    for t in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
        diff = abs(getattr(u, t) - getattr(m, t))
        score = max(0, min(100, 100 - abs(diff - 25) * 2 if t in ("extraversion", "neuroticism") else 100 - diff))
        total += score * w[t]
        max_total += 100 * w[t]
    return round((total / max_total) * 100)

@router.get("/discover", response_model=List[MatchCard])
async def discover(skip: int = 0, limit: int = 20, role: str = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(User).where(User.id != current_user.id)
    if role:
        query = query.where(User.role == role)
    users = (await db.execute(query)).scalars().all()
    uo = OceanProfile(openness=current_user.ocean_openness, conscientiousness=current_user.ocean_conscientiousness,
                      extraversion=current_user.ocean_extraversion, agreeableness=current_user.ocean_agreeableness,
                      neuroticism=current_user.ocean_neuroticism)
    cards = []
    for usr in users:
        mo = OceanProfile(openness=usr.ocean_openness, conscientiousness=usr.ocean_conscientiousness,
                          extraversion=usr.ocean_extraversion, agreeableness=usr.ocean_agreeableness,
                          neuroticism=usr.ocean_neuroticism)
        cards.append(MatchCard(id=str(usr.id), name=usr.name, role=usr.role, location=usr.location,
                               bio=usr.bio, skills=usr.skills or [], compatibility=_compat(uo, mo),
                               avatar_url=usr.avatar_url, ocean=mo))
    cards.sort(key=lambda x: x.compatibility, reverse=True)
    return cards[skip:skip+limit]

@router.post("/action", response_model=MatchResult)
async def action(data: MatchAction, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Match).where(and_(Match.user_id == current_user.id, Match.matched_user_id == data.matched_user_id)))
    existing = result.scalar_one_or_none()
    if existing:
        existing.status = data.action
        await db.commit()
        return MatchResult(match_id=str(existing.id), status=data.action, is_mutual=False)
    m = Match(user_id=current_user.id, matched_user_id=data.matched_user_id, compatibility_score=0, status=data.action)
    db.add(m)
    await db.commit()
    await db.refresh(m)
    mutual = (await db.execute(select(Match).where(and_(Match.user_id == data.matched_user_id, Match.matched_user_id == current_user.id, Match.status == "like")))).scalar_one_or_none()
    return MatchResult(match_id=str(m.id), status=data.action, is_mutual=bool(mutual))
