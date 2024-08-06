from os import path
from dotenv import load_dotenv
import secrets

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config."""
    SECRET_KEY = secrets.token_hex()
    AWS_REGION = 'us-east-1'
    COGNITO_CLIENT_ID = 'REPLACE'
    COGNITO_POOL_ID = 'REPLACE'
    JSON_SORT_KEYS = False

