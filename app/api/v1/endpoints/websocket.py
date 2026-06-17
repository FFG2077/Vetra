from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import User, get_db
from core.websocket_manager import manager
from core.auth import authenticate_ws


router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)) -> None:
	'''WebSocket endpoint for real-time communication'''
	await websocket.accept()

	data = await websocket.receive_json()
	if data.get("event") != "auth":
		await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication required")
		return
	user = await authenticate_ws(data['data'].get('token'), db)
	if not user:
		await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
		return
	await websocket.send_json({
		"event": "auth.ok",
	})

	public_id = user.public_id
	await manager.connect(public_id, websocket)

	handshaked_chats: set[str] = set()

	try:
		while True:
			'''
			{
			'event': 'auth/message.send/delete/edit/handshake',
			'data': {
				'token': '',  // for handshake/send/delete/edit
				'message_uuid': '', // for delete/edit
				'chat_uuid': '',   // for handshake/send
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
			if not handshaked_chats and event != 'message.handshake':
				await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Handshake required")

				return
			
			# Handle events

			# Handshake event
			elif event == 'message.handshake':
				chat_uuid = data['data']['chat_uuid']
				if not await manager.handshake(db, public_id, chat_uuid):
					await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Chat does not exist or permission denied")

					return

				handshaked_chats.add(chat_uuid)

				await websocket.send_json({
          "event": "handshake.ok",
          "data": {"chat_uuid": chat_uuid}
        })

			# Send message event
			elif event == 'message.send':
				chat_uuid = data['data']['chat_uuid']
				if chat_uuid not in handshaked_chats:
					await websocket.send_json({
						"event": "message.send.error",
						"data": {"error": "Handshake required"}
					})
					continue

				try:
					await manager.send_message(db, public_id, user.name, chat_uuid, data['data']['content'])

					await websocket.send_json({
						"event": "message.send.ok",
					})
				except Exception as e:
					await websocket.send_json({
						"event": "message.send.error",
						"data": {"error": str(e)}
					})
				
			# Unknown event
			else:
				await websocket.close(
					code=status.WS_1003_UNSUPPORTED_DATA,
					reason="Unknown event"
				)
				return 
	
	except WebSocketDisconnect:
		print("Client disconnected")

	finally:
		await manager.disconnect(public_id)