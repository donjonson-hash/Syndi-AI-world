import asyncio
from sqlalchemy import select
from database.database import engine, AsyncSessionLocal, Base
from database.models import User
from database.crud import create_user, get_all_candidates

# Данные наших героев из предыдущего чата
mikhail_data = {
    "name": "Mikhail",
    "role": "Founder",
    "skills": {"Python": 0.9, "Management": 0.8},
    "psycho_profile": {"openness": 0.2, "conscientiousness": 0.9, "extraversion": 0.4, "agreeableness": 0.3, "neuroticism": 0.1},
    "enneagram": {"type": 8, "wing": "8w7"}
}

michelle_data = {
    "name": "Michelle",
    "role": "Candidate",
    "skills": {"Genetic Engineering": 0.95, "Lab Management": 0.8},
    "psycho_profile": {"openness": 0.9, "conscientiousness": 0.7, "extraversion": 0.2, "agreeableness": 0.6, "neuroticism": 0.4},
    "enneagram": {"type": 5, "wing": "5w4"} # В примере было 5 + 3, возьмем 5 как базу
}

async def init_db():
    # 1. Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Открываем сессию
    async with AsyncSessionLocal() as db:
        print("🗄️ Создаем таблицы... OK")
        
        # Проверяем, есть ли уже Михаил, чтобы не дублировать
        existing_mikhail = await db.execute(select(User).where(User.name == "Mikhail"))
        if not existing_mikhail.scalar_one_or_none():
            mikhail = await create_user(db, mikhail_data)
            print(f"✅ Сохранен: {mikhail}")
        else:
            print("⚠️ Михаил уже существует")

        existing_michelle = await db.execute(select(User).where(User.name == "Michelle"))
        if not existing_michelle.scalar_one_or_none():
            michelle = await create_user(db, michelle_data)
            print(f"✅ Сохранена: {michelle}")
        else:
            print("⚠️ Мишель уже существует")

if __name__ == "__main__":
    print("🚀 Запуск инициализации Базы Данных...")
    asyncio.run(init_db())
    print("🏁 Финиш!")
