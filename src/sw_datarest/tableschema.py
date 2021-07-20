import json
from pydantic import create_model, Field
from typing import List 


#match data types in dictionary
tableschema_type_map = {
    'string': str,
    'number': float,
    'integer': int,
    'complex': complex,
    'boolean': bool
    }

# Pydantic's orm_mode tells Pydantic model to read the data 
class _Config:
    orm_mode = True



def create_model_from_tableschema(model_name, schema_location):
    schema_path = schema_location
    with open(schema_path, 'rb') as json_file:
        schema = json.load(json_file)

    # TODO: Add support for composite keys
    primary_key = schema['primaryKey']
    if isinstance(primary_key, list):
        raise ValueError('Multi-column primary keys not yet supported')
    else:
        id_column = primary_key

    attributes = {}
    for field_def in schema['fields']:
        name = field_def['name']
        typ = tableschema_type_map[field_def['type']]
        # optional
        description = field_def.get('description')
        example = field_def.get('x_datarest_example')
        attributes[name] = (
            typ, Field(description=description, example=example))
    model = create_model(model_name, **attributes, __config__=_Config)
    return (id_column, model)