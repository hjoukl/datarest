# The app configuration defined as a pydantic model, plus some helpers.

import enum
from typing import Dict, List, Optional, Union
from typing_extensions import Annotated, Literal

import attrdict
import yaml
from pydantic import BaseModel, Field

from . import _yaml_tools


@_yaml_tools.dump_as_str
@enum.unique
class ExposeRoutesEnum(str, enum.Enum):
    """Enumeration of exposable endpoints.
    """
    get_all = 'get_all'
    get_one = 'get_one'
    delete_all = 'delete_all'
    delete_one = 'delete_one'
    create = 'create'
    update = 'update'

    def __str__(self):
        # Avoid IdEnum.xxx output of Enum class, provide actual string value
        return self.value


@_yaml_tools.dump_as_str
class SchemaSpecEnum(str, enum.Enum):
    """Enumeration of the supported schema specifications.
    """
    sqlalchemy = "https://www.sqlalchemy.org/"
    data_resource = "https://specs.frictionlessdata.io/data-resource/"
    
    def __str__(self):
        # Avoid IdEnum.xxx output of Enum class, provide actual string value
        return self.value


class SQLAlchemyTable(BaseModel):
    schema_spec: Literal[SchemaSpecEnum.sqlalchemy]
    dbtable: str
    paginate: int = 10
    expose_routes: Optional[List[ExposeRoutesEnum]] = [
        ExposeRoutesEnum.get_one]


class TableschemaTable(BaseModel):
    schema_spec: Literal[SchemaSpecEnum.data_resource]
    # schema is used by pydantic so work with an alias
    schema_: str = Field(..., alias='schema')
    dbtable: str
    paginate: int = 10
    expose_routes: Optional[List[ExposeRoutesEnum]] = [
        ExposeRoutesEnum.get_one]


Table =  Annotated[
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


class Fastapi(BaseModel):
    app: App


class Database(BaseModel):
    connect_string: str


class Datarest(BaseModel):
    fastapi: Fastapi
    database: Database
    datatables: Datatables


class AppConfig(BaseModel):
    datarest: Datarest


def app_config(
        table, title=None, description='', version='0.1.0',
        connect_string="sqlite:///app.db",
        expose_routes=(ExposeRoutesEnum.get_one,)):
    """Return AppConfig object.
    """
    title = table if title is None else title
    #expose_routes = list(expose_routes)
    config = AppConfig(datarest=Datarest(
        fastapi=Fastapi(
            app=App(
                title=f"{title} API",
                description=description,
                version=version,
                )
            ),
        database=Database(
            connect_string=connect_string,
            ),
        datatables=Datatables(__root__={
            table: TableschemaTable(
                schema_spec="https://specs.frictionlessdata.io/data-resource/",
                schema=f"{table}.yaml",
                dbtable=table,
                expose_routes=expose_routes,
                )
            }),
        ))
    return config


def write_app_config(cfg_path, app_config):
    """Write app.yaml config YAML string to cfg_path file.
    """
    app_config_yaml = yaml.safe_dump(
        app_config.dict(by_alias=True), default_flow_style=False,
        sort_keys=False)
    with open(cfg_path, encoding='utf-8', mode='w') as cfg_file:
        cfg_file.write(app_config_yaml)


def read_app_config(cfg_path='app.yaml'):
    """Read app.yaml config YAML string from cfg_path file.

    Returns attrdict.AttrDict object.
    """
    with open(cfg_path, 'rb') as config_file:
        dct = yaml.safe_load(config_file)
        config = AppConfig.parse_obj(dct)
    return config
