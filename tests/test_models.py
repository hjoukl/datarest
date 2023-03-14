import pytest
from datarest._models import create_model, ModelCombo

def test_create_model_data_resource():
    model_name = "test_model"
    model_def = {
        "schema_spec": "data_resource",
        "dbtable": "test_table",
        "expose_routes": True,
        "query_params": ["param1", "param2"],
        "paginate": True,
        "fields": {
            "field1": {"type": "int"},
            "field2": {"type": "str"}
        }
    }

    model_combo = create_model(model_name, model_def)

    assert isinstance(model_combo, ModelCombo)
    assert model_combo.resource_name == model_name
    assert model_combo.dbtable == "test_table"
    assert model_combo.expose_routes is True
    assert model_combo.query_params == ["param1", "param2"]
    assert model_combo.paginate is True

def test_create_model_invalid_schema_spec():
    model_name = "test_model"
    model_def = {
        "schema_spec": "invalid_spec",
        "dbtable": "test_table",
        "expose_routes": True,
        "query_params": ["param1", "param2"],
        "paginate": True,
        "fields": {
            "field1": {"type": "int"},
            "field2": {"type": "str"}
        }
    }

    with pytest.raises(ValueError):
        create_model(model_name, model_def)
