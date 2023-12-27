from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pycognito import Cognito
from pycognito.exceptions import WarrantException

from opening_generator.config import config_data

auth_router = APIRouter(tags=["Auth"])
COGNITO_POOL_ID = config_data["COGNITO_POOL_ID"]
COGNITO_CLIENT_ID = config_data["COGNITO_CLIENT_ID"]


@auth_router.post("/token", status_code=200)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
                           ):
    user = Cognito(COGNITO_POOL_ID, COGNITO_CLIENT_ID,
                   username=form_data.username)
    try:
        user.authenticate(password=form_data.password)
    except WarrantException:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.id_token, "token_type": "bearer"}
