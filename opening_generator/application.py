import logging

from fastapi import FastAPI
from mangum import Mangum
from uvicorn import run

from opening_generator.api.api_eco import eco_router
from opening_generator.api.api_position import position_router
from opening_generator.api.api_repertoire import repertoire_router
from opening_generator.api.api_user import user_router
from opening_generator.api.auth import auth_router

logging.getLogger().setLevel('INFO')
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(asctime)s - %(message)s",
)

app = FastAPI(title="Opening Generator", root_path="/api")
app.include_router(eco_router)
app.include_router(repertoire_router)
app.include_router(position_router)
app.include_router(user_router)
app.include_router(auth_router)
handler = Mangum(app)

if __name__ == "__main__":
    run(app, host="127.0.0.1", port=8000)
