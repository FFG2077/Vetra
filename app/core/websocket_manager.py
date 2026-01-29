from fastapi import WebSocket
from services.websocket_service import websocketService
from repositories.websocket_repo import WebSocketRepository


class ConnectionManager:
	def __init__(self):
		self.active_connections: dict[str, WebSocket] = {}

	async def connect(self, public_id: WebSocket, websocket: str) -> None:
		self.active_connections[public_id] = websocket

	async def disconnect(self, public_id: WebSocket) -> None:
		self.active_connections.pop(public_id, None)

	async def handshake(self, db, public_id: str, chat_id: int) -> bool:
		socket = self.active_connections.get(public_id)

		if socket:
			repo = WebSocketRepository(db)
			service = websocketService(repo)

			try:
				permissions = await service.handshake(public_id, chat_id)

				if permissions:
					return True
			except ValueError:
				return False
			
		return False

	async def send_personal_message(self, public_id: str, message: str) -> None:
		websocket = self.active_connections.get(public_id)
		if websocket:
			await websocket.send_text(message)


manager = ConnectionManager()