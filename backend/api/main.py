"""
Syndi API with Database
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import uvicorn

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db, init_db, close_db
from db import crud

from models.big_five import BigFiveTest, TestSubmission
from models.user import UserCreate

app = FastAPI(title="Syndi API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

big_five_test = BigFiveTest()


@app.on_event("startup")
async def startup():
    await init_db()
    print("✓ Database ready")


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/")
async def root():
    return {"name": "Syndi API", "version": "1.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected"}


@app.get("/test/questions")
async def get_questions():
    """Get Big Five test questions"""
    questions = big_five_test.get_questions()
    return [{"id": q["id"], "text": q["text"], "trait": q["trait"]} for q in questions]


@app.post("/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create new user"""
    existing = await crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_dict = user_data.dict()
    user_dict['id'] = str(uuid4())
    user = await crud.create_user(db, user_dict)
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "message": "User created successfully"
    }


@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users"""
    users = await crud.get_users(db)
    return [{"id": u.id, "email": u.email, "name": u.name} for u in users]


@app.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name}


@app.post("/test/submit")
async def submit_test(submission: TestSubmission, db: AsyncSession = Depends(get_db)):
    """Submit Big Five test"""
    user = await crud.get_user(db, str(submission.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = big_five_test.calculate_profile(submission.answers)
    scores = {
        'openness': profile.openness,
        'conscientiousness': profile.conscientiousness,
        'extraversion': profile.extraversion,
        'agreeableness': profile.agreeableness,
        'neuroticism': profile.neuroticism
    }
    await crud.create_big_five_result(db, str(submission.user_id), scores)
    
    return {
        "user_id": str(submission.user_id),
        "profile": scores,
        "message": "Results saved"
    }


@app.get("/agents")
async def list_agents():
    return {"agents": [{"id": "kristina", "name": "Kristina", "role": "UX Designer"}]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
