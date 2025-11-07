from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database import User
from domain.schemas.user import UserRegisterSchema, UserOut


class UserRepository:
	def __init__(self, session: AsyncSession):
		self.db = session

	async def get_users(self):
		'''get all users'''

		query = await self.db.execute(
			select(User)
		)
		result = query.scalars().all()
	
		return [UserOut.model_validate(u) for u in result]
	
	async def create(self, creds: UserRegisterSchema):
		'''create user'''

		user = User(
			name=creds.name,
			email=creds.email,
			password_hash=creds.password
		)
	
		self.db.add(user)
		await self.db.commit()
		await self.db.refresh(user)

		return user
	
	async def get_by_email(self, email: str):
		'''check if mail is busy'''

		query = await self.db.execute(
			select(User).where(User.email == email)
		)
		user = query.scalars().first()

		return user