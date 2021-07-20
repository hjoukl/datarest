from pydantic import create_model, Field
import sqlalchemy.types
from typing import List 
from . import database

# match data types in dictionary
dt_type_map = {
    sqlalchemy.types.TEXT: str,
    sqlalchemy.types.REAL: float,
    sqlalchemy.types.INTEGER: int,
    }

# Pydantic's orm_mode tells Pydantic model to read the data 
class _Config:
    orm_mode = True


def create_model_from_db(model_name, dbtable):
    attributes = {}
    table_cls = database.get_table_cls(dbtable)
    
    primary_key_list = []
    # iterate colmuns in dbtable + get column name and type
    for column in table_cls.__table__.columns:
        name = str(column.name)
        typ = dt_type_map[type(column.type)]
        attributes[name] = (
            typ, Field(description=name))
        # if columns has primary key --> append to  primary_key_list
        if column.primary_key:
            primary_key_list.append(name)
    model = create_model(model_name, **attributes, __config__=_Config)
    
    # TODO: Add support for composite keys
    # if primary_key_list has more than one item --> raise ValueError
    if len(primary_key_list) > 1:
        raise ValueError('Multi-column primary keys not yet supported')
    else:
        # set the only primary_key_list item as id_column
        id_column = primary_key_list[0]
    return (id_column, model)