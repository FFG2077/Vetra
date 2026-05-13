from repositories.websocket_repo import WebSocketRepository


class WebsocketService:
	def __init__(self, repo: WebSocketRepository):
		self.repo = repo

	async def handshake(self, public_id: str, chat_uuid: str) -> bool | ValueError:
		'''Perform handshake operations for WebSocket connection'''
		
		return await self.repo.handshake(public_id=public_id, chat_uuid=chat_uuid)
		
	async def create_message(self, public_id: str, chat_uuid: str, content: str):
		'''Create and store a new message'''
		return await self.repo.create_message(public_id=public_id, chat_uuid=chat_uuid, content=content)