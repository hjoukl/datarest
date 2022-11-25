from sqlalchemy import create_engine
from sqlalchemy import orm

from _app_config import config


connect_string = config.datarest.database.connect_string
# check_same_thread needed for sqlite only
engine = create_engine(
    connect_string, connect_args={"check_same_thread": False})

Session = orm.Session
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


# dependency for fastapi app/router, yields the actual db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
       db.close()
