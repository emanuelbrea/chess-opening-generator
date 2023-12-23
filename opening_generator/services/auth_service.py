import logging

import jwt
from fastapi import HTTPException
from jwt import PyJWKClient, PyJWKClientError, DecodeError

from opening_generator.config import config_data


class AuthService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        region = config_data["AWS_REGION"]
        userpool_id = config_data["COGNITO_POOL_ID"]
        keys_url = (
            "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
                region, userpool_id
            )
        )
        self.jwks_client = PyJWKClient(keys_url)
        self.app_client_id = config_data["COGNITO_CLIENT_ID"]

    def get_user_claims(self, token: str):
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        except PyJWKClientError as err:
            raise HTTPException(status_code=401, detail="Invalid jwt") from err
        try:
            data = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.app_client_id,
                options={"verify_exp": False},
            )
        except DecodeError as err:
            raise HTTPException(status_code=401, detail="Invalid jwt") from err
        self.logger.debug("Received request from user %s", data.get("email"))
        return data
