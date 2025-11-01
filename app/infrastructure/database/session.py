from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings


engine = create_async_engine(
	settings.DATABASE_URL,
	future=True,  # for SQLAlchemy 2.0
)

AsyncSessionLocal = sessionmaker(
	class_=AsyncSession,
  autocommit=False,
  autoflush=False,
  bind=engine,
	expire_on_commit=False
)

async def get_db():
	async with AsyncSessionLocal() as session:
		yield session