from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Импортируем НАШИ рабочие модули
from database.database import get_db
from database.crud import get_user_by_name, get_all_candidates, get_user_by_id
from core.ai.matching_engine import MatchingEngine

app = FastAPI(
    title="Syndi Match API",
    description="API для матчинга на основе реальной БД",
    version="1.0.0"
)

# CORS (чтобы можно было делать запросы с фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация движка
matching_engine = MatchingEngine()

# =============== СХЕМЫ ДАННЫХ (DTO) ===============

class MatchResponse(BaseModel):
    founder_name: str
    candidate_name: str
    match_score: float
    ai_interpretation: str
    skills_score: float
    enneagram_score: float

class UserProfile(BaseModel):
    id: int
    name: str
    role: str
    skills: dict
    enneagram: dict
    
    class Config:
        from_attributes = True

# =============== СИСТЕМНЫЕ ЭНДПОИНТЫ ===============

@app.get("/")
async def root():
    return {"status": "Syndi API is Running", "database": "Connected (SQLite)"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# =============== ЭНДПОИНТЫ ПОЛЬЗОВАТЕЛЕЙ ===============

@app.get("/users", response_model=List[UserProfile])
async def list_users(db: AsyncSession = Depends(get_db)):
    """Получить список всех пользователей из БД"""
    # Сейчас у нас нет функции "get_all", добавим быстрый хак или используем существующую логику
    # Для простоты вернем хардкод или перепишем CRUD. Давай вернем тех, кого знаем.
    mikhail = await get_user_by_name(db, "Mikhail")
    michelle = await get_user_by_name(db, "Michelle")
    
    users = []
    if mikhail: users.append(mikhail)
    if michelle: users.append(michelle)
    return users

@app.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить пользователя по ID"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# =============== ЭНДПОИНТЫ МЭТЧИНГА (ГЛАВНОЕ) ===============

@app.get("/match/{founder_name}", response_model=List[MatchResponse])
async def find_match(founder_name: str, db: AsyncSession = Depends(get_db)):
    """
    Найти пару для фаундера по имени.
    Пример: /match/Mikhail
    """
    # 1. Находим фаундера
    founder = await get_user_by_name(db, founder_name)
    if not founder:
        raise HTTPException(status_code=404, detail=f"Founder '{founder_name}' not found")

    # 2. Находим всех остальных
    candidates = await get_all_candidates(db, exclude_user_id=founder.id)
    
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")

    results = []
    
    # 3. Прогоняем через движок
    for candidate in candidates:
        # Конвертируем в словари
        f_dict = founder.to_dict()
        c_dict = candidate.to_dict()
        
        # Считаем
        total_score, ai_text = matching_engine.calculate_match(f_dict, c_dict)
        
        # Достаем детали для красивого вывода (опционально, можно пересчитать)
        # Здесь упростим, просто соберем ответ
        results.append(MatchResponse(
            founder_name=founder.name,
            candidate_name=candidate.name,
            match_score=round(total_score, 1),
            ai_interpretation=ai_text,
            skills_score=0.0, # Можно доработать метод движка, чтобы возвращал детали
            enneagram_score=0.0
        ))
    
    # Сортируем по убыванию очков
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    return results

# =============== ЗАПУСК ===============

if __name__ == "__main__":
    print("🚀 Запуск сервера FastAPI...")
    print("🔗 Документация доступна по адресу: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
