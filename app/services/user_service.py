from repositories.user_repo import UserRepository
from domain.schemas.user import UserRegisterSchema, UserLoginSchema
from core.security import verify_password, hash_password
from fastapi import HTTPException


class UserService:
	def __init__(self, repo: UserRepository):
		self.repo = repo

	async def register_user(self, creds: UserRegisterSchema):
		'''register user'''

		user = await self.repo.get_by_email(creds.email)
		if user:
			raise HTTPException(status_code=400, detail='Email already exists')
		password_hash = hash_password(creds.password)

		new_creds = UserRegisterSchema(
			name=creds.name,
			email=creds.email,
			password=password_hash
		)
		
		return await self.repo.create(new_creds)
	
	async def login_user(self, creds: UserLoginSchema):
		'''login user'''

		user = await self.repo.get_by_email(creds.email)
		if not user:
			raise HTTPException(status_code=401, detail='Incorrect username or password')
		
		if not verify_password(creds.password, user.password_hash):
			raise HTTPException(status_code=401, detail='Incorrect username or password')
	
		return user
		
			

