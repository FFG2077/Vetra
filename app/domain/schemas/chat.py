from pydantic import BaseModel


class CreateChatSchema(BaseModel):
	name: str
	member_uuids: list[str] | None


class ChatOut(BaseModel):
	public_id: str
	name: str | None
	is_group: bool

	class Config:
		from_attributes = True