from os import path
from dotenv import load_dotenv
import secrets

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config."""
    SECRET_KEY = secrets.token_hex()
    AWS_REGION = 'us-east-1'
    COGNITO_CLIENT_ID = '1rnu18aka8gk8k9hrjlttg40cs'
    COGNITO_POOL_ID = 'us-east-1_GFAp0SDxh'
    JSON_SORT_KEYS = False


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
