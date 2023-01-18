import pytest
import frictionless

from datarest._data_resource_tools import add_attr, add_descriptions, identifier_field_name, normalize_field_names

@pytest.mark.skip
def test_add_attr():
    # Test adding an attribute to all fields in a resource's schema
    resource = frictionless.Resource(data=[['col1', 'col2'], [1, 2]])
    print(resource)

    resource_2 = add_attr(resource, 'test_attr')
    print(resource_2)



    # tst umschreiben, so dass am ende gecheckt wird, ob col1 ein attribut test_attr besitzt mit val1

# evtl parametrisieren
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

#gleiches wie in (1)
@pytest.mark.skip
def test_normalize_field_names():
    # Test normalizing field names in a resource with multiple fields
    resource = frictionless.Resource(
        data=[['col 1', 'col-2', '3col'], [1, 2, 3]],
        schema={
            'fields': [
                {'name': 'col 1'},
                {'name': 'col-2'},
                {'name': '3col'},
            ]
        }
    )
    expected = frictionless.Resource(
        data=[['col_1', 'col_2', 'f_3col'], [1, 2, 3]],
        schema={
            'fields': [
                {'name': 'col_1'},
                {'name': 'col_2'},
                {'name': 'f_3col'},
            ]
        }
    )
    assert normalize_field_names(resource) == expected

if __name__=="__main__":
    test_add_attr()

