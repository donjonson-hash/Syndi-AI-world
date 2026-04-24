"""
AvatarFactory — создание AI-аватаров для со-фаундеров Syndi.
Адаптировано из kristina-revolutionary/avatar_platform/avatar_factory.py
"""
from __future__ import annotations
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .profession_profile import get_profession, ProfessionProfile
from .emotional_core import EmotionalCore

logger = logging.getLogger(__name__)


@dataclass
class AvatarInstance:
    """Экземпляр AI-аватара со-фаундера."""
    avatar_id: str
    user_id: int
    founder_name: str
    role_id: str                        # "builder", "seller", "operator", "researcher"
    profession: Optional[ProfessionProfile]
    emotional_core: EmotionalCore
    match_id: Optional[str] = None      # ID матча, при котором создан
    partner_user_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict = field(default_factory=dict)  # проектный контекст

    def get_system_prompt(self) -> str:
        """Собрать system prompt для LLM."""
        base = self.profession.build_system_prompt(self.founder_name) if self.profession else (
            f"Ты AI-аватар со-фаундера {self.founder_name}. Помогай с задачами."
        )
        emotional_state = self.emotional_core.get_state()
        style_hint = emotional_state.get("llm_style_hint", "")
        return f"{base}\n\n{style_hint}"

    def to_dict(self) -> Dict:
        emotional_state = self.emotional_core.get_state()
        return {
            "avatar_id": self.avatar_id,
            "user_id": self.user_id,
            "founder_name": self.founder_name,
            "role_id": self.role_id,
            "profession": {
                "title": self.profession.title,
                "core_skills": self.profession.core_skills,
                "routine_tasks": self.profession.routine_tasks,
            } if self.profession else None,
            "emotional_state": emotional_state,
            "match_id": self.match_id,
            "partner_user_id": self.partner_user_id,
            "created_at": self.created_at,
        }


class AvatarFactory:
    """Фабрика для создания аватаров со-фаундеров."""

    # In-memory хранилище: user_id -> AvatarInstance
    _avatars: Dict[int, AvatarInstance] = {}

    @classmethod
    def create_avatar(
        cls,
        user_id: int,
        founder_name: str,
        role_id: str,
        match_id: Optional[str] = None,
        partner_user_id: Optional[int] = None,
        big5: Optional[Dict] = None,
    ) -> AvatarInstance:
        profession = get_profession(role_id)
        if profession is None:
            logger.warning(f"Профессия '{role_id}' не найдена, создаём базовый аватар")

        emotional_core = EmotionalCore(big5=big5)

        avatar = AvatarInstance(
            avatar_id=str(uuid.uuid4()),
            user_id=user_id,
            founder_name=founder_name,
            role_id=role_id,
            profession=profession,
            emotional_core=emotional_core,
            match_id=match_id,
            partner_user_id=partner_user_id,
        )

        cls._avatars[user_id] = avatar
        logger.info(f"Аватар создан: user_id={user_id}, role={role_id}, match={match_id}")
        return avatar

    @classmethod
    def get_avatar(cls, user_id: int) -> Optional[AvatarInstance]:
        return cls._avatars.get(user_id)

    @classmethod
    def list_avatars(cls) -> List[Dict]:
        return [a.to_dict() for a in cls._avatars.values()]
