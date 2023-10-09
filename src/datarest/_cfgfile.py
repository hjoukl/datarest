# The app configuration defined as a pydantic model, plus some helpers.

import enum
from pathlib import Path
from typing import Dict, List, Optional, Union
from typing_extensions import Annotated, Literal

import yaml
from pydantic import BaseModel, Field

from . import _yaml_tools


class StrEnum(str, enum.Enum):
    """String enum base class with actual string value in str(...) output.

    Overrides the default 'IdEnum.xxx' output of the Enum class.
    """

    def __str__(self):
        # Avoid IdEnum.xxx output of Enum class, provide actual string value
        return self.value


@_yaml_tools.dump_as_str
@enum.unique
class ExposeRoutesEnum(StrEnum):
    """Enumeration of exposable endpoints.
    """
    get_all = 'get_all'
    get_one = 'get_one'
    delete_all = 'delete_all'
    delete_one = 'delete_one'
    create = 'create'
    update = 'update'


@_yaml_tools.dump_as_str
@enum.unique
class AuthnEnum(StrEnum):
    """Enumeration of authentication mechanisms.
    """
    HTTPBasic = 'HTTPBasic'
    OAuth2PasswordBearer = 'OAuth2PasswordBearer'


@_yaml_tools.dump_as_str
@enum.unique
class AuthnBackendEnum(StrEnum):
    """Enumeration of authn_backends.
    """
    LDAP = 'LDAP'



@_yaml_tools.dump_as_str
@enum.unique
class SchemaSpecEnum(StrEnum):
    """Enumeration of the supported schema specifications.
    """
    sqlalchemy = "https://www.sqlalchemy.org/"
    data_resource = "https://specs.frictionlessdata.io/data-resource/"


# The rather complex Table + Datatables implementation is needed to allow for
# using the specialized SQLAlchemyTable and TableschemaTable classes where a
# Table is expected, discriminated by their schema_spec attribute. This
# provides for putting the concrete table implementation where a base Table is
# expected and for proper serialization.

# Helper classes to enforce intended field order.

# Common Table fields
class _TableFields(BaseModel):
    dbtable: str
    paginate: int = 10
    expose_routes: Optional[List[ExposeRoutesEnum]] = [
        ExposeRoutesEnum.get_one]
    query_params: Optional[List[str]] = []


class _SQLAlchemyTableFields(BaseModel):
    schema_spec: Literal[SchemaSpecEnum.sqlalchemy]


class _TableschemaTableFields(BaseModel):
    schema_spec: Literal[SchemaSpecEnum.data_resource]
    # schema is used by pydantic so work with an alias
    schema_: str = Field(..., alias='schema')


# The actual Table implementation classes.
class SQLAlchemyTable(_SQLAlchemyTableFields, _TableFields):
    pass


class TableschemaTable(_TableschemaTableFields, _TableFields):
    pass


Table = Annotated[
    Union[TableschemaTable, SQLAlchemyTable],
    Field(discriminator='schema_spec')
    ]


class Datatables(BaseModel):
    __root__: Dict[str, Table]

    def __getattr__(self, attr):  # if you want to use '.'
        try:
            return self.__root__[attr]
        except KeyError as exc:
            raise AttributeError from exc

    def items(self):
        return self.__root__.items()


class App(BaseModel):
    title: str
    version: str
    prefix: Optional[str] = None
    description: Optional[str] = '' 


class HTTPBasicAuthn(BaseModel):
    authn_type: Literal[AuthnEnum.HTTPBasic] = AuthnEnum.HTTPBasic


class AsymmetricSecret(BaseModel):
    public_key_path: str
    private_key_path: str


class SymmetricSecret(BaseModel):
    secret: str


class OAuth2PasswordBearerAuthn(BaseModel):
    authn_type: Literal[AuthnEnum.OAuth2PasswordBearer] = \
        AuthnEnum.OAuth2PasswordBearer
    token_url: str = '/token'
    access_token_expire_minutes: int = 15


class LDAPAuthnBackend(BaseModel):
    authn_backend_type: Literal[AuthnBackendEnum.LDAP] = AuthnBackendEnum.LDAP
    bind_dn: str
    server: str


class Authn(BaseModel):
    authn: Union[HTTPBasicAuthn, OAuth2PasswordBearerAuthn]
    authn_backend: LDAPAuthnBackend


class Fastapi(BaseModel):
    app: App
    authn: Union[Authn, None] = None


class Database(BaseModel):
    connect_string: str


class Datarest(BaseModel):
    fastapi: Fastapi
    database: Database
    datatables: Datatables


class AppConfig(BaseModel):
    datarest: Datarest

# TODO: Design a saner API for setting authn configuration, including
# init-phase config checks (e.g. LDAP-based configs must ensure proper LDAP
# bind_dn + server settings, ...)
def app_config(
        table,
        title=None,
        version='0.1.0',
        prefix=None,
        description='',
        connect_string="sqlite:///app.db",
        expose_routes=(ExposeRoutesEnum.get_one, ),
        query_params=(),
        paginate=10,
        authn=None,
        authn_backend=None,
        ldap_bind_dn=None,
        ldap_server=None,
        ):
    """Return AppConfig object.
    """
   
    if prefix:
        # Normalize prefix
        prefix = '-'.join(prefix.lower().split()).strip('/')
        prefix = f'/{prefix}'

    expose_routes = list(expose_routes)

    authn_model = None
    if authn is not None:
        authn_frontend_model = None
        authn_backend_model = None

        if authn == AuthnEnum.HTTPBasic:
            authn_frontend_model = HTTPBasicAuthn()
        elif authn == AuthnEnum.OAuth2PasswordBearer:
            authn_frontend_model = OAuth2PasswordBearerAuthn()

        if authn_backend == AuthnBackendEnum.LDAP:
            authn_backend_model = LDAPAuthnBackend(
                bind_dn=ldap_bind_dn, server=ldap_server)

        authn_model = Authn(
            authn=authn_frontend_model, authn_backend=authn_backend_model)

    config = AppConfig(
        datarest=Datarest(
            fastapi=Fastapi(
                app=App(
                    title=title,
                    prefix=prefix,
                    description=description,
                    version=version,
                    ),
                authn=authn_model,
                ),
            database=Database(connect_string=connect_string, ),
            datatables=Datatables(
                __root__={
                    table:
                    TableschemaTable(
                        schema_spec=
                        "https://specs.frictionlessdata.io/data-resource/",
                        schema=f"{table}.yaml",
                        dbtable=table,
                        expose_routes=expose_routes,
                        query_params=query_params,
                        paginate=paginate
                        )
                    }
                ),
            )
        )
    return config


def write_app_config(cfg_path, app_config):
    """Write app.yaml config YAML string to cfg_path file.
    """
    app_config_yaml = yaml.safe_dump(
        #app_config.dict(by_alias=True, exclude_unset=True, exclude_none=True),
        app_config.dict(by_alias=True, exclude_none=True),
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        )
    with open(cfg_path, encoding='utf-8', mode='w') as cfg_file:
        cfg_file.write(app_config_yaml)


def read_app_config(cfg_path='app.yaml'):
    """Read app.yaml config YAML string from cfg_path file.

    Returns AppConfig model.
    """
    with open(cfg_path, 'rb') as config_file:
        dct = yaml.safe_load(config_file)
        config = AppConfig.parse_obj(dct)

    # If the description is a valid filename read description from there.
    # TODO: This is a bit hacky, since rewriting this config object would now
    # write the description text to app.yaml Do we care?
    description = config.datarest.fastapi.app.description
    if description and Path(description).is_file():
        with open(description) as description_file:
            description = description_file.read()

    config.datarest.fastapi.app.description = description 
    return config
