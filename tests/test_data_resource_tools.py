import pytest
from frictionless import Schema, Resource, fields, describe, steps, transform, Pipeline

from datarest._data_resource_tools import add_attr, add_descriptions, add_examples,  identifier_field_name, normalize_field_names, composite_id_step
from datarest.cli import _dict_from
from datarest._resource_ids import IdEnum, id_type_funcs


"""
@pytest.fixture
def generate_test_data():
    expected_schema = Schema(
            fields=[fields.StringField(name='field1', description="test_description"), 
            fields.StringField(name='field2', description="test_description")])

    expected_resource = Resource(
            name ="test",
            data = [],
            schema = expected_schema
        )

    test_schema = Schema(fields=[fields.StringField(name='field1'), fields.StringField(name='field2')])
    test_resource = Resource(name='test',schema=test_schema, data=[])

    return expected_resource, test_resource
"""


def test_add_attr():
    # Test adding an attribute, value pair to all fields in a resource's schema
    
    expected_schema = Schema(
            fields=[fields.StringField(name='field1', description="test_description"), 
            fields.StringField(name='field2', description="test_description")])

    expected_resource = Resource(
            name ="test",
            data = [],
            schema = expected_schema
        )
    test_schema = Schema(fields=[fields.StringField(name='field1'), fields.StringField(name='field2')])
    test_resource = Resource(name='test',schema=test_schema, data=[])
    attributes = {"field1": "test_description", "field2": "test_description"}
    add_attr(test_resource, 'description', **attributes)

    test_field_1 = test_resource.schema.get_field("field1").to_dict()
    test_field_2 = test_resource.schema.get_field("field2").to_dict()

    # test that attribute with value has been generated
    assert("description", "test_description") in test_field_1.items()
    assert("description", "test_description") in test_field_2.items()

    # test that expected resource == actual resource
    expected_resource = expected_resource.to_dict()
    test_resource = test_resource.to_dict()
    assert expected_resource == test_resource
    

def test_add_attr_empty_value():
    # test adding an empyt value to an attribute
    
    test_schema = Schema(fields=[fields.StringField(name='field1'), fields.StringField(name='field2')])
    test_resource = Resource(name='test',schema=test_schema, data=[])
    
    attributes = {"field1": "", "field2": ""}
    add_attr(test_resource, 'description', **attributes)

    test_field_1 = test_resource.schema.get_field("field1").to_dict()
    test_field_2 = test_resource.schema.get_field("field2").to_dict()

    assert("description", "") in test_field_1.items()
    assert("description", "") in test_field_2.items()


def test_add_attr_empty_attribute():
    # test adding an attribute with an empty value -> expected-result: no attribute added

    test_schema = Schema(fields=[fields.StringField(name='field1'), fields.StringField(name='field2')])
    test_resource = Resource(name='test',schema=test_schema, data=[])

    attributes = {"field1": "testlabel", "field2": "testlabel"}
    add_attr(test_resource, "", **attributes)

    test_field_1 = test_resource.schema.get_field("field1").to_dict()
    test_field_2 = test_resource.schema.get_field("field2").to_dict()

    assert("", "testlabel") not in test_field_1.items()
    assert("", "testlabel") not in test_field_2.items()


def test_add_descriptions():

    test_schema = Schema(fields=[fields.StringField(name='field1'), fields.StringField(name='field2')])
    test_resource = Resource(name='test',schema=test_schema, data=[])

    descriptions = {"field1": "This is field 1", "field2": "This is field 2"}
    add_descriptions(test_resource, **descriptions)
    
    test_description_1 = test_resource.schema.get_field("field1").to_dict()
    test_description_2 = test_resource.schema.get_field("field2").to_dict()

    assert("description", "This is field 1") in test_description_1.items()
    assert("description", "This is field 2") in test_description_2.items()


def test_add_examples():

    data = [["name", "age", "city"],
        ["Patrick", 28, "Stuttgart"],
        ["Vivienne", 36, "München"]]
    
    test_resource = describe(data)
    add_examples(test_resource)
    
    test_example_1 = test_resource.schema.get_field("name").to_dict()
    test_example_2 = test_resource.schema.get_field("age").to_dict()
    test_example_3 = test_resource.schema.get_field("city").to_dict()

    assert("example", "Patrick") in test_example_1.items()
    assert("example", 28) in test_example_2.items()
    assert("example", "Stuttgart") in test_example_3.items()
    

# parametrisieren -> für Integer values interessant, ansonsten evtl. schlechter lesbar
# pytest.mark.parametrize("field1, output", [("field_name, field_name")])
# über test_identifier_field_name werden auch die funktionen normalize_headers und normalize_headers_step abgedeckt
# beide funktionen benutzen im grunde nur die identifier_field_name()-Funktion

def test_identifier_field_name():
    # Test field names that are already valid identifiers
    assert identifier_field_name('field_name') == 'field_name'
    assert identifier_field_name('_private') == '_private'
    assert identifier_field_name('class') == 'class'
    
    # Test field names that start with a numeric character
    assert identifier_field_name('1field') == 'f_1field'
    assert identifier_field_name('1field', prefix='p_') == 'p_1field'
    
    # Test empty field name
    assert identifier_field_name('') == 'f_'
    assert identifier_field_name('', prefix='p_') == 'p_'


@pytest.mark.skip(reason="how to test a step?")
def test_composite_id_step():
    
    data = [["id","name", "age", "city"],
        [1, "Patrick", 28, "Stuttgart"],
        [2, "Vivienne", 36, "München"]]
    
    test_resource = describe(data)
    transform_step = composite_id_step(
        id_= lambda *fields, concat_sep: concat_sep.join(map(str, fields)),
        id_type="custom",
        primary_key=("id"),
        field_names=test_resource.schema.field_names,
        id_field_name='composite_id'
    )

    pipeline = Pipeline(steps=[transform_step])
    transform_result = transform(data, pipeline=pipeline)
    
    # breakpoint()
    # ????


if __name__=="__main__":
    test_add_attr_empty_attribute()

