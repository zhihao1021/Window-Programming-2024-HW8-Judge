from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from config import HOST, PORT
from routes import (
    auth_router,
    check_router,
    reset_router
)

app = FastAPI()
app.include_router(auth_router)
app.include_router(check_router)
app.include_router(reset_router)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def run_api():
    config = Config(
        app=app,
        host=HOST,
        port=PORT
    )
    server = Server(config=config)
    await server.serve()
