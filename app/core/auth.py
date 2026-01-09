from datetime import timedelta

from authx import AuthX, AuthXConfig
from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

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


async def get_current_user_ws(
  websocket: WebSocket,
  db: AsyncSession = Depends(get_db)
) -> User | None:
  auth_header = websocket.headers.get("authorization")

  if not auth_header:
    # await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return None
  
  scheme, _, token = auth_header.partition(" ")
  print(scheme, token)
  if scheme.lower() != "bearer" or not token:
    # await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing token")
    return None
  
  try:
    public_id = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]).get("sub")
  except JWTError:
    return None

  result = await db.execute(select(User).where(User.public_id == public_id))
  user = result.scalars().first()
  
  if not user:
    raise None
  
  return UserOut.model_validate(user)