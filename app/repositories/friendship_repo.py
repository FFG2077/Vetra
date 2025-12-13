from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.schemas.user import UserOut
from infrastructure.database import Friendship, User, FriendshipStatus


class FriendshipRepository:
	def __init__(self, session: AsyncSession):
		self.db = session

	async def get_friends(self, public_id: str):
		'''Get friends of current user'''
		query = await self.db.execute(
			select(User)
			.join(Friendship, User.id == Friendship.friend_id)
			.where(Friendship.status == FriendshipStatus.ACCEPTED)
		)

		result = query.scalars().all()
		
		return [UserOut.model_validate(u) for u in result]
	

	async def send_request(self, user_uuid: str, friend_uuid: str):
		'''Send friend request'''
		user_subquery = select(User.id).where(User.public_id == user_uuid).scalar_subquery()
		friend_subquery = select(User.id).where(User.public_id == friend_uuid).scalar_subquery()

		friendship = Friendship(
			user_id=func.least(user_subquery, friend_subquery),
			friend_id=func.greatest(user_subquery, friend_subquery),
			status=FriendshipStatus.PENDING
		)

		self.db.add(friendship)
		await self.db.commit()
		await self.db.refresh(friendship)

	async def accept_request(self, user_uuid: str, friend_uuid: str):
		'''Accept friend request'''
		user_subquery = select(User.id).where(User.public_id == user_uuid).scalar_subquery()
		friend_subquery = select(User.id).where(User.public_id == friend_uuid).scalar_subquery()

		query = await self.db.execute(
			update(Friendship)
			.where(
				Friendship.user_id == func.least(user_subquery, friend_subquery),
				Friendship.friend_id == func.greatest(user_subquery, friend_subquery),
				Friendship.status == FriendshipStatus.PENDING
			)
			.values(status=FriendshipStatus.ACCEPTED)
		)

		if query.rowcount == 0:
			raise ValueError("Friend request not found or already accepted")

		await self.db.commit()

	async def remove_friend(self, user_uuid: str, friend_uuid: str):
		'''Remove friend'''
		user_subquery = select(User.id).where(User.public_id == user_uuid).scalar_subquery()
		friend_subquery = select(User.id).where(User.public_id == friend_uuid).scalar_subquery()

		query = await self.db.execute(
			delete(Friendship)
			.where(
				Friendship.user_id == func.least(user_subquery, friend_subquery),
				Friendship.friend_id == func.greatest(user_subquery, friend_subquery),
				Friendship.status == FriendshipStatus.ACCEPTED
			)
		)

		if query.rowcount == 0:
			raise ValueError("Friend not found or not accepted")

		await self.db.commit()