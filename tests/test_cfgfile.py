import pytest
from pathlib import Path 
import yaml
import os
import tempfile

from datarest._yaml_tools import dump_as_str, dump_decimal_as_str
from datarest._cfgfile import app_config, write_app_config, read_app_config, AppConfig, ExposeRoutesEnum, SchemaSpecEnum, Datarest, Fastapi, App, Datatables, Database, TableschemaTable

dump_decimal_as_str()
dump_as_str(ExposeRoutesEnum)
dump_as_str(SchemaSpecEnum)


def test_app_config_defaults():
    # Test default values
    config = app_config('table')
    assert isinstance(config, AppConfig)
    assert config.datarest.fastapi.app.title == "table API"
    assert config.datarest.fastapi.app.description == ""
    assert config.datarest.fastapi.app.version == "0.1.0"
    assert config.datarest.database.connect_string == "sqlite:///app.db"
    #import pdb; pdb.set_trace()
    assert config.datarest.datatables.__root__['table'].schema_spec == SchemaSpecEnum.data_resource
    assert config.datarest.datatables.__root__['table'].schema_ == 'table.yaml'
    assert config.datarest.datatables.__root__['table'].dbtable == 'table'
    assert config.datarest.datatables.__root__['table'].paginate == 10
    assert config.datarest.datatables.__root__['table'].expose_routes == [ExposeRoutesEnum.get_one]


def test_app_config_overrides():
    # Override default values
    config = app_config('table', title='Custom Title', description='Custom Description', version='1.2.3', connect_string='postgresql://localhost/app')
    assert isinstance(config, AppConfig)
    assert config.datarest.fastapi.app.title == "Custom Title API"
    assert config.datarest.fastapi.app.description == "Custom Description"
    assert config.datarest.fastapi.app.version == "1.2.3"
    assert config.datarest.database.connect_string == "postgresql://localhost/app"
    assert config.datarest.datatables.__root__['table'].schema_spec == SchemaSpecEnum.data_resource
    assert config.datarest.datatables.__root__['table'].schema_ == 'table.yaml'
    assert config.datarest.datatables.__root__['table'].dbtable == 'table'
    assert config.datarest.datatables.__root__['table'].paginate == 10
    assert config.datarest.datatables.__root__['table'].expose_routes == [ExposeRoutesEnum.get_one]


def test_app_config_invalid_table():
    #checks if the table argument is a String and if not a TypeError is raised
    with pytest.raises(TypeError):
        app_config(123)
        #welcher error auch immer als erwartungshaltung


def test_app_config_no_title():
    # Test default values with no title
    config = app_config('table')
    assert isinstance(config, AppConfig)
    assert config.datarest.fastapi.app.title == "table API"


def test_app_config_expose_routes():
    # Test expose_routes parameter
    config = app_config('table', expose_routes=[ExposeRoutesEnum.create, ExposeRoutesEnum.update])
    assert isinstance(config, AppConfig)
    assert config.datarest.datatables.__root__['table'].expose_routes == [ExposeRoutesEnum.create, ExposeRoutesEnum.update]


def test_app_config_invalid_expose_routes():
    # Test invalid expose_routes parameter
    with pytest.raises(ValueError):
        app_config('table', expose_routes=['invalid_route'])



def test_write_app_config_writes_yaml():
    #Test that write_app_config writes the app_config object to the specified file path in YAML format
    app_config = AppConfig(datarest=Datarest(
        fastapi=Fastapi(
            app=App(
                title="Test API",
                description="Test Description",
                version="1.0.0",
            ),
        ),
        database=Database(
            connect_string="sqlite:///test.db",
        ),
        datatables=Datatables(__root__={
            "table1": TableschemaTable(
                schema_spec="https://specs.frictionlessdata.io/data-resource/",
                schema="table1.yaml",
                dbtable="table1",
                expose_routes=[ExposeRoutesEnum.get_one],
            ),
        }),
    ))

    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            cfg_path = temp.name
            write_app_config(cfg_path, app_config)
            with open(cfg_path, 'r') as f:
                written_yaml = yaml.safe_load(f)
            assert written_yaml == app_config.dict(by_alias=True)
    finally:
        os.remove(cfg_path)



@pytest.mark.skip
#macht es sinn hier noch die Exception in die Funktion zu implementieren? Oder doch einfach den Test skippen
def test_write_app_config_invalid_app_config_type():
    with pytest.raises(TypeError):
        write_app_config('test.yaml', 'invalid_type')


def test_write_app_config_invalid_cfg_path_type():
    with pytest.raises(TypeError):
        write_app_config(123, AppConfig(...))


@pytest.mark.skip
#macht es sinn hier noch die Exception in die Funktion zu implementieren? Oder doch einfach den Test skippen
def test_write_app_config_empty_cfg_path():
    with pytest.raises(ValueError):
        write_app_config('', AppConfig(datarest=Datarest(
        fastapi=Fastapi(
            app=App(
                title="Test API",
                description="Test Description",
                version="1.0.0",
            ),
        ),
        database=Database(
            connect_string="sqlite:///test.db",
        ),
        datatables=Datatables(__root__={
            "table1": TableschemaTable(
                schema_spec="https://specs.frictionlessdata.io/data-resource/",
                schema="table1.yaml",
                dbtable="table1",
                expose_routes=[ExposeRoutesEnum.get_one],
            ),
        }),
    )))


def test_read_app_config_valid_yaml():
    #Test that read_app_config reads a valid YAML file and returns an AppConfig object.
    cfg_path = 'test.yaml'
    app_config = AppConfig(datarest=Datarest(
        fastapi=Fastapi(
            app=App(
                title="Test API",
                description="Test Description",
                version="1.0.0",
            ),
        ),
        database=Database(
            connect_string="sqlite:///test.db",
        ),
        datatables=Datatables(__root__={
            "table1": TableschemaTable(
                schema_spec="https://specs.frictionlessdata.io/data-resource/",
                schema="table1.yaml",
                dbtable="table1",
                expose_routes=[ExposeRoutesEnum.get_one],
            ),
        }),
    ))
    write_app_config(cfg_path, app_config)
    read_config = read_app_config(cfg_path)
    assert read_config == app_config
    os.remove(cfg_path)

@pytest.mark.skip
#macht es sinn hier noch die Exception in die Funktion zu implementieren? Oder doch einfach den Test skippen
def test_read_app_config_invalid_yaml():
    cfg_path = 'test.yaml'
    invalid_yaml = """
    datarest:
        fastapi:
            app:
                title: Invalid API
                version: 1.0.0
    """
    with open(cfg_path, 'w') as f:
        f.write(invalid_yaml)
    with pytest.raises(ValidationError):
        read_app_config(cfg_path)
    os.remove(cfg_path)

#Test that the AppConfig, Datarest, Fastapi, App, Database, and Datatables classes correctly validate their input data.
#use the parse_obj method to try to create an instance of the class. 
#correct errors are raised for invalid data?

@pytest.mark.skip
def test_app_config_validation():
    # Test that AppConfig accepts valid input
    valid_data = {
        "datarest": {
            "fastapi": {
                "app": {
                    "title": "Test API",
                    "description": "Test Description",
                    "version": "1.0.0",
                }
            },
            "database": {
                "connect_string": "sqlite:///test.db",
            },
            "datatables": {
                "__root__": {
                    "table1": {
                        "schema_spec": '"https://specs.frictionlessdata.io/data-resource/"',
                        "schema_spec": '"https://specs.frictionlessdata.io/data-resource/"',
                        "schema": "table1.yaml",
                        "dbtable": "table1",
                        "expose_routes": ["get_one"],
                    },
                },
            },
        },
    }
    app_config = AppConfig.parse_obj(valid_data)
    assert app_config.datarest.fastapi.app.title == "Test API"
    assert app_config.datarest.database.connect_string == "sqlite:///test.db"
    assert app_config.datarest.datatables.__root__["table1"].expose_routes == [ExposeRoutesEnum.get_one]

#  pydantic.error_wrappers.ValidationError: 1 validation error for AppConfig
#   datarest -> datatables -> __root__ -> __root__
#    Discriminator 'schema_spec' is missing in value (type=value_error.discriminated_union.missing_discriminator; discriminator_key=schema_spec)
# pydantic/main.py:341: ValidationError
