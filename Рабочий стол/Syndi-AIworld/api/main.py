"""
Syndi API - FastAPI Application
Главное приложение FastAPI для платформы Syndi
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from uuid import UUID
import uvicorn

from models.big_five import (
    BigFiveTest, TestSubmission, BigFiveResponse, 
    QuestionResponse, AnswerScale
)
from models.user import (
    UserProfile, UserCreate, UserUpdate, UserPublicProfile,
    Skill, SkillLevel, UserGoal
)
from services.matching import MatchingEngine, QuickMatcher, MatchResult
from services.llm import get_llm_service
from agents import get_kristina, AgentResponse

# Инициализация приложения
app = FastAPI(
    title="Syndi API",
    description="API для платформы персональных AI-агентов Syndi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервисов
big_five_test = BigFiveTest()
matching_engine = MatchingEngine()

# Временное хранилище (в production - PostgreSQL)
users_db: dict[UUID, UserProfile] = {}


# ============ HEALTH CHECK ============

@app.get("/health", tags=["System"])
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "healthy",
        "service": "Syndi API",
        "version": "1.0.0"
    }


@app.get("/status", tags=["System"])
async def system_status():
    """
    Подробный статус системы
    
    Returns:
        Информация о всех компонентах системы
    """
    llm_service = get_llm_service()
    llm_status = llm_service.get_status()
    
    return {
        "api": {
            "status": "healthy",
            "version": "1.0.0"
        },
        "llm": {
            "provider": llm_status["provider"],
            "available": llm_status["available"],
            "initialized": llm_status["client_initialized"]
        },
        "database": {
            "type": "in-memory",
            "users": len(users_db)
        },
        "agents": {
            "kristina": {
                "status": "active",
                "conversations": get_kristina().total_conversations
            }
        }
    }


# ============ BIG FIVE TEST ENDPOINTS ============

@app.get("/test/questions", response_model=List[QuestionResponse], tags=["Big Five Test"])
async def get_test_questions():
    """
    Получить список вопросов для теста Big Five (15 вопросов)
    
    Returns:
        Список вопросов с id, текстом и типом черты (OCEAN)
    """
    questions = big_five_test.get_questions()
    return questions


@app.post("/test/submit", response_model=BigFiveResponse, tags=["Big Five Test"])
async def submit_test(submission: TestSubmission):
    """
    Отправить ответы на тест Big Five и получить профиль
    
    Args:
        submission: Список ответов {question_id, value (1-5)}
    
    Returns:
        Профиль Big Five с интерпретацией
    """
    try:
        # Конвертируем ответы в словарь
        answers = {a.question_id: a.value for a in submission.answers}
        
        # Проверяем, что все 15 вопросов отвечены
        if len(answers) != 15:
            raise HTTPException(
                status_code=400,
                detail=f"Необходимо ответить на все 15 вопросов. Получено: {len(answers)}"
            )
        
        # Рассчитываем профиль
        profile = big_five_test.calculate_profile(answers)
        
        # Генерируем интерпретацию
        interpretation = generate_interpretation(profile)
        
        return BigFiveResponse(
            openness=profile.openness,
            conscientiousness=profile.conscientiousness,
            extraversion=profile.extraversion,
            agreeableness=profile.agreeableness,
            neuroticism=profile.neuroticism,
            dominant_trait=profile.get_dominant_trait().value,
            interpretation=interpretation
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def generate_interpretation(profile) -> dict:
    """Генерирует текстовую интерпретацию профиля"""
    
    def interpret_score(score: float, high_desc: str, low_desc: str) -> str:
        if score >= 70:
            return high_desc
        elif score <= 30:
            return low_desc
        else:
            return "Сбалансированный показатель"
    
    return {
        "openness": interpret_score(
            profile.openness,
            "Высокая открытость: творческий, любите новый опыт",
            "Низкая открытость: практичный, предпочитаете проверенное"
        ),
        "conscientiousness": interpret_score(
            profile.conscientiousness,
            "Высокая добросовестность: организованный, надёжный",
            "Низкая добросовестность: гибкий, спонтанный"
        ),
        "extraversion": interpret_score(
            profile.extraversion,
            "Высокая экстраверсия: общительный, энергичный",
            "Низкая экстраверсия: интроверт, предпочитаете уединение"
        ),
        "agreeableness": interpret_score(
            profile.agreeableness,
            "Высокая доброжелательность: эмпатичный, командный игрок",
            "Низкая доброжелательность: прямолинейный, конкурентный"
        ),
        "neuroticism": interpret_score(
            profile.neuroticism,
            "Высокий нейротизм: эмоционально чувствительный",
            "Низкий нейротизм: эмоционально стабильный, спокойный"
        )
    }


# ============ USER ENDPOINTS ============

@app.post("/users", response_model=UserProfile, tags=["Users"])
async def create_user(user_data: UserCreate):
    """
    Создать нового пользователя
    
    Args:
        user_data: Данные для создания профиля
    
    Returns:
        Созданный профиль пользователя
    """
    user = UserProfile(
        email=user_data.email,
        name=user_data.name,
        title=user_data.title,
        bio=user_data.bio,
        location=user_data.location,
        skills=user_data.skills,
        goals=user_data.goals
    )
    users_db[user.id] = user
    return user


@app.get("/users/{user_id}", response_model=UserProfile, tags=["Users"])
async def get_user(user_id: UUID):
    """Получить профиль пользователя по ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return users_db[user_id]


@app.patch("/users/{user_id}", response_model=UserProfile, tags=["Users"])
async def update_user(user_id: UUID, update_data: UserUpdate):
    """Обновить профиль пользователя"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user = users_db[user_id]
    update_dict = update_data.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(user, field, value)
    
    users_db[user_id] = user
    return user


@app.post("/users/{user_id}/big-five", response_model=UserProfile, tags=["Users"])
async def save_user_big_five(user_id: UUID, submission: TestSubmission):
    """
    Сохранить результаты Big Five теста для пользователя
    
    Args:
        user_id: ID пользователя
        submission: Ответы на тест
    
    Returns:
        Обновленный профиль пользователя
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Рассчитываем профиль
    answers = {a.question_id: a.value for a in submission.answers}
    profile = big_five_test.calculate_profile(answers)
    
    # Сохраняем
    user = users_db[user_id]
    user.big_five = profile
    user.has_completed_test = True
    users_db[user_id] = user
    
    return user


@app.get("/users", response_model=List[UserProfile], tags=["Users"])
async def list_users(
    goal: Optional[UserGoal] = None,
    skill: Optional[str] = None,
    limit: int = Query(default=20, le=100)
):
    """
    Получить список пользователей с фильтрацией
    
    Args:
        goal: Фильтр по цели
        skill: Фильтр по навыку
        limit: Лимит результатов
    """
    users = list(users_db.values())
    
    if goal:
        users = [u for u in users if goal in u.goals]
    
    if skill:
        users = [
            u for u in users 
            if any(s.name.lower() == skill.lower() for s in u.skills)
        ]
    
    return users[:limit]


# ============ MATCHING ENDPOINTS ============

@app.get("/matches/{user_id}", tags=["Matching"])
async def find_matches(
    user_id: UUID,
    limit: int = Query(default=5, le=20),
    min_score: float = Query(default=30.0, ge=0, le=100)
):
    """
    Найти совместимых пользователей для матчинга
    
    Args:
        user_id: ID пользователя
        limit: Максимальное количество результатов
        min_score: Минимальный балл совместимости
    
    Returns:
        Список совпадений с оценками совместимости
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user = users_db[user_id]
    candidates = [u for u in users_db.values() if u.id != user_id]
    
    if not candidates:
        return {"matches": [], "message": "Пока нет других пользователей для матчинга"}
    
    matches = matching_engine.find_matches(user, candidates, limit, min_score)
    
    return {
        "user_id": str(user_id),
        "total_matches": len(matches),
        "matches": [m.to_dict() for m in matches]
    }


@app.get("/matches/{user_id}/quick", tags=["Matching"])
async def quick_match(user_id: UUID):
    """
    Быстрый матчинг (упрощённый алгоритм для MVP)
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Топ-5 лучших совпадений
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user = users_db[user_id]
    candidates = [u for u in users_db.values() if u.id != user_id]
    
    if not candidates:
        return {"matches": [], "message": "Пока нет других пользователей для матчинга"}
    
    matches = QuickMatcher.quick_match(user, candidates)
    
    return {
        "user_id": str(user_id),
        "total_matches": len(matches),
        "matches": [m.to_dict() for m in matches]
    }


# ============ SEED DATA ============

@app.post("/seed", tags=["Development"])
async def seed_test_data():
    """
    Создать тестовые данные для разработки
    
    Returns:
        Список созданных пользователей
    """
    test_users = [
        UserCreate(
            email="alex@example.com",
            name="Александр Петров",
            title="Full-stack Developer",
            bio="Опытный разработчик с фокусом на Python и React",
            location="Москва",
            skills=[
                Skill(name="Python", level=SkillLevel.EXPERT, years_experience=5),
                Skill(name="React", level=SkillLevel.ADVANCED, years_experience=3),
                Skill(name="PostgreSQL", level=SkillLevel.ADVANCED, years_experience=4),
            ],
            goals=[UserGoal.FIND_COFOUNDER, UserGoal.JOIN_PROJECT]
        ),
        UserCreate(
            email="maria@example.com",
            name="Мария Иванова",
            title="UX/UI Designer",
            bio="Дизайнер с опытом в продуктовых стартапах",
            location="Санкт-Петербург",
            skills=[
                Skill(name="Figma", level=SkillLevel.EXPERT, years_experience=4),
                Skill(name="User Research", level=SkillLevel.ADVANCED, years_experience=3),
                Skill(name="Prototyping", level=SkillLevel.ADVANCED, years_experience=4),
            ],
            goals=[UserGoal.FIND_COFOUNDER, UserGoal.JOIN_PROJECT]
        ),
        UserCreate(
            email="dmitry@example.com",
            name="Дмитрий Сидоров",
            title="Product Manager",
            bio="Продакт с опытом в B2B SaaS",
            location="Москва",
            skills=[
                Skill(name="Product Strategy", level=SkillLevel.EXPERT, years_experience=6),
                Skill(name="Agile", level=SkillLevel.ADVANCED, years_experience=5),
                Skill(name="Data Analysis", level=SkillLevel.INTERMEDIATE, years_experience=2),
            ],
            goals=[UserGoal.FIND_TEAM, UserGoal.HIRE_TALENT]
        ),
        UserCreate(
            email="anna@example.com",
            name="Анна Козлова",
            title="Marketing Specialist",
            bio="Маркетолог с фокусом на digital и growth",
            location="Казань",
            skills=[
                Skill(name="Digital Marketing", level=SkillLevel.ADVANCED, years_experience=4),
                Skill(name="SEO", level=SkillLevel.ADVANCED, years_experience=3),
                Skill(name="Content Strategy", level=SkillLevel.INTERMEDIATE, years_experience=2),
            ],
            goals=[UserGoal.JOIN_PROJECT, UserGoal.NETWORKING]
        ),
    ]
    
    created = []
    for user_data in test_users:
        user = UserProfile(
            email=user_data.email,
            name=user_data.name,
            title=user_data.title,
            bio=user_data.bio,
            location=user_data.location,
            skills=user_data.skills,
            goals=user_data.goals
        )
        users_db[user.id] = user
        created.append(user)
    
    return {
        "message": f"Создано {len(created)} тестовых пользователей",
        "users": created
    }


# ============ AGENT ENDPOINTS ============

from pydantic import BaseModel, Field
from agents.base import AgentRole


class ChatRequest(BaseModel):
    """Запрос на общение с агентом"""
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict] = Field(default=None)


class ChatResponse(BaseModel):
    """Ответ агента"""
    agent_id: str
    agent_name: str
    content: str
    message_type: str
    suggestions: List[str]
    actions: List[Dict]
    metadata: Dict


class AgentInfo(BaseModel):
    """Информация об агенте"""
    id: str
    name: str
    role: str
    expertise: List[str]
    personality: str
    active_users: int


@app.get("/agents", response_model=List[AgentInfo], tags=["AI Agents"])
async def list_agents():
    """
    Получить список доступных AI-агентов
    
    Returns:
        Список агентов с их специализациями
    """
    kristina = get_kristina()
    
    agents = [
        AgentInfo(
            id=kristina.agent_id,
            name=kristina.name,
            role=kristina.role.value,
            expertise=kristina.expertise,
            personality=kristina.personality,
            active_users=len(kristina.memories)
        )
    ]
    
    return agents


@app.get("/agents/{agent_id}", response_model=AgentInfo, tags=["AI Agents"])
async def get_agent_info(agent_id: str):
    """
    Получить информацию о конкретном агенте
    
    Args:
        agent_id: ID агента
    
    Returns:
        Информация об агенте
    """
    if agent_id == "kristina_ux_001":
        kristina = get_kristina()
        return AgentInfo(
            id=kristina.agent_id,
            name=kristina.name,
            role=kristina.role.value,
            expertise=kristina.expertise,
            personality=kristina.personality,
            active_users=len(kristina.memories)
        )
    
    raise HTTPException(status_code=404, detail="Агент не найден")


@app.post("/agents/{agent_id}/chat", response_model=ChatResponse, tags=["AI Agents"])
async def chat_with_agent(agent_id: str, user_id: UUID, request: ChatRequest):
    """
    Отправить сообщение AI-агенту
    
    Args:
        agent_id: ID агента (например, "kristina_ux_001")
        user_id: ID пользователя
        request: Сообщение и контекст
    
    Returns:
        Ответ агента с предложениями и действиями
    """
    if agent_id != "kristina_ux_001":
        raise HTTPException(status_code=404, detail="Агент не найден")
    
    # Получаем агента
    agent = get_kristina()
    
    # Обрабатываем сообщение
    try:
        response = await agent.process_message(
            user_id=str(user_id),
            message=request.message,
            context=request.context
        )
        
        return ChatResponse(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            content=response.content,
            message_type=response.message_type.value,
            suggestions=response.suggestions,
            actions=response.actions,
            metadata=response.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка агента: {str(e)}")


@app.get("/agents/{agent_id}/history/{user_id}", tags=["AI Agents"])
async def get_chat_history(agent_id: str, user_id: UUID, limit: int = Query(default=20, le=50)):
    """
    Получить историю общения с агентом
    
    Args:
        agent_id: ID агента
        user_id: ID пользователя
        limit: Количество сообщений
    
    Returns:
        История сообщений
    """
    if agent_id != "kristina_ux_001":
        raise HTTPException(status_code=404, detail="Агент не найден")
    
    agent = get_kristina()
    memory = agent.get_memory(str(user_id))
    
    return {
        "agent_id": agent_id,
        "user_id": str(user_id),
        "total_messages": len(memory.messages),
        "messages": memory.get_context(limit=limit)
    }


@app.delete("/agents/{agent_id}/history/{user_id}", tags=["AI Agents"])
async def clear_chat_history(agent_id: str, user_id: UUID):
    """
    Очистить историю общения с агентом
    
    Args:
        agent_id: ID агента
        user_id: ID пользователя
    """
    if agent_id != "kristina_ux_001":
        raise HTTPException(status_code=404, detail="Агент не найден")
    
    agent = get_kristina()
    memory = agent.get_memory(str(user_id))
    memory.clear()
    
    return {
        "message": "История общения очищена",
        "agent_id": agent_id,
        "user_id": str(user_id)
    }


# ============ MAIN ============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
