import logging

import jwt
from jwt import PyJWKClient

from config import Config


class AuthService:

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        region = config.AWS_REGION
        userpool_id = config.COGNITO_POOL_ID
        keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
        self.jwks_client = PyJWKClient(keys_url)
        self.app_client_id = config.COGNITO_CLIENT_ID

    def get_user_claims(self, token):
        token = token.replace("Bearer ", "")
        self.logger.info(token)
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        self.logger.info(signing_key)
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            audience=self.app_client_id,
            options={"verify_exp": False},
        )
        return data


auth_service = AuthService(Config)
