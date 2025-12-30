from fastapi import WebSocket


class ConnectionManager:
	def __init__(self):
		self.active_connections: dict[str, WebSocket] = {}

	async def connect(self, websocket: WebSocket, public_id: str) -> None:
		await websocket.accept()
		self.active_connections[public_id] = websocket

	async def disconnect(self, websocket: WebSocket, public_id: str) -> None:
		self.active_connections.pop(public_id, None)

	async def send_personal_message(self, public_id: str, message: str) -> None:
		websocket = self.active_connections.get(public_id)
		if websocket:
			await websocket.send_text(message)


manager = ConnectionManager()