import pytest
from pathlib import Path 
import yaml
import os
import tempfile
from pydantic import ValidationError

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


def test_write_app_config_invalid_app_config_type():
    # app_config parameter has the wrong type
    with pytest.raises(AttributeError):
        write_app_config('test.yaml', 'invalid_type')


def test_write_app_config_invalid_cfg_path_type():
    # cfg_path parameter is not a valid path
    with pytest.raises(TypeError):
        write_app_config(123, AppConfig(...))


def test_write_app_config_empty_cfg_path():
    # Test that path-parameter is not a valid path to a file
    with pytest.raises(FileNotFoundError):
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
        cfg_path = 'test.yaml'
        write_app_config(cfg_path, app_config)
        read_config = read_app_config(cfg_path)
        assert read_config == app_config
    finally:
        os.remove(cfg_path)


def test_read_app_config_invalid_yaml():
    # Test that an error is raised if the yaml contains invalid data
    
    invalid_yaml = """
    datarest:
        fastapi:
            app:
                title: Invalid API
                version: 1.0.0
    """
    try:
        cfg_path = 'test.yaml'
        with open(cfg_path, 'w') as f:
            f.write(invalid_yaml)
        with pytest.raises(ValidationError):
            read_app_config(cfg_path)
    finally:
        os.remove(cfg_path)


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
                    "table1": {
                        "schema_spec": "https://www.sqlalchemy.org/",
                        "schema": "table1.yaml",
                        "dbtable": "table1",
                        "expose_routes": ["get_one"],
                    },
                },
            },
        }

    app_config = AppConfig.parse_obj(valid_data)
    assert app_config.datarest.fastapi.app.title == "Test API"
    assert app_config.datarest.database.connect_string == "sqlite:///test.db"
    assert app_config.datarest.datatables.__root__["table1"].expose_routes == [ExposeRoutesEnum.get_one]


