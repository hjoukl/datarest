# Support for adding and modifying resource schema and field metadata.
# Custom transformation steps for adding resource IDs.

import enum
import functools
import re

import frictionless

from ._resource_ids import IdEnum, id_type_funcs


def add_attr(resource, attr_name, **field_attrs):
    """Add `attr_name` to each resource field if an entry for field.name
    exists in field_attrs keyword args.
    """
    for field in resource.schema.fields:
        try:
            attr_value = field_attrs[field.name]
            setattr(field, attr_name, attr_value)
        except KeyError:
            pass
    return resource


def add_descriptions(resource, **descriptions):
    """Add data resource schema field descriptions.
    """
    return add_attr(resource, attr_name='description', **descriptions)


def add_examples(resource):
    """Read 1st data row and use its values as schema field examples.
    """
    # get the 1st row as data example
    example_row = resource.extract(limit_rows=1)
    resource = add_attr(resource, attr_name='example', **example_row)
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


def field_name_normalizer(prefix='f_'):
    """Field name normalizer factory.

    Returns a callable that takes a field and normalizes its field name to a
    valid identifier.
    """
    def normalize_name(field):
        field.name = identifier_field_name(field.name, prefix=prefix)

    return normalize_name


def field_type_mapper(**type_map):
    """Field type map factory.

    Returns a type modifier callable that expects a tableschema field and 
    substitutes its type name, looked up in type_map.
    """
    def modify_type(field):
        # Default to original type, if no map given.
        new_type = type_map.get(field.type, field.type)
        field.schema.set_field_type(field.name, new_type)

    return modify_type


def modify_resource_fields(resource, *modifiers):
    """Loop over resource.schema.fields and modify field properties with
    given modifiers.

    Returns the (in-place) modified resource.

    E.g.
        resource = modifiy_resource_fields(
            resource,
            field_name_normalizer(),
            field_type_mapper(any='string')
            )
    """
    for field in resource.schema.fields:
        for modify in modifiers:
            modify(field)
    return resource


def composite_id_step(
        id_,
        id_type,
        primary_key,
        field_names,
        id_field_name='id_',
        concat_sep='.'
    ):
    """Return a custom frictionless resource transform step that uses the
    provided id_ generation callable to derive a unique key from a composite
    natural/biz key.

    Parameters:
        id_: a callable with signature id_(*fields, concat_sep) to generate a
            unique ID from the composite primary key fields.
        id_type: a _resource_ids.IdEnum
        primary_key: the natural/biz primary key field tuple
        field_names: the table schema field names list
        id_field_name: name to use for the generated composite id field
        concat_sep: separator to use for key field concatenation
    """
    # Get the given PK field indexes for use in the transform step
    pk_indexes = [
        i for (i, field_name) in enumerate(field_names)
        if field_name in set(primary_key)
        ]

    class _composite_id_step(frictionless.Step):

        def transform_resource(self, resource):
            # a frictionless resource transform step to add a single field
            # resource id from the primary key fields

            current = resource.to_copy()

            # Data

            def data():
                with current:
                    for line in current.cell_stream:
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
                frictionless.fields.StringField(
                    name=id_field_name, description='Unique resource id'
                    )
                )
            resource.schema.primary_key = [id_field_name]
            resource.schema.custom['x_datarest_primary_key_info'] = {
                'id_type': str(id_type),
                'id_src_fields': list(primary_key)
                }

    return _composite_id_step


# These ID types do not use business keys i.e. existing field data but
# generated unique IDs (UUID, GUID).
non_biz_id_types = set([IdEnum.uuid4_base64])


def primary_key_step(
        resource,
        id_type: IdEnum,
        primary_key=(),
        create_exposed=False,
        id_field_name='id_',
        concat_sep='.'
    ):
    """Return a custom frictionless resource transform step to add a single
    primary key field to a given resource.
    """
    fields = resource.schema.fields
    field_names = resource.schema.field_names

    # Default to 1st column for biz keys if no primary key field name given.
    if id_type not in non_biz_id_types and not primary_key:
        primary_key = (fields[0].name, )

    primary_key_set = set(primary_key)
    if not primary_key_set <= set(field_names):
        raise ValueError(
            f'Primary key fields {primary_key} not a subset of table fields '
            f'{field_names}'
            )

    if id_type == IdEnum.biz_key:
        if len(primary_key) > 1:
            raise ValueError(
                f'Composite primary key not supported for ID type {id_type}'
                )
        pk_field = resource.schema.get_field(name=primary_key[0])
        if create_exposed and pk_field.type not in ['integer']:
            raise ValueError(
                f'ID type {id_type} must be integer if data create is exposed'
                )

        class _primary_key_step(frictionless.Step):

            def transform_resource(self, resource):
                # Meta
                resource.schema.primary_key = list(primary_key)
                resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type': str(id_type),
                    'id_src_fields': list(primary_key)
                    }

        return _primary_key_step

    else:
        if id_field_name in field_names:
            raise ValueError(
                f'ID field name {id_field_name} conflicts with existing field '
                f'name'
                )

        id_ = id_type_funcs[id_type]

        step = composite_id_step(
            id_=id_,
            id_type=id_type,
            primary_key=primary_key,
            field_names=field_names,
            id_field_name=id_field_name,
            concat_sep=concat_sep
            )

        return step

    raise ValueError(f'Id type {id_type} is not supported')
