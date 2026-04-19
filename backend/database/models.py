from sqlalchemy import String, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(50)) # Например, "Founder" или "Candidate"

    # Храним сложные данные как JSON
    skills: Mapped[dict] = mapped_column(JSON) 
    psycho_profile: Mapped[dict] = mapped_column(JSON) # Big Five результаты
    enneagram: Mapped[dict] = mapped_column(JSON)     # { "type": 5, "wing": "6w5" }
    
    # Поле для кэшированного результата мэтчинга (опционально)
    match_score: Mapped[float] = mapped_column(Integer, nullable=True)
    ai_interpretation: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<User(name='{self.name}', role='{self.role}')>"

    def to_dict(self):
        """Превращает объект БД в обычный словарь для нашего алгоритма"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "skills": self.skills,
            "psycho_profile": self.psycho_profile,
            "enneagram": self.enneagram
        }
