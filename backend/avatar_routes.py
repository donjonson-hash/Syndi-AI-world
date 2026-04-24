"""Avatar endpoints — получение и управление AI-аватарами со-фаундеров."""
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database.models import User as UserDB
from avatar_platform.avatar_factory import AvatarFactory

router = APIRouter(prefix="/api/v1/avatar", tags=["avatar"])


@router.get("/me")
async def get_my_avatar(current_user: UserDB = Depends(get_current_user)):
    """Получить AI-аватар текущего пользователя."""
    avatar = AvatarFactory.get_avatar(current_user.id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found. Complete a match first.")
    return avatar.to_dict()


@router.get("/list")
async def list_avatars(current_user: UserDB = Depends(get_current_user)):
    """Список всех аватаров (admin/debug)."""
    return {"avatars": AvatarFactory.list_avatars(), "total": len(AvatarFactory._avatars)}
