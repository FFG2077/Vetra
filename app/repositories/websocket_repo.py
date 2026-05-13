from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import UserInChat, User, Message, Chat


class WebSocketRepository:
	def __init__(self, session: AsyncSession):
		self.db = session

	async def handshake(self, public_id: str, chat_uuid: str) -> bool | ValueError:
		'''Check if user with public_id is part of chat with chat_uuid'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()
		chat_id_subquery = select(Chat.id).where(Chat.public_id == chat_uuid).scalar_subquery()

		query = select(exists().where(
			and_(
				UserInChat.user_id == subquery,
				UserInChat.chat_id == chat_id_subquery
			)
		))

		result = await self.db.execute(query)

		if result.scalar():
			return True
		else:
			raise ValueError("Chat not found or no permission")
		
	async def create_message(self, public_id: str, chat_uuid: str, content: str) -> Message:
		'''Create and store a new message in the database'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()
		chat_id_subquery = select(Chat.id).where(Chat.public_id == chat_uuid).scalar_subquery()

		message = Message(
			chat_id=chat_id_subquery,
			user_id=subquery,
			content=content
		)

		self.db.add(message)
		await self.db.commit()
		await self.db.refresh(message)

		return message
	
	async def get_chat_members(self, chat_uuid: str) -> list[str]:
		"""Get all member public_ids in chat"""
		chat_id_subquery = select(Chat.id).where(Chat.public_id == chat_uuid).scalar_subquery()
		query = await self.db.execute(
      select(User.public_id)
      .join(UserInChat, User.id == UserInChat.user_id)
      .where(UserInChat.chat_id == chat_id_subquery)
    )
		
		members = query.scalars().all()
		return [str(m) for m in members]