# sql dependecies
from sqlalchemy import create_engine
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy.ext.automap import automap_base
# config dependency
from .app_config import config


# use sqlalchemy's shiny reflection capabilities i.e. read generate ORM model
# from the database schema
Base = automap_base()
connect_string = config.datarest.database.connect_string
# check_same_thread needed for sqlite only
engine = create_engine(
    connect_string, connect_args={"check_same_thread": False})
# calling prepare() just sets up mapped classes and relationships.
Base.prepare(engine, reflect=True)

# session type
#Manages persistence operations for ORM-mapped objects.
Session = orm.Session
#The sessionmaker factory generates new session + reating them given the configurational arguments established here.
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


# dependency for fastapi app/router
#this instance is the actual database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
       db.close()



def get_table_cls(tablename):
    # object-level access to the data table
    return getattr(Base.classes, tablename)


