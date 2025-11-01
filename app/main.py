from fastapi import FastAPI
from api.v1 import api_router
from infrastructure.database import Base, engine
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager


# create tables
@asynccontextmanager
async def lifespan(app: FastAPI):
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	yield


app = FastAPI(title='Seetalk', lifespan=lifespan)

# routes
app.include_router(api_router)


def custom_openapi():
	if app.openapi_schema:
		return app.openapi_schema
	
	openapi_schema = get_openapi(
		title="Seetalk API",
		version="1.0.0",
		routes=app.routes,
	)
	# add securityScheme
	openapi_schema["components"]["securitySchemes"] = {
    "bearerAuth": {
      "type": "http",
      "scheme": "bearer",
      "bearerFormat": "JWT",
    }
  }

	# apply to all endpoints by default
	for path in openapi_schema["paths"].values():
		for method in path.values():
			method["security"] = [{"bearerAuth": []}]

	app.openapi_schema = openapi_schema

	return app.openapi_schema


app.openapi = custom_openapi
