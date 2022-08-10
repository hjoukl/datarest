from typing import Dict, Tuple, Any, Type

from pydantic.errors import ConfigError
from sqlmodel import Field, SQLModel
from sqlmodel.main import SQLModelMetaclass


# Adapted from SQLModel PR:
# https://github.com/tiangolo/sqlmodel/pull/43/files#diff-d47aa94b4399636b3bf61c282806410ca16c47e6edb13a2d3ba675f9460e7389
# 
# (Copyright Michael Watkins (https://github.com/watkinsm),
#  License: MIT (https://github.com/tiangolo/sqlmodel/blob/main/LICENSE))

def create_model(
    model_name: str,
    *,
    __module__: str = __name__,
    __cls_kwargs__: Dict[str, Any] = None,
    **field_definitions,
) -> Type[SQLModelMetaclass]:
    """
    Dynamically create a model, similar to the Pydantic `create_model()` method
    :param model_name: name of the created model
    :param __module__: module of the created model
    :param __class_kwargs__: a dict for class creation, e.g. table=True
    :param field_definitions: fields of the model
    """
    __cls_kwargs__ = __cls_kwargs__ or {}
    fields = {}
    annotations = {}

    for f_name, f_def in field_definitions.items():
        if f_name.startswith("_"):
            raise ValueError("Field names may not start with an underscore")
        try:
            if isinstance(f_def, tuple) and len(f_def) > 1:
                f_annotation, f_value = f_def
            elif isinstance(f_def, tuple):
                f_annotation, f_value = f_def[0], Field(nullable=False)
            else:
                f_annotation, f_value = f_def, Field(nullable=False)
        except ValueError as e:
            raise ConfigError(
                "field_definitions values must be either a tuple of "
                "(<type_annotation>, <default_value>) or just a type "
                "annotation [or a 1-tuple of (<type_annotation>,)]"
            ) from e

        if f_annotation:
            annotations[f_name] = f_annotation
        fields[f_name] = f_value

    namespace = {
        "__annotations__": annotations, "__module__": __module__, **fields}
    return type(model_name, (SQLModel,), namespace, **__cls_kwargs__)
