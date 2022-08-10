"""Support for dynamic model creation.
"""

import collections
import json
import attrdict
from pydantic import create_model, Field
from typing import List 
from . import tableschema
from . import database_sqlalchemy


# adding configuration to model
#factory function for creating tuple subclasses with named fields
ModelCombo = collections.namedtuple(
    'ModelCombo',
    ['resource_name', 'resource_model', 'resource_collection_model', 'dbtable',
     'id_column'])



def create_pydantic_model(model_name, model_def):
    """Dynamically create pydantic model from config model definition.
    
    FastAPI uses pydantic models to describe endpoint input/output data.
    
    Parameters:
       model_name: resource name string
       model_def: model definition from config file (AttrDict)
    Returns: A ModelCombo object
    """
    # Create resource + collection model class names using standard Python conventions
    model_name_title = model_name.title()
    model_cls_name = '{}Model'.format(model_name_title)    
    collection_model_cls_name = '{}CollectionModel'.format(model_name_title)
    
    if model_def.profile == 'table-schema':
        id_column, model = tableschema.create_model_from_tableschema(
            model_cls_name, model_def.schema)
        collection_model = create_model(
            collection_model_cls_name, **{model_name: (List[model], ...)})
        return ModelCombo(
            resource_name=model_name,
            resource_model=model,
            resource_collection_model=collection_model,
            dbtable=model_def.dbtable,
            id_column=id_column)
        
    if model_def.profile == 'database-sqlalchemy':
        id_column, model = database_sqlalchemy.create_model_from_db(
            model_cls_name, model_def.dbtable)
        collection_model = create_model(
            collection_model_cls_name, **{model_name: (List[model], ...)})
        return ModelCombo(
            resource_name=model_name,
            resource_model=model,
            resource_collection_model=collection_model,
            dbtable=model_def.dbtable,
            id_column=id_column)


    raise ValueError('Unsupported data profile')


def create_pydantic_models(config):
    """Loop over config data resources to create pydantic models.
    
    Parameters:
        config: config dictionary (AttrDict)
        
    Returns: (model_name, model)-dictionary
    """
    models = {} 
    for model_name, model_def in config.datarest.data.items():
        
        # AttrDict.items() does not return AttrDict-wrapped dicts for values
        # that are dicts
        model_def = attrdict.AttrDict(model_def)
        models[model_name] = create_pydantic_model(model_name, model_def)
    return models
