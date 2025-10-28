from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
	# Project
	APP_NAME: str = 'SeeTalk'

	# DataBase
	DATABASE_URL: str

	# AuthX
	JWT_SECRET_KEY: str

	# For debug
	DEBUG: bool


	class Config:
		env_file = '.env'
		case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
  return Settings()

settings = get_settings()
