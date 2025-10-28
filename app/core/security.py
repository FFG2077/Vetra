from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

def hash_password(password: str) -> str:
	'''Hash a password'''
	return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
	'''Verify password'''
	return pwd_context.verify(password, hashed_password)