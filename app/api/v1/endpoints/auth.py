from core.auth import security
from core.security import hash_password, verify_password
from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal, get_db, User
from pydantic import BaseModel, EmailStr


router = APIRouter()

class UserLoginSchema(BaseModel):
	email: EmailStr
	password: str


class UserRegisterSchema(BaseModel):
	name: str
	email: EmailStr
	password: str


@router.post('/login')
def login(creds: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
	user = db.query(User).filter(
		User.email == creds.email
	).first()

	# find user
	if not user:
		raise HTTPException(status_code=401, detail='Incorrect username or password')
	
	# verify password
	if not verify_password(creds.password, user.password_hash):
		raise HTTPException(status_code=401, detail='Incorrect username or password')
	
	# create token
	token = security.create_access_token(uid=str(user.id))
		
	return {'access_token': token, "token_type": "bearer",}


@router.post('/registration', summary='registration')
def registration(creds: UserRegisterSchema, response: Response, db: Session = Depends(get_db)):
	# check if mail is busy
	if db.query(User).filter(User.email == creds.email).first():
		raise HTTPException(status_code=400, detail='Email already exists')
	
	# create user
	user = User(
		name=creds.name,
		email=creds.email,
		password_hash=hash_password(creds.password)
	)
	
	db.add(user)
	db.commit()
	db.refresh(user)

	token = security.create_access_token(uid=str(user.id))
	
	return {
		'access_token': token,
		"user": {
      "id": user.id,
      "name": user.name,
      "email": user.email
    }
	}