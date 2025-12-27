from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from domain.schemas.chat import CreateChatSchema
from infrastructure.database import RoleEnum, User
from repositories.chat_repo import ChatRepository


class ChatService:
	def __init__(self, repo: ChatRepository):
		self.repo = repo
		
	async def create_chat(self, chat_data: CreateChatSchema, user: User):
		chat = await self.repo.create_chat(chat_data)

		try:
			if chat.is_group:
				await self.repo.add_user_to_chat(user.public_id, chat.id, RoleEnum.ADMIN)
			else:
				await self.repo.add_user_to_chat(user.public_id, chat.id, RoleEnum.MEMBER)
		except IntegrityError:
			raise HTTPException(status_code=400, detail="User already in chat")
		
		return chat
	
	async def my_chats(self, user: User):
		return await self.repo.get_chats_by_user(user.public_id)
	
	async def delete_chat(self, chat_id: int):
		'''Delete chat'''
		try:
			await self.repo.delete_chat(chat_id)
		except IntegrityError:
			raise HTTPException(status_code=400, detail="Failed to delete chat")
	
	async def rename_chat(self, chat_id: int, new_name: str, public_id: str):
		'''Rename chat'''
		try:
			await self.repo.rename_chat(chat_id, new_name, public_id=public_id)
		except ValueError:
			raise HTTPException(status_code=400, detail="Failed to rename chat")
	
	async def invite_user(self, user, friend_uuid: str, chat_id: int):
		'''Invite user'''
		try:
			chats = await self.repo.get_chats_by_user(friend_uuid)
			await self.repo.add_user_to_chat(user.public_id, friend_uuid, chat_id, RoleEnum.MEMBER)
		except IntegrityError:
			raise HTTPException(status_code=400, detail="Failed to invite user")