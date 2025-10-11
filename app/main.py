from fastapi import FastAPI
from server.api.v1.endpoints.users import router as users_router

app = FastAPI(title='Seetalk')

# routes
app.include_router(users_router)