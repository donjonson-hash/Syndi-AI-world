from pydantic import BaseModel
from typing import Optional, Dict, List

class UserProfile(BaseModel):
    user_id: str
    mbti_result: Optional[str] = None
    enneagram: Optional[str] = None
    psychomatrix: Optional[Dict] = None
    birthdate: Optional[str] = None
    tarot: Optional[Dict] = None
    quantum_paths: Optional[List[Dict]] = None
    madness: Optional[str] = None
    shadow: Optional[str] = None
    biorhythm: Optional[Dict] = None
    baizi: Optional[Dict] = None

    @classmethod
    async def load(cls, user_id: str) -> 'UserProfile':
        # Implementation (e.g., fetch from database)
        # For now, return a new instance with user_id
        return cls(user_id=user_id)

    async def save(self) -> None:
        # Implementation (e.g., save to database)
        pass

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        return cls(**data)

    def to_dict(self) -> Dict:
        return self.dict(exclude_unset=True)