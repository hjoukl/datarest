# The datarest command line interface
import os
import string
import time
from pathlib import Path
import shutil
from typing import List, Optional

import frictionless
from frictionless import formats
import yaml

from . import _cfgfile
from . import _models
from . import _yaml_tools
from ._resource_ids import IdEnum
from ._data_resource_tools import (
    add_descriptions, add_examples, modify_resource_fields,
    field_name_normalizer, field_type_mapper, make_required, primary_key_step)


# Make Decimal objects work with pyyaml (needed for examples).
_yaml_tools.dump_decimal_as_str()
# Add a selective str representer that uses YAML block style for strings with
# newlines.
_yaml_tools.set_selective_str_blockstyle(Dumper=yaml.SafeDumper)


def _dict_from(colon_str_seq):
    """Return {name: value} dict from ['name:value', ...] sequence.
    """
    dct = {}
    for colon_str in colon_str_seq:
        name, value = colon_str.split(':')
        name = name.strip()
        value = value.strip()
        dct[name] = value
    return dct


def cli():
    # uvicorn uses click, so we are able to integrate it with the typer cli
    import click
    import typer
    import uvicorn
    app = typer.Typer()
    # nested subcommands
    init_app = typer.Typer()

    # Order is crucial: @app.command() incantations must come before callback
    # and the type-click-integration stuff, otherwise not both our and
    # uvicorn's commands are hooked properly
    def authn_backend_callback(
            ctx: typer.Context, param: typer.CallbackParam, value: str):
        print(ctx, param, value)
        return value


    # define our own exposed cli commands & params
    @init_app.command()
    def datafile(
            datafile: str = typer.Argument(...),
            encoding: Optional[str] = typer.Option(None),
            connect_string: Optional[str] = typer.Option("sqlite:///app.db"),
            expose: Optional[List[_cfgfile.ExposeRoutesEnum]] = typer.Option(
                ('get_one',), help='Select the API method(s) to expose'),
            resource_id_type: Optional[IdEnum] = typer.Option(
                'uuid4_base64', help='Type of resource ID to expose'),
            primary_key: List[str] = typer.Option(
                [], help='Provide one or more primary key field(s)'),
            required: List[str] = typer.Option(
                [], help='Set one or more additionally required field(s), i.e.'
                ' not marked as optional.'),
            query: List[str] = typer.Option(
                [], help='Provide one or more field(s) eligible as query'
                ' parameter'),
            title: Optional[str] = typer.Option(
                None, help='API title (defaults to table name)'),
            version: Optional[str] = typer.Option('0.1.0'),
            prefix: Optional[str] = typer.Option(
                None, help='API URL endpoints path prefix'),
            description: str = typer.Option(
                '', help='Provide API description as a string of a filename'),
            field_description: Optional[List[str]] = typer.Option(
                None, help='Provide one or more field description(s)'),
            field_type: Optional[List[str]] = typer.Option(
                None, help='Provide one or more field type(s), overriding '
                'automatic type detection'),
            paginate: int = typer.Option(10, help='Max. pagination limit'),
            rewrite_datafile: bool = typer.Option(
                False, help='Rewrite normalized + id-enhanced data file'),
            authn: Optional[_cfgfile.AuthnEnum] = typer.Option(
                None, help='Authentication scheme (authn frontend)'),
            authn_backend: Optional[_cfgfile.AuthnBackendEnum] = typer.Option(
                None, help='Authenticator mechanism (authn backend)', 
                callback=authn_backend_callback),
            ldap_bind_dn: Optional[str] = typer.Option(
                None, help='LDAP bind dn, use {uid} as login user name '
                'placeholder (e.g. "uid={uid},ou=people,dc=...")'),
            ldap_server: Optional[str] = typer.Option(
                None, help='LDAP server'),
            ):
        cfg_path = Path('app.yaml')
        if cfg_path.exists():
            typer.echo(f'Found existing {cfg_path.name}, skipping init.')
            raise typer.Exit(1)
        try:
            # TODO: datafile can be an URL - add proper support for this.
            # TODO: This is a hack, we're applying Path to a potential URL.
            # While it works this is obviously less than ideal.
            datafile_p = Path(datafile)
            if rewrite_datafile:
                # backup local table data file
                if datafile_p.exists():
                    timestamp = int(time.time())
                    datafile_bak = datafile_p.with_name(
                        f'{datafile_p.name}.{timestamp}.bak')
                    shutil.copyfile(datafile, datafile_bak)

            table = datafile_p.stem.lower()

            title = f"{table} API" if title is None else title
            # write main app.yaml config file
            _cfgfile.write_app_config(
                cfg_path,
                app_config=_cfgfile.app_config(
                    table=table,
                    title=title,
                    version=version,
                    prefix=prefix,
                    description=description,
                    connect_string=connect_string,
                    expose_routes=expose,
                    query_params=query,
                    paginate=paginate,
                    authn=authn,
                    authn_backend=authn_backend,
                    ldap_bind_dn=ldap_bind_dn,
                    ldap_server=ldap_server,
                    )
                )

            datafile_resource = frictionless.describe(
                datafile, encoding=encoding)

            # Normalize table headers to be valid identifiers, use string
            # instead of any tableschema datatype.
            # See https://github.com/frictionlessdata/framework/issues/812 for
            # background to CSV any detection.
            # TODO: Should this better be done with transform steps?
            # Is there a simple way to modify header names and avoid rewriting
            # the data?
            # Create {field_name: type_name} lookup table.
            name2type = _dict_from(field_type)

            # Caution: The order of the modifiers positional args is crucial,
            # currently. The reason seems to be that changes made directly on a
            # field are not always properly reflected on the containing schema.
            # Maybe a bug in frictionless?
            # TODO: Investigate frictionless schema.fields consistency.
            datafile_resource = modify_resource_fields(
                datafile_resource,
                field_name_normalizer(),
                make_required(field_names=required),
                field_type_mapper(
                    type2type={'any': 'string'}, name2type=name2type),
                )

            if field_description:
                add_descriptions(
                    datafile_resource, **_dict_from(field_description))

            if _cfgfile.ExposeRoutesEnum.create in expose:
                create_exposed = True
            else:
                create_exposed = False

            try: 
                add_examples(datafile_resource)
            except IndexError:
                print(f'Warning: using 1st data row for examples failed')

            # Inject primary key into the resource schema. Depending on the
            # used id type this adds a single generated id field to the tabular
            # resource data.
            add_pk_step = primary_key_step(
                datafile_resource,
                id_type=resource_id_type,
                primary_key=primary_key,
                create_exposed=create_exposed,
            )
            resource_with_pk = frictionless.transform(
                datafile_resource,
                steps=[add_pk_step()])

            # Create data resource yaml file
            resource_path = f'{table}.yaml'
            resource_with_pk.to_yaml(resource_path)

            if rewrite_datafile:
                # write id (primary key)-enhanced + normalized data file
                resource_with_pk.write(datafile)

            cfg = _cfgfile.read_app_config()
            from . import _database
            from sqlmodel import SQLModel
            models = _models.create_models(cfg.datarest.datatables)
            SQLModel.metadata.create_all(_database.engine)

            resource_with_pk.write(
                cfg.datarest.database.connect_string,
                control=formats.SqlControl(table=table))
        except Exception as exc:
            typer.echo(exc)
            # raise typer.Exit(1)
            raise

    @init_app.command()
    def db(
            table: str = typer.Argument(...),
            connect_string: str = typer.Option("sqlite:///app.db"),
            expose: Optional[List[_cfgfile.ExposeRoutesEnum]] = typer.Option(
                ('get_one',), help='Select the API method(s) to expose'),
            query: List[str] = typer.Option(
                [], help='Provide one or more field(s) eligible as query'
                ' parameter'),
            title: Optional[str] = typer.Option(
                None, help='API title (defaults to table name)'),
            version: Optional[str] = typer.Option('0.1.0'),
            prefix: Optional[str] = typer.Option(
                None, help='API URL endpoints path prefix'),
            description: str = typer.Option(
                '', help='Provide API description as a string of a filename'),
            field_description: Optional[List[str]] = typer.Option(
                None, help='Provide one or more field description(s)'),
            paginate: int = typer.Option(10, help='Max. pagination limit'),
            authn: Optional[_cfgfile.AuthnEnum] = typer.Option(
                None, help='Authentication scheme (authn frontend)'),
            authn_backend: Optional[_cfgfile.AuthnBackendEnum] = typer.Option(
                None, help='Authenticator mechanism (authn backend)', 
                callback=authn_backend_callback),
            ldap_bind_dn: Optional[str] = typer.Option(
                None, help='LDAP bind dn'),
            ldap_server: Optional[str] = typer.Option(
                None, help='LDAP server'),
            ):
        cfg_path = Path('app.yaml')
        if cfg_path.exists():
            typer.echo(f'Found existing {cfg_path.name}, skipping init.')
            raise typer.Exit(1)
        try:
            # write main app.yaml config file
            _cfgfile.write_app_config(
                cfg_path,
                app_config=_cfgfile.app_config(
                    table=table,
                    title=table.title(),
                    description=description,
                    version=version,
                    connect_string=connect_string,
                    expose_routes=expose,
                    query_params=query,
                    paginate=paginate,
                    authn=authn,
                    authn_backend=authn_backend,
                    ldap_bind_dn=ldap_bind_dn,
                    ldap_server=ldap_server,
                    )
                )

            # Connect to DB using environment-expanded connect_string
            db_resource = frictionless.describe(
                string.Template(connect_string).substitute(os.environ),
                control=formats.SqlControl(table=table)
                )

            if field_description:
                add_descriptions(db_resource, **_dict_from(field_description))
            add_examples(db_resource)

            primary_key = db_resource.schema.primary_key
            if isinstance(primary_key, str):
                primary_key = [primary_key,]

            if len(primary_key) == 0:
                raise ValueError(
                    f'DB table {table} has no primary key constraint')
            elif len(primary_key) > 1:
                raise ValueError(
                    f'Composite primary database key {primary_key} not '
                    f'supported')

            pk_field = db_resource.schema.get_field(name=primary_key[0])
            if pk_field.type in ['string']:
                db_resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type': str(IdEnum.uuid4_base64),
                    'id_src_fields': []
                }
            else:
                # TODO: This works for an integer PK - care for other types
                # and check if create route is actually exposed?
                db_resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type': str(IdEnum.biz_key),
                    'id_src_fields': []
                }

            # Create data resource yaml file
            resource_path = f'{table}.yaml'
            db_resource.to_yaml(resource_path)

            cfg = _cfgfile.read_app_config()
            from . import _database
            from sqlmodel import SQLModel
            models = _models.create_models(cfg.datarest.datatables)
            SQLModel.metadata.create_all(_database.engine)

        except Exception as exc:
            typer.echo(exc)
            # raise typer.Exit(1)
            raise

    app.add_typer(init_app, name="init")

    # Just for providing the main command documentation
    @app.callback()
    def callback():
        """Python low code data-driven REST-Tool.
        """

    # get the typer cli's underlying click command
    typer_click_object = typer.main.get_command(app)

    # uvicorn.main is the uvicorn cli entry point.
    # Monkeypatch a default to its  'app' arg to a allow for running simply as
    # datarest run --host ... instead of datarest datarest:app --host ...
    app_arg = [
        param for param in uvicorn.main.params
        if isinstance(param, click.Argument) and param.name == 'app'][0]
    app_arg.default = 'datarest._app:app'

    # hook uvicorn's click to our typer cli here
    uvicorn.main.name = 'run'
    typer_click_object.add_command(uvicorn.main)

    return typer_click_object()
