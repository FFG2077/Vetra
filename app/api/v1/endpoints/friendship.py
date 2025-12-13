from fastapi import APIRouter, Depends
from fastapi import status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user
from domain.schemas.user import UserOut
from infrastructure.database import User, get_db
from repositories.friendship_repo import FriendshipRepository
from services.friendship_service import FriendshipService


router = APIRouter()

@router.get('/get_friends', summary='Get friends of current user')
async def get_users(db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)) -> list[UserOut]:
	'''Get friends of current user'''
	repo = FriendshipRepository(db)
	friendship_service = FriendshipService(repo)

	friends = await friendship_service.get_friends(public_id=user.public_id)

	return friends


@router.post('/send_request', summary='Send friend request')
async def send_friend_request(friend_uuid: str, db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)):
	'''Send friend request'''
	repo = FriendshipRepository(db)
	friendship_service = FriendshipService(repo)
	
	await friendship_service.send_request(user_uuid=user.public_id, friend_uuid=friend_uuid)

	return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post('/accept_request', summary='Accept friend request')
async def accept_friend_request(friend_uuid: str, db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)):
	'''Accept friend request'''
	repo = FriendshipRepository(db)
	friendship_service = FriendshipService(repo)
	
	await friendship_service.accept_request(user_uuid=user.public_id, friend_uuid=friend_uuid)

	return Response(status_code=status.HTTP_204_NO_CONTENT)