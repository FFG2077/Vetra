from sqlalchemy import and_, exists, func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import Chat, UserInChat, RoleEnum, User, Friendship, Message, FriendshipStatus
from domain.schemas.chat import ChatOut, CreateChatSchema


class ChatRepository:
	def __init__(self, session: AsyncSession):
		self.db = session

	async def friendship_exists(self, user_id, friend_id):
		'''Check if friendship exists between two users'''

		friendship_exists = select(
			exists().where(
				and_(
					Friendship.user_id == func.least(user_id, friend_id),
					Friendship.friend_id == func.greatest(user_id, friend_id),
					Friendship.status == FriendshipStatus.ACCEPTED
				)
			)
		)
		exists_result = (
			await self.db.execute(friendship_exists)
		).scalar()

		return exists_result
	
	async def chat_exists(self, user_id: int, friend_id: int):
		'''Check if a direct chat exists between two users'''
		query = await self.db.execute(
      select(exists().where(
          and_(
            Chat.is_group == False,
            Chat.id.in_(
              select(UserInChat.chat_id)
              .where(UserInChat.user_id == user_id)
              .intersect(
                select(UserInChat.chat_id)
                .where(UserInChat.user_id == friend_id)
              )
            )
          )
				)
			)
    )

		return query.scalar()

	async def create_direct_chat(self, public_id, friend_uuid: str):
		'''create a direct chat with a friend'''
		user_id = select(User.id).where(User.public_id == public_id).scalar_subquery()
		friend_id = select(User.id).where(User.public_id == friend_uuid).scalar_subquery()

		if not await self.friendship_exists(user_id, friend_id):
			raise ValueError("Friend not found or not accepted")
	
		if await self.chat_exists(user_id=user_id, friend_id=friend_id):
			raise ValueError("Direct chat already exists")

		chat = Chat(
			name=None,
			is_group=False
		)

		self.db.add(chat)
		await self.db.flush()

		members = [
			UserInChat(chat_id=chat.id, user_id=user_id, role=RoleEnum.ADMIN),
			UserInChat(chat_id=chat.id, user_id=friend_id, role=RoleEnum.ADMIN)
		]
		self.db.add_all(members)

		await self.db.commit()
		await self.db.refresh(chat)

		chat = ChatOut.model_validate(chat)

		return chat
	
	async def create_group_chat(self, user_uuid: int, chat_name: str, member_uuids: list[str]):
		'''Create a group chat'''
		user_id = select(User.id).where(User.public_id == user_uuid).scalar_subquery()

		chat = Chat(
			name=chat_name,
			is_group=True
		)

		self.db.add(chat)
		await self.db.flush()

		owner = UserInChat(chat_id=chat.id, user_id=user_id, role=RoleEnum.OWNER)

		for member_uuid in member_uuids:
			member_id = select(User.id).where(User.public_id == member_uuid).scalar_subquery()

			if not await self.friendship_exists(user_id, member_id):
				raise ValueError(f"Friend with uuid {member_uuid} not found or not accepted")
			member = UserInChat(chat_id=chat.id, user_id=member_id, role=RoleEnum.MEMBER)

			self.db.add_all([owner, member])

		await self.db.commit()
		await self.db.refresh(chat)

		return chat
	
	async def get_chat_history(self, chat_id: int, public_id: str):
		'''Get chat history'''
		user_id = select(User.id).where(User.public_id == public_id).scalar_subquery()

		user_in_chat_exists = select(
			exists().where(
				and_(
					UserInChat.user_id == user_id,
					UserInChat.chat_id == chat_id
				)
			)
		)

		user_in_chat_result = (
			await self.db.execute(user_in_chat_exists)
		).scalar()

		print(user_in_chat_result)

		if not user_in_chat_result:
			raise ValueError("Denied access to chat")

		query = await self.db.execute(
			select(Message)
			.join(UserInChat,
				and_(
					UserInChat.chat_id == Message.chat_id,
					UserInChat.user_id == user_id
				)
			)
			.where(Message.chat_id == chat_id)
		)

		result = query.scalars().all()

		return result


	# async def create_chat_with_friend(self, current_user: str, friend_uuid: str, chat_id: int, role: RoleEnum.MEMBER):
	# 	'''Add user in chat'''

	# 	current_user_id = select(User.id).where(User.public_id == current_user).scalar_subquery()
	# 	friend_id = select(User.id).where(User.public_id == friend_uuid).scalar_subquery()

	# 	friendship_exists = select(
	# 		exists().where(
	# 			and_(
	# 				Friendship.user_id == func.least(current_user_id, friend_id),
	# 				Friendship.friend_id == func.greatest(current_user_id, friend_id),
	# 				Friendship.status == 'accepted'
	# 			)
	# 		)
	# 	)
	# 	exists_result = (
	# 		await self.db.execute(friendship_exists)
	# 	).scalar()

	# 	if not exists_result:
	# 		raise ValueError("Friend not found or not accepted")
	# 	users_in_chat = [
	# 		UserInChat(
	# 			user_id=current_user_id,
	# 			chat_id=chat_id,
	# 			role=role
	# 		),
	# 		UserInChat(
	# 			user_id=friend_id,
	# 			chat_id=chat_id,
	# 			role=role
	# 		),
	# 	]
		
	# 	self.db.add_all(users_in_chat)
	# 	await self.db.commit()

	async def get_chats_by_user(self, public_id: int):
		'''Get chats by user uuid'''
		subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()

		chat_ids_query = (
      select(UserInChat.chat_id)
      .where(UserInChat.user_id == subquery)
    )

		query = await self.db.execute(
			select(Chat, User.name)
			.join(UserInChat, UserInChat.chat_id == Chat.id)
			.join(User, User.id == UserInChat.user_id)
			.where(Chat.id.in_(chat_ids_query),
				User.id != subquery)
		)

		result = query.all()

		chats = []

		for chat, friend_name in result:
			chats.append(ChatOut.model_validate({
				'public_id': chat.public_id,
				'name': chat.name if chat.is_group else friend_name,
				'is_group': chat.is_group
			}))

		return chats

	async def delete_chat(self, public_id, chat_id):
		'''Delete chat'''
		user_subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()

		user_in_chat_exists = select(
			exists().where(
				and_(
					UserInChat.user_id == user_subquery,
					UserInChat.chat_id == chat_id
				)
			)
		)

		user_in_chat_result = (
			await self.db.execute(user_in_chat_exists)
		).scalar()

		if not user_in_chat_result:
			raise ValueError("Denied access to chat")

		query = await self.db.execute(
			delete(Chat)
			.where(Chat.id == chat_id)
		)
		await self.db.commit()

	async def rename_chat(self, chat_id: int, new_name: str, public_id: str):
		'''Rename chat'''
		user_subquery = select(User.id).where(User.public_id == public_id).scalar_subquery()

		chat_subquery = select(UserInChat.chat_id).where(
			UserInChat.user_id == user_subquery
		).scalar_subquery()

		query = await self.db.execute(
			update(Chat)
			.where(
				Chat.id == chat_id,
				Chat.id.in_(chat_subquery)
			)
			.values(name=new_name)
		)
		if query.rowcount == 0:
			raise ValueError("Friend not found or not accepted")

		await self.db.commit()

	async def add_user_to_chat(self, user_uuid: str, friend_uuid: str, chat_id: int):
		'''Add user to chat'''
		user_subquery = select(User.id).where(User.public_id == user_uuid).scalar_subquery()
		friend_subquery = select(User.id).where(User.public_id == friend_uuid).scalar_subquery()

		if not await self.friendship_exists(user_subquery, friend_subquery):
			raise ValueError("Friend not found or not accepted")
		
		friend_in_chat_exists = select(
			exists().where(
				and_(
					UserInChat.user_id == friend_subquery,
					UserInChat.chat_id == chat_id
				)
			)
		)

		user_in_chat_exists = select(
			exists().where(
				and_(
					UserInChat.user_id == user_subquery,
					UserInChat.chat_id == chat_id
				)
			)
		)

		friend_in_chat_result = (
			await self.db.execute(friend_in_chat_exists)
		).scalar()

		user_in_chat_result = (
			await self.db.execute(user_in_chat_exists)
		).scalar()

		if friend_in_chat_result:
			raise ValueError("Friend is already in chat")

		if not user_in_chat_result:
			raise ValueError("Denied access to chat")

		user_in_chat = UserInChat(
			user_id=friend_subquery,
			chat_id=chat_id,
			role=RoleEnum.MEMBER
		)

		self.db.add(user_in_chat)
		await self.db.commit()