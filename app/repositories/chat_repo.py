from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import Chat, UserInChat, RoleEnum
from domain.schemas.chat import ChatOut, CreateChatSchema


class ChatRepository:
	def __init__(self, session: AsyncSession):
		self.db = session

	async def create_chat(self, chat_data: CreateChatSchema):
		'''create chat'''
		chat = Chat(
			name=chat_data.name,
			is_group=chat_data.is_group
		)
		self.db.add(chat)
		await self.db.commit()
		await self.db.refresh(chat)

		chat = ChatOut.model_validate(chat)

		return chat

	async def add_user_to_chat(self, user_id: int, chat_id: int, role: RoleEnum.MEMBER):
		'''Add user in chat'''
		user_in_chat = UserInChat(
			user_id=user_id,
			chat_id=chat_id,
			role=role
		)

		self.db.add(user_in_chat)
		await self.db.commit()

	async def get_chats_by_user(self, user_id: int):
		'''Get chats by user'''
		query = await self.db.execute(
			select(Chat)
			.join(UserInChat, UserInChat.chat_id == Chat.id)
			.where(UserInChat.user_id == user_id)
		)

		result = query.scalars().all()
		
		return result

	async def delete_chat(self):
		'''Delete chat'''
