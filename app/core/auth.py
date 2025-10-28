from authx import AuthX, AuthXConfig
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from infrastructure.database import get_db, User
from .config import settings


config = AuthXConfig()

# Main settigs
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY

if settings.DEBUG:
  # dev
  config.JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24 * 365  # infinity token for dev
  config.JWT_REFRESH_TOKEN_EXPIRES = 3600 * 24 * 365 * 30  # infinity token for dev
else:
  # prod
  config.JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
  config.JWT_REFRESH_TOKEN_EXPIRES = 86400 * 30  # 30 days

# headers
config.JWT_TOKEN_LOCATION = ["headers"]
config.JWT_HEADER_NAME = "Authorization" 
config.JWT_HEADER_TYPE = "Bearer"

# Algoritm
config.JWT_ALGORITHM = "HS256"

security = AuthX(config=config)


async def get_current_user(
  token = Depends(security.access_token_required),
  db: Session = Depends(get_db)
) -> User:
  
  user_id = int(token.sub)
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(401, "User not found")
  return user