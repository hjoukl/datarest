# support for different resource IDs

import enum
import re

import frictionless

from ._resource_ids import (
    IdEnum, id_type_funcs,
    )


def add_attr(resource, attr_name, **field_attrs):
    """Add attr: value to data resource table schema fields for each field in
    {field_name: value} field dict.
    """
    for field in resource.schema.fields:
        attr_value = field_attrs[field.name]
        setattr(field, attr_name, attr_value)
    return resource


def add_descriptions(resource, **descriptions):
    """Add data resource schema field descriptions.
    """
    return add_attr(resource, attr_name='description', **descriptions)


def add_examples(resource):
    """Read 1st data row and use its values as schema field examples.
    """
    # get the 1st row as data example
    example_row = next(resource.extract(stream=True))
    # dict-unpacking doesn't reliably work with Row objects, see
    # https://github.com/frictionlessdata/frictionless-py/issues/1152
    resource = add_attr(resource, attr_name='example', **example_row.to_dict())

    # Reading data from a resource adds stats information to the resource
    # object, which we don't need. So remove it.
    resource.pop('stats')
    return resource


def identifier_field_name(name, prefix='f_'):
    """Change resource field names to valid identifiers.
    """
    if not name.isidentifier():
        name = re.sub('[^0-9a-zA-Z_]', '_', name)
        if not name.isidentifier():
            # starts with a numeric character
            name = f'{prefix}{name}'
    return name


def normalize_field_names(resource, prefix='f_'):
    """Normalize resource header field names to valid identifiers.
    """
    for field in resource.schema.fields:
        field.name = identifier_field_name(field.name)
    return resource


def normalize_headers_step(prefix='f_'):
    """Normalize resource header field names to valid identifiers.
    
    Custom frictionless transform step.
    
    Parameters:
        prefix: Add prefix to field names that start with a numeric character
            after character substitution.
    """
    def step(resource):
        # a frictionless resource transform step to normalize headers
        current = resource.to_copy()
        # Meta
        resource.data = current.data
        normalize_field_names(resource, prefix=prefix)
        return step 


def composite_id_step(
        id_, id_type, primary_key, field_names, id_field_name='id_',
        concat_sep='.'):
    """Create a resource transform step using the provided id_ generation
    callable.

    Custom frictionless transform step.
    
    Parameters:
        id_: a callable id_(*fields, concat_sep) to generate a unique ID
        id_type: a _resource_ids.IdEnum
        primary_key: the natural/biz primary key field tuple
        field_names: the table schema field names list
        id_field_name: name to use for the generated composite id field
        concat_sep: separator to use for key field concatenation
    """
    # Get the given PK field indexes for use in the transform step
    pk_indexes = [
        i for (i, field_name) in enumerate(field_names)
        if field_name in set(primary_key)]

    def step(resource):
        # a frictionless resource transform step to add a single field 
        # resource id from the primary key fields

        current = resource.to_copy()
        # Data
        def data():
            with current:
                for line in current.list_stream:
                    # can't use operator.itemgetter here since it doesn't
                    # always return tuples but a single value for a single
                    # index arg
                    pk_fields = (line[i] for i in pk_indexes)
                    composite_id = id_(*pk_fields, concat_sep=concat_sep)
                    line.insert(0, composite_id)
                    yield line

        # Meta
        resource.data = data
        resource.schema.fields.insert(
            0,
            frictionless.Field(
                name=id_field_name, type='string',
                description='Unique resource id')
            )
        resource.schema.primary_key = [id_field_name]
        resource.schema['x_datarest_primary_key_info'] = {
            'id_type': str(id_type),
            'id_src_fields': list(primary_key)
            }
    return step


def primary_key_step(
        resource,
        id_type: IdEnum,
        primary_key=(),
        create_exposed=False,
        id_field_name='id_',
        concat_sep='.'):
    """Return a custom frictionless resource transform step to add a single
    primary key field to a given resource.
    """
    fields = resource.schema.fields
    field_names = resource.schema.field_names
    if not primary_key:
        primary_key = (fields[0].name,)
    primary_key_set = set(primary_key)
    if not primary_key_set <= set(field_names):
        raise ValueError(
            f'Primary key fields {primary_key} not a subset of table fields '
            f'{field_names}')
    
    if id_type == IdEnum.biz_key:
        if len(primary_key) > 1:
            raise ValueError(
                f'Composite primary key not supported for ID type {id_type}')
        pk_field = resource.schema.get_field(name=primary_key[0])
        if create_exposed and pk_field.type not in ['integer']:
            raise ValueError(
                f'ID type {id_type} must be integer if data create is exposed')

        def step(resource):
            current = resource.to_copy()
            # Meta
            resource.schema.primary_key = list(primary_key)

            resource.schema['x_datarest_primary_key_info'] = {
                'id_type': str(id_type),
                'id_src_fields': list(primary_key)
                }

        return step

    else:
        if id_field_name in field_names:
            raise ValueError(
                f'ID field name {id_field_name} conflicts with existing field '
                f'name')

        id_ = id_type_funcs[id_type]

        step = composite_id_step(
            id_=id_,
            id_type=id_type,
            primary_key=primary_key,
            field_names=field_names,
            id_field_name=id_field_name,
            concat_sep=concat_sep) 

        return step

    raise ValueError(f'Id type {id_type} is not supported')
