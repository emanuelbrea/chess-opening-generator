from os import environ

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

if "RDS_HOSTNAME" in environ:
    db_url = f'postgresql://{environ["RDS_USERNAME"]}:{environ["RDS_PASSWORD"]}@{environ["RDS_HOSTNAME"]}:{environ["RDS_PORT"]}/{environ["RDS_DB_NAME"]}'

else:
    db_url = environ.get("DATABASE_URL")

engine = create_engine(db_url, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
