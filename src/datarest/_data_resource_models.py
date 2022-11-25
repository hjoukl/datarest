import json
from typing import List 

import frictionless
from sqlmodel import Field

import _sqlmodel_ext
import _resource_ids


tableschema_type_map = {
    'string': str,
    'number': float,
    'integer': int,
    'complex': complex,
    'boolean': bool
    }


def create_model(model_name, model_def):
    resource = frictionless.Resource(model_def.schema_)
    (id_columns, model) = create_model_from_tableschema(
        model_name, schema=resource['schema'])
    return (id_columns, model)


def create_model_from_tableschema(model_name, schema):
    id_columns = schema['primaryKey']
    # The tableschema spec allows for both a list or a string for the
    # primaryKey attribute, we make it a tuple.
    if isinstance(id_columns, str):
        id_columns = (id_columns,)
    else:
        id_columns = tuple(id_columns)

    id_default_func = _resource_ids.create_id_default(
        id_type=schema['x_datarest_primary_key_info']['id_type'],
        primary_key=tuple(
            schema['x_datarest_primary_key_info']['id_src_fields']),
        )

    attributes = {}
    for field_def in schema['fields']:
        name = field_def['name']
        typ = tableschema_type_map[field_def['type']]
        # optional
        primary_key = True if name in id_columns else False
        description = field_def.get('description')
        example = field_def.get('example')
        sa_column_kwargs = {}
        if primary_key and id_default_func is not None:
            sa_column_kwargs['default'] = id_default_func
        attributes[name] = (
            typ, 
            Field(description=description,
                  primary_key=primary_key,
                  schema_extra={'example': example},
                  sa_column_kwargs=sa_column_kwargs)
            )
    model = _sqlmodel_ext.create_model(
        model_name, __cls_kwargs__={'table': True},  **attributes)
    return (id_columns, model)
