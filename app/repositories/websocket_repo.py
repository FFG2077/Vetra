from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import UserInChat, User


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
			raise ValueError()