from typing import Optional

import frictionless
from sqlmodel import Field

from . import _sqlmodel_ext
from . import _resource_ids


# Map tableschema type names to Python types.
tableschema_type_map = {
    'date': str,
    'string': str,
    'number': float,
    'integer': int,
    'complex': complex,
    'boolean': bool
}


def create_model(model_name, model_def):
    """Create model `model_name` from given model_def config.

    Reads the frictionless tableschema schema file specified in
    model_def.schema_ (trailing underscore due to pydantic reserve name).

    Returns:
        (id_columns: tuple[str], model: SQLModel) tuple
    """
    # Use safe Resource.from_descriptor API, see
    # https://github.com/frictionlessdata/frictionless-py/issues/1514#issuecomment-1598732059
    resource = frictionless.Resource.from_descriptor(model_def.schema_)
    (id_columns, model) = create_model_from_tableschema(
        model_name, schema=resource.schema)
    return (id_columns, model)


def create_model_from_tableschema(model_name, schema):
    """Create model `model_name` from given tableschema `schema`.

    Returns:
        SQLModel object (=both pydantic and SQLAlchemy model).
    """
    id_columns = schema.primary_key
    # The tableschema spec allows for both a list or a string for the
    # primaryKey attribute, we make it a tuple.
    if isinstance(id_columns, str):
        id_columns = (id_columns,)
    else:
        id_columns = tuple(id_columns)

    id_default_func = _resource_ids.create_id_default(
        id_type=schema.custom['x_datarest_primary_key_info']['id_type'],
        primary_key=tuple(
            schema.custom['x_datarest_primary_key_info']['id_src_fields']),
    )

    attributes = {}
    for field_def in schema.fields:
        name = field_def.name
        # Map the tableschema type names to Python types.
        typ = tableschema_type_map[field_def.type]
        # Determine if this field is part of the primary key.
        primary_key = True if name in id_columns else False
        # SQLModel uses Optional type annotations for nullability.
        if not field_def.required and not primary_key:
            # Make this field optional.
            typ = Optional[typ]
        description = field_def.description
        example = field_def.example
        # SQLAlchemy column keyword args.
        sa_column_kwargs = {}
        if primary_key and id_default_func is not None:
            # Hook in a default id creation function for SQLAlchemy.
            sa_column_kwargs['default'] = id_default_func
        attributes[name] = (
            # Python type/annotation for field.
            typ,
            # SQLModel field definition.
            Field(description=description,
                  primary_key=primary_key,
                  schema_extra={'example': example},
                  sa_column_kwargs=sa_column_kwargs)
            )
    # Create the SQLModel (=pydantic + SQLAlchemy) for the given tableschema
    # fields schema.
    model = _sqlmodel_ext.create_model(
        model_name, __cls_kwargs__={'table': True},  **attributes)
    return (id_columns, model)
