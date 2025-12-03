from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user
from domain.schemas.chat import CreateChatSchema
from infrastructure.database import User, get_db
from repositories.chat_repo import ChatRepository
from services.chat_service import ChatService


router = APIRouter()

@router.post('/create_chat', summary='Create chat')
async def create_chat(chat_data: CreateChatSchema, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	chat = await service.create_chat(chat_data, user)

	return chat


@router.delete('/delete_chat', summary='Delete chat')
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)
	
	await service.delete_chat(chat_id)

	return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.post('/invite_user', summary='Invite a user to a group')
# async def invite_user(user_id: int,chat_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
# 	repo = ChatRepository(db)
# 	service = ChatService(repo)

# 	await service.invite_user(user_id, chat_id)

# 	return Response(status_code=status.HTTP_204_NO_CONTENT)