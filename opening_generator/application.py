import logging

from fastapi import FastAPI
from uvicorn import run

from opening_generator.api.api_eco import eco_router
from opening_generator.api.api_position import position_router
from opening_generator.api.api_repertoire import repertoire_router
from opening_generator.api.api_user import user_router
from opening_generator.api.auth import auth_router
from opening_generator.db import init_db

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
)

init_db()

app.include_router(eco_router, prefix="/api")
app.include_router(repertoire_router, prefix="/api")
app.include_router(position_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(auth_router)

if __name__ == "__main__":
    run(app, host="127.0.0.1", port=8000)
