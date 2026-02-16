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

	is_handshaked = False
	chat_id = None

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
			event = data.get("event")

			# Validate event
			if not event:
				await websocket.close(
          code=status.WS_1003_UNSUPPORTED_DATA,
          reason="Event required"
        )
        
				return

			# handshake check
			if not is_handshaked and event != 'message:handshake':
				await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Handshake required")

				return
			
			# Handle events

			# Handshake event
			elif event == 'message:handshake':
				chat_id = data['data']['chat_id']
				if not await manager.handshake(db, public_id, chat_id):
					await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Chat does not exist or permission denied")

					return

				is_handshaked = True

				await websocket.send_json({
          "event": "handshake:ok",
          "data": {"chat_id": chat_id}
        })

			# Send message event
			elif event == 'message:send':
				await manager.send_message(db, public_id, chat_id, data['data']['content'])
				
			# Unknown event
			else:
				await websocket.close(
					code=status.WS_1003_UNSUPPORTED_DATA,
					reason="Unknown event"
				)
				return
			
	finally:
		await manager.disconnect(websocket, public_id)