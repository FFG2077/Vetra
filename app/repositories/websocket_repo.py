from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import UserInChat, User, Message


class WebSocketRepository:
	def __init__(self, session: AsyncSession):
		self.db = session

	async def handshake(self, public_id: str, chat_id: int) -> bool | ValueError:
		'''Check if user with public_id is part of chat with chat_id'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()

		query = select(exists().where(
			and_(
				UserInChat.user_id == subquery,
				UserInChat.chat_id == chat_id
			)
		))

		result = await self.db.execute(query)

		if result.scalar():
			return True
		else:
			raise ValueError("Chat not found or no permission")
		
	async def create_message(self, public_id: str, chat_id: int, content: str) -> Message:
		'''Create and store a new message in the database'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()

		message = Message(
			chat_id=chat_id,
			user_id=subquery,
			content=content
		)

		self.db.add(message)
		await self.db.commit()
		await self.db.refresh(message)

		return message
	
	async def get_chat_members(self, chat_id: int) -> list[str]:
		"""Get all member public_ids in chat"""
		query = await self.db.execute(
      select(User.public_id)
      .join(UserInChat, User.id == UserInChat.user_id)
      .where(UserInChat.chat_id == chat_id)
    )
		
		members = query.scalars().all()
		return [str(m) for m in members]