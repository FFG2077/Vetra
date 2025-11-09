from pydantic import BaseModel


class CreateChatSchema(BaseModel):
	name: str
	is_group: bool


class ChatOut(BaseModel):
	id: int
	name: str
	is_group: bool

	class Config:
		from_attributes = True