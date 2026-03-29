from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from domain.schemas.chat import CreateChatSchema
from infrastructure.database import RoleEnum, User
from repositories.chat_repo import ChatRepository


class ChatService:
	def __init__(self, repo: ChatRepository):
		self.repo = repo
		
	async def create_direct_chat(self, public_id: str, friend_uuid: str):
		if public_id == friend_uuid:
			raise HTTPException(status_code=400, detail="Cannot create chat with yourself")
		
		chat = await self.repo.create_direct_chat(public_id, friend_uuid)

		return chat
	
	async def create_group_chat(self, user_uuid: str, creds: CreateChatSchema):
		# user_uuid: int, chat_name: str, member_uuids: list[str]
		chat = await self.repo.create_group_chat(user_uuid, creds.name, creds.member_uuids)

		return chat
	
	async def my_chats(self, user: User):
		return await self.repo.get_chats_by_user(user.public_id)
	
	async def delete_chat(self, user_uuid: str, chat_id: int):
		'''Delete chat'''
		try:
			await self.repo.delete_chat(user_uuid, chat_id)
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"{e}")
	
	async def rename_chat(self, chat_id: int, new_name: str, public_id: str):
		'''Rename chat'''
		try:
			await self.repo.rename_chat(chat_id, new_name, public_id=public_id)
		except ValueError:
			raise HTTPException(status_code=400, detail="Failed to rename chat")
		
	async def get_chat_history(self, chat_id: int, public_id: str):
		'''Get chat history'''
		try:
			history = await self.repo.get_chat_history(chat_id, public_id)
			return history
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"{e}")
	
	async def invite_user(self, user_uuid: str, friend_uuid: str, chat_id: int):
		'''Invite a user to a group chat'''
		try:
			await self.repo.add_user_to_chat(user_uuid, friend_uuid, chat_id)
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"{e}")
		
	async def leave_chat(self, user_uuid: str, chat_uuid: str):
		'''Leave chat'''
		try:
			await self.repo.leave_chat(user_uuid, chat_uuid)
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"{e}")