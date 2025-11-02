from infrastructure.database import get_db, User
from fastapi import APIRouter, Depends
from domain.schemas.user import UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.auth import get_current_user

from repositories.user_repo import UserRepository


router = APIRouter()

@router.get('/get_users', summary='Get all users')
async def get_users(db: AsyncSession=Depends(get_db)):
	repo = UserRepository(db)
	users = await repo.get_users()
	# result = await db.execute(select(User))
	# users = result.scalars().all()
	return users


@router.get('/get_me', summary='get current user', response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
	return user