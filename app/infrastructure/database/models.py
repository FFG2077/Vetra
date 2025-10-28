from datetime import datetime
from typing import Annotated
from sqlalchemy import ForeignKey, DateTime, String, Text, Enum as SQLEnum
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
  )]


class User(Base):
	__tablename__ = 'users'

	id: Mapped[intpk]
	name: Mapped[str] = mapped_column(String(50))  # unique=True
	created_at: Mapped[created_at]
	email: Mapped[str] = mapped_column(String(255), unique=True)
	password_hash: Mapped[str] = mapped_column(String(255))

	# Relationships
	chats: Mapped[list['UserInChat']] = relationship()


class Message(Base):
	__tablename__ = 'messages'

	id: Mapped[intpk]
	chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'))
	user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
	content: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[created_at]
	updated_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    onupdate=func.now(),
    default=None
  )


class Chat(Base):
	__tablename__ = 'chats'

	id: Mapped[intpk]
	name: Mapped[str] = mapped_column(String(50))
	is_group: Mapped[bool] = mapped_column(default=False)

	# Relationships
	messages: Mapped[list['Message']] = relationship()
	members: Mapped[list['UserInChat']] = relationship()


class RoleEnum(str, Enum):
  OWNER = "owner"
  ADMIN = "admin"
  MEMBER = "member"


class UserInChat(Base):
	__tablename__ = 'user_in_chat'

	# id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(
		ForeignKey('users.id', ondelete='CASCADE'),
		primary_key=True,
	)
	chat_id: Mapped[int] = mapped_column(
		ForeignKey('chats.id', ondelete='CASCADE'),
		primary_key=True,
	)
	role: Mapped[str] = mapped_column(
    SQLEnum(RoleEnum, native_enum=False, length=20),
    default=RoleEnum.MEMBER
  )
	# role: Mapped[int] = mapped_column(primary_key=True)  # нажна ли доп таблица?


# class PasswordHash(Base): подумать!
# 	__tablename__ = 'password_hash'
	
# 	id: Mapped[int] = mapped_column(primary_key=True)
# 	password_hash: Mapped[str] = mapped_column(String(255))


# class Role(Base):
# 	__tablename__ = 'role'

# 	id: Mapped[int] = mapped_column(primary_key=True)
# 	name: Mapped[str] = mapped_column(String(20))