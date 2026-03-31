from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user
from domain.schemas.chat import CreateChatSchema
from infrastructure.database import User, get_db
from repositories.chat_repo import ChatRepository
from services.chat_service import ChatService


router = APIRouter()

@router.post('/create_direct_chat', summary='Create chat with a friend')
async def create_direct_chat(friend_uuid: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	'''Create a direct chat with a friend'''
	repo = ChatRepository(db)
	service = ChatService(repo)

	chat = await service.create_direct_chat(user.public_id, friend_uuid)

	return chat


@router.post('/create_group_chat', summary='Create a group chat')
async def create_group_chat(creds: CreateChatSchema, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	'''Create a group chat'''
	repo = ChatRepository(db)
	service = ChatService(repo)

	chat = await service.create_group_chat(user.public_id, creds)

	return chat


@router.delete('/delete_chat', summary='Delete chat')
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)
	
	await service.delete_chat(user.public_id, chat_id)

	return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/rename_chat', summary='Rename chat')
async def rename_chat(chat_uuid: str, new_name: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	await service.rename_chat(chat_uuid, new_name, user.public_id)

	return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/invite_user', summary='Invite a user to a group')
async def invite_user(user_uuid: str, chat_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	await service.invite_user(user.public_id, user_uuid, chat_id)

	return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/history', summary='Get chat history')
async def get_chat_history(chat_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	history = await service.get_chat_history(chat_id, user.public_id)

	return history


@router.post('/leave_chat', summary='leave chat')
async def leave_chat(chat_uuid: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	await service.leave_chat(user.public_id, chat_uuid)

	return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/kick_user', summary='Kick user from group')
async def kick_user(user_uuid: str, chat_uuid: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
	repo = ChatRepository(db)
	service = ChatService(repo)

	await service.kick_user(user.public_id, user_uuid, chat_uuid)

	return Response(status_code=status.HTTP_204_NO_CONTENT)