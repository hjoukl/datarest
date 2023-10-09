"""Support for dynamic model creation.
"""

import collections
from typing import List

from . import _cfgfile
from . import _sqlmodel_ext
from . import _data_resource_models


# TODO: Maybe get rid of ModelCombo namedtuple and switch to a full pydantic
# model here, too?
ModelCombo = collections.namedtuple(
    'ModelCombo',
    ['resource_name', 'resource_model', 'resource_collection_model', 'dbtable',
     'id_columns', 'expose_routes', 'query_params', 'paginate'])


def create_model(model_name, model_def):
    """Dynamically create SQLModel model (=pydantic + SQLAlchemy model) from
    config model definition.

    FastAPI uses pydantic models to describe endpoint input/output data.

    Parameters:
       model_name: resource name string
       model_def: model definition from config file

    Returns: A ModelCombo object
    """
    # Create resource + collection model class names using standard Python
    # naming conventions
    model_cls_name = model_name.title()
    collection_model_cls_name = f'{model_cls_name}CollectionModel'

    if model_def.schema_spec == _cfgfile.SchemaSpecEnum.data_resource:
        # TODO: Unify model creation code (parts are in _data_resource_models,
        # others in _sqlmodel_ext)
        id_columns, model = _data_resource_models.create_model(
            model_cls_name, model_def)
        # **kwargs entries used here are:
        #     model_name: (<type_annotation>, <default_value>)
        collection_model = _sqlmodel_ext.create_model(
            collection_model_cls_name, **{model_name: (List[model], ...)})
        return ModelCombo(
            resource_name=model_name,
            resource_model=model,
            resource_collection_model=collection_model,
            dbtable=model_def.dbtable,
            id_columns=id_columns,
            expose_routes=model_def.expose_routes,
            query_params=model_def.query_params,
            paginate=model_def.paginate)

    raise ValueError('Unsupported data schema specification')


def create_models(datatables: _cfgfile.Datatables):
    """Loop over config data resources to create pydantic models.

    Parameters:
        datatables: Datatables model

    Returns: (model_name, model)-dictionary
    """
    models = {}
    for model_name, model_def in datatables.items():
        models[model_name] = create_model(model_name, model_def)
    return models
