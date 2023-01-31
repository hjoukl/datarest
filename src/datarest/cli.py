# The datarest command line interface
import os
import string
import time
from pathlib import Path
import shutil
from typing import List, Optional

import frictionless
from frictionless import formats

from . import _cfgfile
from . import _models
from . import _yaml_tools
from ._resource_ids import IdEnum
from ._data_resource_tools import (
    add_descriptions, add_examples, normalize_field_names, primary_key_step)


# Make Decimal objects work with pyyaml (needed for examples)
_yaml_tools.dump_decimal_as_str()


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

    # define our own exposed cli commands & params
    @init_app.command()
    def datafile(
            datafile: Path = typer.Argument(...),
            encoding: Optional[str] = typer.Option(None),
            connect_string: Optional[str] = typer.Option("sqlite:///app.db"),
            expose: Optional[List[_cfgfile.ExposeRoutesEnum]] = typer.Option(
                ('get_one',), help='Select the API method(s) to expose'),
            resource_id_type: Optional[IdEnum] = typer.Option(
                'uuid4_base64', help='Type of resource ID to expose'),
            primary_key: List[str] = typer.Option(
                [], help='Provide one or more primary key field(s)'),
            query: List[str] = typer.Option(
                [], help='Provide one or more field(s) eligible as query'
                ' parameter'),
            description: str = typer.Option(
                '', help='Provide API description'),
            field_description: Optional[List[str]] = typer.Option(
                None, help='Provide one or more field description(s)'),
            rewrite_datafile: bool = typer.Option(
                False, help='Rewrite normalized + id-enhanced data file'),
            authn: Optional[_cfgfile.AuthnEnum] = typer.Option(
                None, help='Authentication mechanism'),
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
            if rewrite_datafile:
                # backup table data file
                timestamp = int(time.time())
                datafile_bak = datafile.with_name(
                    f'{datafile.name}.{timestamp}.bak')
                shutil.copyfile(datafile, datafile_bak)

            table = datafile.stem.lower()

            # write main app.yaml config file
            _cfgfile.write_app_config(
                cfg_path,
                app_config=_cfgfile.app_config(
                    table=table,
                    title=table.title(),
                    description=description,
                    version='0.1.0',
                    connect_string=connect_string,
                    expose_routes=expose,
                    query_params=query,
                    authn_type=authn,
                    ldap_bind_dn=ldap_bind_dn,
                    ldap_server=ldap_server,
                    )
                )

            datafile_resource = frictionless.describe(
                datafile, encoding=encoding)

            # normalize table headers to be valid identifiers
            # TODO: Should this better be done with transform steps?
            # Is there a simple way to modify header names and avoid rewriting
            # the data?
            datafile_resource = normalize_field_names(
                datafile_resource)

            if field_description:
                add_descriptions(
                    datafile_resource, **_dict_from(field_description))

            if _cfgfile.ExposeRoutesEnum.create in expose:
                create_exposed = True
            else:
                create_exposed = False

            add_examples(datafile_resource)

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
            description: str = typer.Option(
                '', help='Provide API description'),
            field_description: Optional[List[str]] = typer.Option(
                None, help='Provide one or more field description(s)'),
            authn: Optional[_cfgfile.AuthnEnum] = typer.Option(
                None, help='Authentication mechanism'),
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
                    version='0.1.0',
                    connect_string=connect_string,
                    expose_routes=expose,
                    query_params=query,
                    authn_type=authn,
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

            if len(primary_key) > 1:
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
