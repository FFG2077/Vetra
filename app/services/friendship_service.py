from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from repositories.friendship_repo import FriendshipRepository


class FriendshipService:
	def __init__(self, repo: FriendshipRepository):
		self.repo = repo
		
	async def get_friends(self, public_id: str):
		'''Get friends of current user'''
		try:
			friends = await self.repo.get_friends(public_id=public_id)
			return friends
		except IntegrityError:
			raise HTTPException(status_code=400, detail='Error fetching friends')
		
	async def send_request(self, user_uuid: str, friend_uuid: str):
		'''Send friend request'''
		try:
			await self.repo.send_request(user_uuid=user_uuid, friend_uuid=friend_uuid)
		except IntegrityError:
			raise HTTPException(status_code=400, detail='Error sending friend request')
		
	async def accept_request(self, user_uuid: str, friend_uuid: str):
		'''Accept friend request'''
		try:
			await self.repo.accept_request(user_uuid=user_uuid, friend_uuid=friend_uuid)
		except ValueError:
			raise HTTPException(status_code=400, detail='Error accepting friend request')
		
	async def remove_friend(self, user_uuid: str, friend_uuid: str):
		'''Remove friend'''
		try:
			await self.repo.remove_friend(user_uuid=user_uuid, friend_uuid=friend_uuid)
		except ValueError:
			raise HTTPException(status_code=400, detail='Error removing friend')
		
	async def cancel_request(self, user_uuid: str, friend_uuid: str):
		'''Cancel friend request'''
		try:
			await self.repo.cancel_request(user_uuid=user_uuid, friend_uuid=friend_uuid)
		except ValueError:
			raise HTTPException(status_code=400, detail='Error canceling friend request')
		
	async def list_friend_requests(self, user_uuid: str):
		'''List friend requests'''
		try:
			requests = await self.repo.list_friend_requests(user_uuid=user_uuid)
			return requests
		except IntegrityError:
			raise HTTPException(status_code=400, detail='Error listing friend requests')