from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
from pathlib import Path

# Чтобы не было ошибок импорта при запуске из разных папок
sys.path.insert(0, str(Path(__file__).parent.parent))

# =============== ИМПОРТИРУЕМ НАШЕ НОВОЕ ЯДРО ===============
from core.database import engine, Base, get_async_session
from models.db_models import UserDB, SkillDB
from models.db_converters import db_to_pydantic
from services.matching import MatchingEngine

app = FastAPI(
    title="Syndi Match API (New Engine)",
    description="API для матчинга на основе психо-эзотерики и ИИ",
    version="2.0.0"
)

# CORS (чтобы можно было делать запросы с любого фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация нашего нового движка
matching_engine = MatchingEngine()

# =============== СИСТЕМНЫЕ ЭНДПОИНТЫ ===============

@app.on_event("startup")
async def startup():
    """Создаем таблицы при старте сервера"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных SQLite инициализирована")

@app.get("/")
async def root():
    return {"status": "Syndi API is Running (v2)", "engine": "Инь-Янь + Суперкар"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# =============== ЗАГРУЗКА ДАННЫХ (Для теста) ===============

@app.post("/demo_fill_db")
async def demo_fill_db():
    """Быстро добавить Михаила и Мишель в базу для теста API"""
    from sqlalchemy import delete # Импортируем команду удаления
    
    async for session in get_async_session():
        # 1. Правильно очищаем старую базу (Сначала навыки, потом пользователей)
        await session.execute(delete(SkillDB))
        await session.execute(delete(UserDB))
        
        # 2. Добавляем новых
        session.add_all([
            UserDB(
                name="Михаил (Программист)", email="m@t.ru", enneagram_type=5,
                skills=[SkillDB(name="Python", level="EXPERT"), SkillDB(name="AI", level="ADVANCED")]
            ),
            UserDB(
                name="Мишель (Биотех)", email="mi@t.ru", enneagram_type=3,
                skills=[SkillDB(name="Биология (база)", level="BEGINNER"), SkillDB(name="Генная инженерия", level="EXPERT")]
            )
        ])
        await session.commit()
    return {"status": "success", "message": "База очищена. Михаил и Мишель добавлены."}

# =============== ГЛАВНЫЙ ЭНДПОИНТ МЭТЧИНГА ===============

@app.get("/match/{founder_name}")
async def find_match(founder_name: str):
    """
    Найти пару для фаундера по имени.
    Пример: /match/Михаил
    """
    async for session in get_async_session():
        # 1. Ищем фаундера в БД (с подгрузкой навыков)
        stmt = select(UserDB).options(selectinload(UserDB.skills)).where(UserDB.name.ilike(f"%{founder_name}%"))
        result = await session.execute(stmt)
        founder_db = result.scalar_one_or_none()
        
        if not founder_db:
            raise HTTPException(status_code=404, detail=f"Фаундер '{founder_name}' не найден")

        # Конвертируем из формата БД в формат ИИ
        founder = db_to_pydantic(founder_db)

        # 2. Ищем всех остальных пользователей
        stmt_cand = select(UserDB).options(selectinload(UserDB.skills)).where(UserDB.id != founder_db.id)
        result_cand = await session.execute(stmt_cand)
        candidates_db = result_cand.scalars().all()
        
        if not candidates_db:
            raise HTTPException(status_code=404, detail="В базе нет других кандидатов")

        candidates = [db_to_pydantic(c) for c in candidates_db]

    # 3. ЗАПУСКАЕМ НАШ ИИ-ДВИЖОК (generate_ai_text=False для экономии)
    matches = await matching_engine.find_matches(
        founder, 
        candidates, 
        limit=5, 
        generate_ai_text=False 
    )
    
    if not matches:
        raise HTTPException(status_code=404, detail="Совместимых пар не найдено (скорее всего они не прошли порог 50%)")

    # 4. Отдаем красивый JSON (используем метод to_dict() из MatchResult)
    return JSONResponse(content={
        "founder": founder.name,
        "matches_count": len(matches),
        "results": [m.to_dict() for m in matches]
    })

# =============== ЗАПУСК ===============

if __name__ == "__main__":
    print("🚀 Запуск сервера FastAPI...")
    print("🔗 Документация доступна по адресу: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
