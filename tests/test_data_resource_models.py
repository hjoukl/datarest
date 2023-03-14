import pytest
import frictionless
from sqlmodel import select
from datarest._data_resource_models import create_model_from_tableschema
from sqlmodel.sql.sqltypes import AutoString


@pytest.fixture
def schema():

    data = [["id","name", "age", "income"],
        [1, "Patrick", 28, "3550.50"],
        [2, "Vivienne", 36, "2852.35"]]
    
    test_resource = frictionless.describe(data)
    test_resource.schema.primary_key.append("id")
    test_resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type':'uuid4_base64',
                    'id_src_fields': ['id']
                    }
    return test_resource.schema

#checkt that a model has been generated from a given schema
def test_create_model_from_tableschema(schema):
    (id_columns, model) = create_model_from_tableschema('TestModel', schema)
    breakpoint()
    # Check that id_columns tuple contains the expected values
    assert isinstance(id_columns, tuple)
    assert len(id_columns) == 1
    assert id_columns[0] == 'id'

    # Check that model has been correctly defined
    assert model.__tablename__ == 'testmodel'
    assert len(model.__table__.columns) == len(schema.fields)
    
    # Check that model columns have the expected names
    for i, field_def in enumerate(schema.fields):
        assert model.__table__.columns[i].name == field_def.name
    
    # Check that column types are correct
    assert model.__table__.columns[0].type.python_type == int
    assert isinstance(model.__table__.columns[1].type, AutoString) # SQLModel maps strings to AutoString-objects
    assert model.__table__.columns[2].type.python_type == int
    assert model.__table__.columns[3].type.python_type == float

    # add an instance to the model and check its properties
    robert = model(id=2, name="Robert", age=25, income="1600.35")
    assert robert.id == 2
    assert robert.name == "Robert"
    assert robert.age == 25
    assert robert.income == 1600.35


