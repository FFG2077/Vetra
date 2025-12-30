from fastapi import APIRouter
from api.v1.endpoints import user, auth, chat, friendship, websocket


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix='/users', tags=['users'])
api_router.include_router(chat.router, prefix='/chat', tags=['chat'])
api_router.include_router(friendship.router, prefix='/friendship', tags=['friendship'])
api_router.include_router(websocket.router)