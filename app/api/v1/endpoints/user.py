from infrastructure.database import get_db, User
from fastapi import APIRouter, Depends
from domain.schemas.user import UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from core.auth import get_current_user

from repositories.user_repo import UserRepository
from repositories.chat_repo import ChatRepository

from services.chat_service import ChatService


router = APIRouter()

@router.get('/get_users', summary='Get all users')
async def get_users(db: AsyncSession=Depends(get_db)):
	repo = UserRepository(db)
	users = await repo.get_users()
	return users


@router.get('/get_me', summary='get current user', response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
	return user


@router.get('/my_chats', summary='Get my chats')
async def my_chats(db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	chats = await service.my_chats(user)

	return chats