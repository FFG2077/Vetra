from datetime import timedelta

from authx import AuthX, AuthXConfig
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from infrastructure.database import User, get_db
from domain.schemas.user import UserOut

config = AuthXConfig()

# Main settigs
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY

if settings.DEBUG:
  # dev
  config.JWT_ACCESS_TOKEN_EXPIRES = None  # infinity token for dev
  config.JWT_REFRESH_TOKEN_EXPIRES = None  # infinity token for dev
else:
  # prod
  config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
  # 1 hour
  config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
  # 30 days

# headers
config.JWT_TOKEN_LOCATION = ["headers"]
config.JWT_HEADER_NAME = "Authorization" 
config.JWT_HEADER_TYPE = "Bearer"

# Algoritm
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)


async def get_current_user(
  token = Depends(security.access_token_required),
  db: AsyncSession = Depends(get_db)
) -> User:
  
  public_id = token.sub
  result = await db.execute(select(User).where(User.public_id == public_id))
  user = result.scalars().first()
  if not user:
    raise HTTPException(401, "User not found")
  return UserOut.model_validate(user)