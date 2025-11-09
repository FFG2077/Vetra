from repositories.chat_repo import ChatRepository
from infrastructure.database import RoleEnum, User
from domain.schemas.chat import CreateChatSchema

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class ChatService:
	def __init__(self, repo: ChatRepository):
		self.repo = repo
		
	async def create_chat(self, chat_data: CreateChatSchema, user: User):
		chat = await self.repo.create_chat(chat_data)

		try:
			if chat.is_group:
				await self.repo.add_user_to_chat(user.id, chat.id, RoleEnum.ADMIN)
			else:
				await self.repo.add_user_to_chat(user.id, chat.id, RoleEnum.MEMBER)
		except IntegrityError:
			raise HTTPException(status_code=400, detail="User already in chat")
		
		return chat
	
	async def my_chats(self, user: User):
		return await self.repo.get_chats_by_user(user.id)