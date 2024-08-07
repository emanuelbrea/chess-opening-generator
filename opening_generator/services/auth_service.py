import json
import logging
import os

import jwt
from fastapi import HTTPException
from jwt import PyJWKClientError, DecodeError
from jwt.algorithms import RSAAlgorithm

from opening_generator import config_data


class AuthService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app_client_id = config_data["COGNITO_CLIENT_ID"]

        keys_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'jwks.json')
        with open(keys_path, "r") as f:
            self.jwks = json.load(f)

    def get_signing_key(self, kid):
        for key in self.jwks["keys"]:
            if key["kid"] == kid:
                return key
        raise HTTPException(status_code=401, detail="Invalid jwt")

    def get_user_claims(self, token: str):
        try:
            unverified_header = jwt.get_unverified_header(token)
            signing_key = self.get_signing_key(unverified_header["kid"])
            public_key = RSAAlgorithm.from_jwk(json.dumps(signing_key))
        except PyJWKClientError as err:
            raise HTTPException(status_code=401, detail="Invalid jwt") from err
        try:
            data = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.app_client_id,
                options={"verify_exp": False},
            )
        except DecodeError as err:
            raise HTTPException(status_code=401, detail="Invalid jwt") from err
        self.logger.debug("Received request from user %s", data.get("email"))
        return data
