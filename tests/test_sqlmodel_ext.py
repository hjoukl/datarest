# Adapted from SQLModel PR:
# https://github.com/tiangolo/sqlmodel/pull/43/files#diff-d47aa94b4399636b3bf61c282806410ca16c47e6edb13a2d3ba675f9460e7389
# Tests: https://github.com/watkinsm/sqlmodel/blob/0b2a7962092a1593d22787b58b2bf2501b0c1b93/tests/test_create_model.py#L6
#
# (Copyright Michael Watkins (https://github.com/watkinsm),
#  License: MIT (https://github.com/tiangolo/sqlmodel/blob/main/LICENSE))

import pytest
import frictionless

from typing import Optional, List

from datarest._cfgfile import TableschemaTable, ExposeRoutesEnum, SchemaSpecEnum
from datarest._sqlmodel_ext import create_model, ConfigError, Type
from datarest._data_resource_models import create_model as c_m


@pytest.fixture
def model_def():

    data = [["id","name", "age", "income"],
        [1, "Patrick", 28, "3550.50"],
        [2, "Vivienne", 36, "2852.35"]]
    
    test_resource = frictionless.describe(data)
    test_resource.schema.primary_key.append("id")
    test_resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type':'uuid4_base64',
                    'id_src_fields': ['id']
                    }
    
    test_resource.to_yaml("test.yaml")

    model_def = TableschemaTable(
        dbtable='test_table',
        paginate=10,
        expose_routes=[ExposeRoutesEnum.get_one],
        query_params=[],
        schema_spec=SchemaSpecEnum.data_resource,
        schema="test.yaml"
    )
    return model_def

def test_create_model(model_def):
    
    model_name = "test_model"
    collection_model_name = "collection_test_model"

    id_columns, model = c_m(
            model_name, model_def)

    test_collection_model = create_model(model_name, **{model_name: (List[model], ...)})
    

    # check if list of models was created

    assert test_collection_model.__fields__["test_model"].name == 'test_model'
    assert test_collection_model.__fields__["test_model"].type_ == List[model].__args__[0]

    # assertions if model_collection was created with input data
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].__contains__('id') == True
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].__contains__('name') == True
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].__contains__('age') == True
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].__contains__('income') == True
    
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('id').name == 'id'
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('id').type_ == int
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('id').required == True

    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('name').name == 'name'
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('name').type_ == str

    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('age').name == 'age'
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('age').type_ == int

    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('income').name == 'income'
    assert test_collection_model.__fields__["test_model"].type_.__dict__['__fields__'].get('income').type_ == float

# check for fields with an underscore
def test_create_model_invalid_fields():
    with pytest.raises(ValueError):
        create_model("InvalidModel", **{"_invalid_field": str})


def test_create_model_invalid_():
    create_model("_InvalidModel", **{"invalid_field": (int, 42)})


"""
@pytest.fixture()
def clear_sqlmodel():
    # Clear the tables in the metadata for the default base model
    SQLModel.metadata.clear()
    # Clear the Models associated with the registry, to avoid warnings
    default_registry.dispose()
    yield
    SQLModel.metadata.clear()
    default_registry.dispose()

"""

"""
def test_create_model(clear_sqlmodel):
    
    Test dynamic model creation, query, and deletion
    
    field_definitions = {
        "id": (Optional[int], Field(default=None, primary_key=True)),
        "name": str,
        "secret_name": (str,),  # test 1-tuple
        "age": (Optional[int], None),
    }

    hero = create_model(
        "Hero", 
        **field_definitions, table=True
    )

    hero_1 = hero(**{"name": "Deadpond", "secret_name": "Dive Wilson"}), breakpoint()

    engine = create_engine("sqlite://")

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(hero_1)
        session.commit()
        session.refresh(hero_1)

    with Session(engine) as session:
        query_hero = session.query(hero).first()
        assert query_hero
        assert query_hero.id == hero_1.id
        assert query_hero.name == hero_1.name
        assert query_hero.secret_name == hero_1.secret_name
        assert query_hero.age == hero_1.age

    with Session(engine) as session:
        session.delete(hero_1)
        session.commit()

    with Session(engine) as session:
        query_hero = session.query(hero).first()
        assert not query_hero

"""
