from repositories.websocket_repo import WebSocketRepository


class websocketService:
	def __init__(self, repo: WebSocketRepository):
		self.repo = repo

	async def handshake(self, public_id: str, chat_id: int) -> bool | ValueError:
		'''Perform handshake operations for WebSocket connection'''
		try:

			if await self.repo.handshake(public_id=public_id, chat_id=chat_id):
				return True
		except ValueError:
			raise ValueError("Chat does not exist or permission denied")
		