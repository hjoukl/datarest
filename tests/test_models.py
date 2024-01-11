import pytest
import frictionless
import yaml
import os
from datarest._cfgfile import TableschemaTable, ExposeRoutesEnum, SchemaSpecEnum, Datatables
from datarest._models import create_model, ModelCombo, create_models
from datarest._data_resource_models import create_model_from_tableschema

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

    try:
        model_combo = create_model("testmodel", model_def)

        # Check that the function returns a ModelCombo object
        assert isinstance(model_combo, ModelCombo)

        # Check that the ModelCombo object has the expected attributes
        assert model_combo.resource_name == "testmodel"
        assert model_combo.dbtable == "test_table"
        assert model_combo.id_columns[0] == "id"
        assert model_combo.expose_routes == [ExposeRoutesEnum.get_one]
        assert model_combo.query_params == []
        assert model_combo.paginate == 10

        # Check that the resource model has the expected attributes
        assert hasattr(model_combo.resource_model, "id")
        assert hasattr(model_combo.resource_model, "name")
        assert hasattr(model_combo.resource_model, "age")
        assert hasattr(model_combo.resource_model, "income")

    finally:
        os.remove("test.yaml")


def test_create_model_invalid_schema():
    with pytest.raises(AttributeError):
        model_def = TableschemaTable(
            dbtable='test_table',
            paginate=10,
            expose_routes=[ExposeRoutesEnum.get_one],
            query_params=[],
            schema_spec=SchemaSpecEnum.unknown,
            schema="test.yaml"
        )
        create_model("testmodel", model_def)


def test_create_model_multiple_inputs(model_def):

    model_def.paginate = 20
    model_def.query_params=["name", "age"]
    model_def.expose_routes = [ExposeRoutesEnum.create, ExposeRoutesEnum.update]

    try:
        model_combo = create_model("testmodel_1", model_def)

        # Check that the ModelCombo object has the expected attributes
        assert model_combo.resource_name == "testmodel_1"
        assert model_combo.dbtable == "test_table"
        assert model_combo.id_columns[0] == "id"
        assert model_combo.expose_routes == [ExposeRoutesEnum.create, ExposeRoutesEnum.update]
        assert model_combo.query_params == ["name", "age"]
        assert model_combo.paginate == 20

    finally:
        os.remove("test.yaml")


def test_create_models(model_def):
    
    try:
        datatables = Datatables(__root__={"test_datatable": model_def})

        models = create_models(datatables)
        
        # Check that the ModelCombo object has the expected attributes
        assert len(models) == 1
        assert models["test_datatable"].resource_name == "test_datatable"
        assert models["test_datatable"].dbtable == "test_table"
        assert models["test_datatable"].id_columns[0] == "id"
        assert models["test_datatable"].expose_routes == [ExposeRoutesEnum.get_one]
        assert models["test_datatable"].query_params == []
        assert models["test_datatable"].paginate == 10

        # Check that the resource model has the expected attributes
        assert hasattr(models["test_datatable"].resource_model, "id")
        assert hasattr(models["test_datatable"].resource_model, "name")
        assert hasattr(models["test_datatable"].resource_model, "age")
        assert hasattr(models["test_datatable"].resource_model, "income")

    finally:
        os.remove("test.yaml")
