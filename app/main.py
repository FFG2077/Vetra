from fastapi import FastAPI
from api.v1 import api_router
from infrastructure.database import Base, engine


# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title='Seetalk')

# routes
app.include_router(api_router)