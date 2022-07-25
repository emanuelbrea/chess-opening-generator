from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

if 'RDS_HOSTNAME' in environ:
    engine = create_engine(
        f'postgresql://{environ["RDS_USERNAME"]}:{environ["RDS_PASSWORD"]}@{environ["RDS_HOSTNAME"]}:{environ["RDS_PORT"]}/{environ["RDS_DB_NAME"]}')
else:
    engine = create_engine(environ.get('DATABASE_URL'))

db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
