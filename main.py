from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.url_shortener import router as url_shortener_router
from database import database

# function that setup and finish the process when "yield" finish
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(url_shortener_router)
