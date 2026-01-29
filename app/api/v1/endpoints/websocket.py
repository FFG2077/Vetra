from fastapi import APIRouter, Depends, WebSocket, status
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

	await manager.connect(public_id, websocket)

	try:
		while True:
			'''
			{
			'event': 'message:send/delete/edit/handshake',
			'data': {
				'message_id': '', // for delete/edit
				'chat_id': '',   // for handshake/send
				'content': '',  // for send/edit
			}
			'''
			data = await websocket.receive_json()

			if data['event'] == 'message:handshake':
				if not await manager.handshake(db, public_id, data['data']['chat_id']):
					await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Chat does not exist or permission denied")
					return
			
	finally:
		await manager.disconnect(websocket, public_id)