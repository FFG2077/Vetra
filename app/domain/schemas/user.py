from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
	public_id: str
	name: str
	email: str

	model_config = {
    "from_attributes": True
  }


class UserLoginSchema(BaseModel):
	email: EmailStr
	password: str


class UserRegisterSchema(BaseModel):
	name: str
	email: EmailStr
	password: str
