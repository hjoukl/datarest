#contains trials and other stuff which helps understanding the code

import pytest
import csv
import os
from pydantic import BaseModel, Field
from pathlib import Path
import typer
import yaml
import sys
import frictionless
from pprint import pprint

from datarest._yaml_tools import str_representer, dump_as_str
from datarest._cfgfile import AppConfig, write_app_config
from datarest._resource_ids import IdEnum
from datarest._data_resource_tools import add_attr, add_descriptions, add_examples

#create a test-csv file and safe it in the same directory
def create_test_data_csv():

    file_name = "countries.csv"
    file_path = "/ae/data/work/lb10732/datarest/tests/"+file_name

    FileExists = os.path.exists(file_path)  

    if FileExists == True:
        print("Data already exists")
    else:
        header = ["no", "name", "capital"]
        data = [
            ["1", "germany", "berlin"],
            ["2", "france", "paris"],
            ["3", "austria", "vienna"],
            ["4", "czech_republic", "prague"],
            ["5", "poland", "warsaw"]]

        with open (file_path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

def save_test_data_as_str():
    #with open (filepath="countries.csv", "r") as file:
        example_data = str(file.readlines())
        return example_data
        

@pytest.mark.skip
def test_app_config():
    test_table_path = Path("countries.csv")
    test_table = test_table_path.stem.lower()
    test_config = app_config(table=test_table, title="TEST")
    return test_config
    assert isinstance(test_config, AppConfig) == True
    assert test_config.datarest.fastapi.app.title == "TEST API"
 

def check_for_type():
    #helper function
    with open ("colors.csv", "r") as file:
        file_type = type(file)
        print(file_type)



    """
    # Create a Dumper object for use in the tests
    dumper = yaml.Dumper(stream=sys.stdout)
    
    # Check that the custom representer has been registered for the SampleClass
    assert dumper.yaml_representers[SampleClass] == str_representer
    assert dumper.yaml_representers[SampleClass] == str_representer

    # Create an object of the SampleClass and check that it is dumped as a string
    sample_obj = SampleClass()
    assert dumper.represent_data(sample_obj) == dumper.represent_str(str(sample_obj))
    """


def test_dump_decimal_as_str():
    # Dump a Decimal object as a string
    dump_decimal_as_str()
    data = {'price': decimal.Decimal('12.34')}
    expected_output = 'price: "12.34"\n'
    output = yaml.dump(data)
    assert output == expected_output

def test_write_app_config_invalid_cfg_path_type():
    write_app_config(123, AppConfig(...))


def create_id_default(
        id_type: IdEnum,
        primary_key=(),
        concat_sep='.'):
    """Return an SQLAlchemy column default function for a the primary key ID
    column.
    """
    id_func = id_type_funcs[id_type]
    if id_func is None:
        # let the database handle id creation
        id_ = None
        return id_
    else:
        def id_(context):
            # a function to create the resource id as a single field composite
            # biz key
            print(type(context))
            data = context.current_parameters
            print(type(data))
            fields = (data[pk_field_name] for pk_field_name in primary_key)
            return id_func(*fields, concat_sep=concat_sep)
        return id_

    raise ValueError(f'Id type {id_type} is not supported')

#prototype test for the test_routes module
def test_create_routes():

    create_routes(app, models)
    
    # Test that the correct number of routes are registered with the app
    assert len(app.routes) >= len(models)
    
    # Test that the correct routes are exposed for each model
    for (model_name, model) in models.items():
        router = [route for route in app.routes if route.name.startswith(model.resource_name)][0]
        for expose in model.expose_routes:
            assert getattr(router, f"{expose}_route") == True
        for route in expose_routes_default:
            if route not in model.expose_routes:
                assert getattr(router, f"{route}_route") == False
    
    # Test that the correct db connection is used for each model
    for (model_name, model) in models.items():
        router = [route for route in app.routes if route.name.startswith(model.resource_name)][0]
        assert router.db() == get_db()

#prototype test for the test_data_resource_tools module
def test_add_attr():
    # Test adding an attribute to all fields in a resource's schema
    resource = frictionless.Resource(data=[['col1', 'col2'], [1, 2]])
    expected = frictionless.Resource(
        data=[['col1', 'col2'], [1, 2]],
        schema={
            'fields': [
                {'name': 'col1', 'test_attr': 'val1'},
                {'name': 'col2', 'test_attr': 'val2'},
            ]
        }
    )
    assert add_attr(resource, 'test_attr', col1='val1', col2='val2') == expected


    # Test adding an attribute to a resource with no fields
    resource = frictionless.Resource(data=[])
    expected = frictionless.Resource(data=[])
    assert add_attr(resource, 'test_attr', col1='val1', col2='val2') == expected
    

    # Test adding an attribute with a value of None
    resource = frictionless.Resource(data=[['col1', 'col2'], [1, 2]])
    expected = frictionless.Resource(
        data=[['col1', 'col2'], [1, 2]],
        schema={
            'fields': [
                {'name': 'col1', 'test_attr': None},
                {'name': 'col2', 'test_attr': None},
            ]
        }
    )
    assert add_attr(resource, 'test_attr') == expected

def test_add_descriptions():
    # Test adding descriptions to all fields in a resource's schema
    resource = frictionless.Resource(data=[['col1', 'col2'], [1, 2]])
    expected = frictionless.Resource(
        data=[['col1', 'col2'], [1, 2]],
        schema={
            'fields': [
                {'name': 'col1', 'description': 'description1'},
                {'name': 'col2', 'description': 'description2'},
            ]
        }
    )
    assert add_descriptions(resource, col1='description1', col2='description2') == expected
    
    # Test adding descriptions to a resource with no fields
    resource = frictionless.Resource(data=[])
    expected = frictionless.Resource(data=[])
    assert add_descriptions(resource, col1='description1', col2='description2') == expected
    
    # Test adding descriptions with a value of None
    resource = frictionless.Resource(data=[['col1', 'col2'], [1, 2]])
    expected = frictionless.Resource(
        data=[['col1', 'col2'], [1, 2]],
        schema={
            'fields': [
                {'name': 'col1', 'description': None},
                {'name': 'col2', 'description': None},
            ]
        }
    )
    assert add_descriptions(resource) == expected


def test_add_examples():
    # Test adding examples from the first row of data to all fields in a resource's schema
    resource = frictionless.Resource(data=[['col1', 'col2'], [1, 2]])
    expected = frictionless.Resource(
        data=[['col1', 'col2'], [1, 2]],
        schema={
            'fields': [
                {'name': 'col1', 'example': 1},
                {'name': 'col2', 'example': 2},
            ]
        }
    )
    assert add_examples(resource) == expected
    
    # Test adding examples to a resource with no fields
    resource = frictionless.Resource(data=[])
    expected = frictionless.Resource(data=[])
    assert add_examples(resource) == expected
    
    # Test adding examples to a resource with a single field
    resource = frictionless.Resource(data=[['col1'], [1]])
    expected = frictionless.Resource(
        data=[['col1'], [1]],
        schema={
            'fields': [
                {'name': 'col1', 'example': 1},
            ]
        }
    )
    assert add_examples(resource) == expected

# Test normalizing field names in a resource with a single field
    resource = frictionless.Resource(data=[['3col'], [1]])
    expected = frictionless.Resource(data=[['f_3col'], [1]], schema={'fields': [{'name': 'f_3col'}]})
    assert normalize_field_names(resource) == expected
    
    # Test normalizing field names in a resource with no fields
    resource = frictionless.Resource(data=[])
    expected = frictionless.Resource(data=[])
    assert normalize_field_names(resource) == expected
    
    # Test normalizing field names with a custom prefix
    resource = frictionless.Resource(data=[['3col'], [1]])
    expected = frictionless.Resource(data=[['p_3col'], [1]], schema={'fields': [{'name': 'p_3col'}]})
    assert normalize_field_names(resource, prefix='p_') == expected

if __name__=="__main__":
    #create_test_data_csv()
    #test_app_config(example_data)
    #test_config = test_app_config()
    #print(type(test_config))
    #test_path = Path("countries_app.yaml")
    #write_app_config(test_path, test_config)
    
