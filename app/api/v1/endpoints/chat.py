from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db, User
from domain.schemas.chat import CreateChatSchema
from repositories.chat_repo import ChatRepository
from services.chat_service import ChatService
from core.auth import get_current_user


router = APIRouter()

@router.post('/create_chat', summary='Create chat')
async def create_chat(chat_data: CreateChatSchema, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	await service.create_chat(chat_data, user)