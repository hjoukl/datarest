# The app configuration defined as a pydantic model, plus some helpers.

import enum
from typing import Dict, List, Optional, Union
from typing_extensions import Annotated, Literal

import yaml
from pydantic import BaseModel, Field

from . import _yaml_tools


class StrEnum(str, enum.Enum):
    """String enum base class provide actual string value in str(...) output.

    Overrides the default IdEnum.xxx output of the Enum class.
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
    HTTPBasic_LDAP = 'HTTPBasic+LDAP'
    OAuth2PasswordBearer_LDAP = 'OAuth2PasswordBearer+LDAP'


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
    description: Optional[str] = ""
    version: str


class LDAP(BaseModel):
    bind_dn: str
    server: str


class Authn(BaseModel):
    authn_type: AuthnEnum
    ldap: Optional[LDAP] = None


class Fastapi(BaseModel):
    app: App
    authn: Optional[Authn] = None


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
        description='',
        version='0.1.0',
        connect_string="sqlite:///app.db",
        expose_routes=(ExposeRoutesEnum.get_one, ),
        query_params=(),
        authn_type=None,
        ldap_bind_dn=None,
        ldap_server=None,
        ):
    """Return AppConfig object.
    """
    title = table if title is None else title

    authn = None
    ldap = None
    if authn_type is not None:
        # Using or here catches a missing ldap attribute, at least
        if ldap_bind_dn is not None or ldap_server is not None:
            ldap = LDAP(
                bind_dn=ldap_bind_dn,
                server=ldap_server,
                )
        authn = Authn(
            authn_type=authn_type,
            ldap=ldap
            )
    # expose_routes = list(expose_routes)
    config = AppConfig(
        datarest=Datarest(
            fastapi=Fastapi(
                app=App(
                    title=f"{title} API",
                    description=description,
                    version=version,
                    ),
                authn=authn,
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
        app_config.dict(by_alias=True, exclude_unset=True, exclude_none=True),
        default_flow_style=False,
        sort_keys=False
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
    return config
