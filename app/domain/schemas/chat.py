from pydantic import BaseModel


class CreateChatSchema(BaseModel):
	name: str
	member_uuids: list[str] | None


class ChatOut(BaseModel):
	id: int
	name: str | None
	is_group: bool

	class Config:
		from_attributes = True