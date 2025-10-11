from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
	# Project
	APP_NAME: str = 'SeeTalk'

	# DataBase
	DATABASE_URL: str

	class Config:
		env_file = 'app/.env'
		case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
  return Settings()

settings = get_settings()
