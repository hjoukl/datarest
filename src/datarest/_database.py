import os
import string

from sqlalchemy import create_engine
from sqlalchemy import orm

from ._app_config import config


connect_string = string.Template(
    config.datarest.database.connect_string
    ).substitute(os.environ)

# TODO: Make check more robust?
# Create connect string using pydantic, e.g. pydantic.PostgresDsn?
if connect_string.startswith('sqlite:'):
    # check_same_thread needed for sqlite only
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    connect_string, connect_args=connect_args)

Session = orm.Session
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


# dependency for fastapi app/router, yields the actual db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
       db.close()
