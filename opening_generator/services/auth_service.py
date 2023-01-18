import logging

import jwt
from flask import request, current_app as app
from jwt import PyJWKClient, PyJWKClientError, DecodeError

from config import Config
from opening_generator.exceptions import InvalidRequestException


class AuthService:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        region = config.AWS_REGION
        userpool_id = config.COGNITO_POOL_ID
        keys_url = (
            "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
                region, userpool_id
            )
        )
        self.jwks_client = PyJWKClient(keys_url)
        self.app_client_id = config.COGNITO_CLIENT_ID

    def get_user_claims(self):
        token = self.get_token()
        if not token:
            return None
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        except PyJWKClientError as err:
            raise InvalidRequestException("Invalid jwt") from err
        try:
            data = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.app_client_id,
                options={"verify_exp": False},
            )
        except DecodeError as err:
            raise InvalidRequestException("Invalid jwt") from err
        self.logger.debug("Received request from user %s", data.get("email"))
        return data

    def get_token(self):
        header = request.headers.get("Authorization")
        if not header:
            if not app.config['DEBUG']:
                raise InvalidRequestException("Missing authorization header")
            return None
        if "Bearer " not in header:
            raise InvalidRequestException("Invalid authorization header")
        token = header.replace("Bearer ", "")
        return token


auth_service = AuthService(Config)
