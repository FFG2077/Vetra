from fastapi import WebSocket
from services.websocket_service import WebsocketService
from repositories.websocket_repo import WebSocketRepository


class ConnectionManager:
	def __init__(self):
		self.active_connections: dict[str, WebSocket] = {}
		self.user_chats: dict[str, set[str]] = {}

	async def connect(self, public_id: str, websocket: WebSocket) -> None:
		"""Connect user"""
		self.active_connections[public_id] = websocket
		self.user_chats[public_id] = set()

	async def disconnect(self, public_id: str) -> None:
		"""Disconnect user"""
		self.active_connections.pop(public_id, None)
		self.user_chats.pop(public_id, None)

	async def handshake(self, db, public_id: str, chat_uuid: str) -> bool:
		"""Join chat"""
		repo = WebSocketRepository(db)
		service = WebsocketService(repo)

		try:
			if await service.handshake(public_id, chat_uuid):
				if public_id not in self.user_chats:
					self.user_chats[public_id] = set()
				
				self.user_chats[public_id].add(chat_uuid)
				return True
		except ValueError:
			return False
		return False

	async def send_message(self, db, public_id: str, user_name: str, chat_uuid: str, content: str) -> None :
		"""Create message and broadcast to all chat members"""
		repo = WebSocketRepository(db)
		service = WebsocketService(repo)

		try:
			# Create message in database
			message = await service.create_message(public_id, chat_uuid, content)

			# get all chat members to broadcast message and notifications
			member_public_ids = await repo.get_chat_members(chat_uuid)

			# broadcast (message and notifications)
			await self.broadcast_message_and_notifications(
				chat_uuid=chat_uuid,
				member_public_ids=member_public_ids,
				message=message,
				sender_public_id=public_id,
				sender_name=user_name
				)
		except ValueError as e:
			raise ValueError(str(e))

	async def broadcast_message_and_notifications(self, chat_uuid: str, member_public_ids: list[str], message: dict, sender_public_id: str, sender_name: str) -> None:
		"""Send message to all online members in this chat"""
		for public_id in member_public_ids:
			print(public_id)
			if public_id == sender_public_id:
				continue

			websocket = self.active_connections.get(public_id)

			print('error!')

			if websocket is None:
				continue

			# Only send message to users who are in the chat (handshaked)
			if (public_id in self.user_chats
					and chat_uuid in self.user_chats[public_id]):
				
				print('error!')
				try:
					await websocket.send_json({
						"event": "message.new",
						"data": {
							"chat_uuid": chat_uuid,
							"sender_id": sender_public_id,
							"sender_name": sender_name,
							"content": message.content
						}
					})
				except Exception:
					await self.disconnect(public_id)
			
			# send notification to users who are not in the chat (not handshaked), but online
			else:
				try:
					await websocket.send_json({
						"event": "notification.new_message",
						"data": {
							"chat_uuid": chat_uuid,
							"unread_count": None, # TODO: calculate unread count
							"last_message": {
								"sender_id": sender_public_id,
                "sender_name": sender_name,
                "content": message.content[:50]
							}
						}
					})
				except Exception:
					await self.disconnect(public_id)


manager = ConnectionManager()