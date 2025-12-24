from sqlalchemy import and_, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import Chat, UserInChat, RoleEnum, User
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

	async def add_user_to_chat(self, public_id: str, chat_id: int, role: RoleEnum.MEMBER):
		'''Add user in chat'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()
		print(subquery)
		user_in_chat = UserInChat(
			user_id=subquery,
			chat_id=chat_id,
			role=role
		)

		self.db.add(user_in_chat)
		await self.db.commit()

	async def get_chats_by_user(self, public_id: int):
		'''Get chats by user id'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()
		query = await self.db.execute(
			select(Chat)
			.join(UserInChat, UserInChat.chat_id == Chat.id)
			.where(UserInChat.user_id == subquery)
		)

		result = query.scalars().all()
		
		return result

	async def delete_chat(self, chat_id):
		'''Delete chat'''
		query = await self.db.execute(
			delete(Chat)
			.where(Chat.id == chat_id)
		)
		await self.db.commit()

	async def rename_chat(self, chat_id: int, new_name: str, public_id: str):
		'''Rename chat'''
		user_subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()

		chat_subquery = select(UserInChat.chat_id).where(
			UserInChat.user_id == user_subquery
		).scalar_subquery()

		query = await self.db.execute(
			update(Chat)
			.where(
				Chat.id == chat_id,
				Chat.id.in_(chat_subquery)
			)
			.values(name=new_name)
		)
		if query.rowcount == 0:
			raise ValueError("Friend not found or not accepted")
		# await self.db.execute(
		# 	update(Chat)
		# 	.where(
		# 		Chat.user_id == user_subquery,
		# 		Chat.id == chat_id
		# 	)
		# 	.values(name=new_name)
		# )

		await self.db.commit()