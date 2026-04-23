"""
migrate_profiles.py — Перенос in-memory _profiles в таблицу founder_profiles.

Запуск (из backend/):
    source venv/bin/activate
    python migrate_profiles.py

Что делает:
  1. Применяет alembic upgrade head (создаёт таблицы если нет)
  2. Для каждого профиля из seed-данных создаёт User + FounderProfileDB
  3. Выводит итоговый отчёт

Повторный запуск безопасен — upsert, дубли не создаются.
"""
import asyncio
import subprocess
import sys
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from database.database import AsyncSessionLocal, engine, init_db
from database import crud
from questionnaire_normalizer import normalize, ONBOARDING_SCHEMA_VERSION
from main import _map_raw_to_normalizer  # noqa: E402

# ─── Seed-профили в questionnaire-формате (совпадают с conftest.py fixtures) ──
SEED_PROFILES = [
    {
        "user_id": "founder_builder",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "3+",
        "self_actions": ["built_mvp", "shipped_product", "wrote_code", "managed_team"],
        "primary_role": "builder",
        "no_go_role_tags": [],
        "decision_style": "analyze_first",
        "conflict_style": "calm_discussion",
        "work_mode": "tight_pair",
        "tempo": "iterate_fast",
        "sync_frequency": "daily",
        "accountability_disappear_label": "never",
        "accountability_ownership_label": "always",
        "big5_o_1": 4, "big5_o_2": 4,
        "big5_c_1": 5, "big5_c_2": 5, "big5_c_3": 4,
        "big5_e_1": 3, "big5_e_2": 2,
        "big5_a_1": 4, "big5_a_2": 4,
        "big5_es_1": 4, "big5_es_2": 4,
    },
    {
        "user_id": "founder_seller",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "1-2",
        "self_actions": ["sold_to_customers", "grew_revenue", "found_investors"],
        "primary_role": "seller",
        "no_go_role_tags": [],
        "decision_style": "fast_risky",
        "conflict_style": "calm_discussion",
        "work_mode": "tight_pair",
        "tempo": "iterate_fast",
        "sync_frequency": "daily",
        "accountability_disappear_label": "rarely",
        "accountability_ownership_label": "always",
        "big5_o_1": 4, "big5_o_2": 5,
        "big5_c_1": 4, "big5_c_2": 4, "big5_c_3": 5,
        "big5_e_1": 5, "big5_e_2": 5,
        "big5_a_1": 4, "big5_a_2": 4,
        "big5_es_1": 4, "big5_es_2": 5,
    },
    {
        "user_id": "founder_operator",
        "time_commitment": "full_time",
        "no_salary_readiness": "12_months",
        "intent_goal": "build_company",
        "launched_projects": "1-2",
        "self_actions": ["managed_team", "built_processes"],
        "primary_role": "operator",
        "no_go_role_tags": [],
        "decision_style": "discuss_first",
        "conflict_style": "calm_discussion",
        "work_mode": "team",
        "tempo": "build_right_first",
        "sync_frequency": "twice_a_week",
        "accountability_disappear_label": "never",
        "accountability_ownership_label": "usually",
    },
]


async def run_migration():
    """Применяет alembic upgrade head."""
    print("═" * 60)
    print("Step 1: alembic upgrade head")
    print("═" * 60)
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"⚠  alembic output:\n{result.stdout}\n{result.stderr}")
        # Не падаем — таблицы могут уже существовать (init_db создаёт их через SQLAlchemy)
    else:
        print(result.stdout or "✓ migrations applied")


async def seed_profiles():
    """Создаёт User + FounderProfileDB для каждого seed-профиля."""
    print("\n" + "═" * 60)
    print("Step 2: seeding founder_profiles")
    print("═" * 60)

    # Убедимся что таблицы существуют (на случай если alembic не запустился)
    await init_db()

    created = 0
    updated = 0
    errors = 0

    async with AsyncSessionLocal() as db:
        for raw in SEED_PROFILES:
            user_id_str = raw["user_id"]
            try:
                # Маппим questionnaire-формат → формат normalize()
                mapped = _map_raw_to_normalizer(raw)
                profile = normalize(mapped)

                # Создаём или получаем User
                db_user = await crud.get_user_by_name(db, user_id_str)
                if not db_user:
                    db_user = await crud.create_user(db, {
                        "name": user_id_str,
                        "role": profile.primary_role.value,
                        "skills": [],
                        "psycho_profile": profile.big5.model_dump() if profile.big5 else None,
                    })
                    action = "created"
                else:
                    action = "existing"

                # Создаём или обновляем FounderProfileDB
                existing_fp = await crud.get_founder_profile_by_user_id(db, db_user.id)
                await crud.create_founder_profile(
                    db,
                    user_id=db_user.id,
                    raw_answers=raw,
                    normalized_profile=profile.model_dump(),
                    schema_version=ONBOARDING_SCHEMA_VERSION,
                )

                if existing_fp:
                    updated += 1
                    print(f"  ↻  {user_id_str} (user_id={db_user.id}) — updated")
                else:
                    created += 1
                    print(f"  ✓  {user_id_str} (user_id={db_user.id}) — {action}, profile created")

            except Exception as e:
                errors += 1
                print(f"  ✗  {user_id_str} — ERROR: {e}")

    print(f"\n{'─' * 40}")
    print(f"  Created: {created}  |  Updated: {updated}  |  Errors: {errors}")
    print(f"{'─' * 40}")
    return errors == 0


async def verify():
    """Проверяет что записи действительно сохранились."""
    print("\n" + "═" * 60)
    print("Step 3: verification")
    print("═" * 60)
    async with AsyncSessionLocal() as db:
        profiles = await crud.list_founder_profiles(db)
        print(f"  founder_profiles в БД: {len(profiles)}")
        for p in profiles:
            print(f"    id={p.id[:8]}… user_id={p.user_id} "
                  f"schema={p.onboarding_schema_version} active={p.is_active}")
    return len(profiles) > 0


async def main():
    await run_migration()
    ok = await seed_profiles()
    verified = await verify()

    print("\n" + "═" * 60)
    if ok and verified:
        print("✅  Migration complete — founder_profiles ready")
    else:
        print("⚠   Migration finished with issues — check output above")
    print("═" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
