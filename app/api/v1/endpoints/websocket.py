from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import User, get_db
from core.websocket_manager import manager
from core.auth import get_current_user_ws


router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user_ws)) -> None:
	'''WebSocket endpoint for real-time communication'''
	await websocket.accept()
	if not user:
		await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
		return

	public_id = user.public_id

	await manager.connect(websocket, public_id)

	try:
		while True:
			data = await websocket.receive_text()

			await manager.send_personal_message(public_id, f"Message text was: {data}")
	finally:
		await manager.disconnect(websocket, public_id)