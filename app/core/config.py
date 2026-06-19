from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
	# Project
	APP_NAME: str = 'Vetra'

	# DataBase
	DATABASE_URL: str
	MYSQL_ROOT_PASSWORD: str
	MYSQL_DATABASE: str
	MYSQL_USER: str
	MYSQL_PASSWORD: str
	# AuthX
	JWT_SECRET_KEY: str

	# For debug
	DEBUG: bool

	model_config = SettingsConfigDict(env_file=env_path, case_sensitive=True)
	# class Config:
	# 	env_file = '.env'
	# 	case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
  return Settings()

settings = get_settings()
