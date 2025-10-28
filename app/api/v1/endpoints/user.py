from infrastructure.database import get_db, User
from fastapi import APIRouter, Depends
# from pydantic import BaseModel
from domain.schemas.user import UserOut
from sqlalchemy.orm import Session
from core.auth import get_current_user


router = APIRouter()

@router.get('/get_users', summary='Get all users')
async def get_users(db: Session=Depends(get_db)):
	return db.query(User).all()


@router.get('/get_me', summary='get current user', response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
	return user