from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import security
from domain.schemas.user import UserLoginSchema, UserRegisterSchema
from infrastructure.database import get_db
from repositories.user_repo import UserRepository
from services.user_service import UserService


router = APIRouter()

@router.post('/login')
async def login(creds: UserLoginSchema, db: AsyncSession = Depends(get_db)):
	repo = UserRepository(db)
	service = UserService(repo)
	user = await service.login_user(creds)
	
	# create token
	token = security.create_access_token(uid=str(user.id))
		
	return {'access_token': token, "token_type": "bearer",}


@router.post('/registration', summary='registration')
async def registration(creds: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
	repo = UserRepository(db)
	service = UserService(repo)
	user = await service.register_user(creds)

	token = security.create_access_token(uid=str(user.id))
	
	return {
		'access_token': token,
		"user": {
      "id": user.id,
      "name": user.name,
      "email": user.email
    }
	}