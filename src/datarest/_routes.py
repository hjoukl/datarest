# Use fastapi_crudrouter to generate router endpoints

import enum
import functools
import io
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field
import yaml

from . import _crudrouter_ext
from . import _database


# TODO: Use pydantic generic models here to avoid duplication?
class HealthOkEnum(str, enum.Enum):
    UP = "UP"
    UNKNOWN = "UNKNOWN"


class HealthErrorEnum(str, enum.Enum):
    DOWN = "DOWN"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class HealthOkResponse(BaseModel):
    status: HealthOkEnum = Field(
        description='API status', example=HealthOkEnum.UP)
    components: Optional[dict] = Field(
        None, desciption='Optional additional health info')


class HealthErrorResponse(BaseModel):
    status: HealthErrorEnum = Field(
        description='API status', example=HealthErrorEnum.DOWN)
    components: Optional[dict] = Field(
        None, desciption='Optional additional health info')


health_responses = {
    status.HTTP_200_OK: {
        'model': HealthOkResponse,
        'description': 'Health responses',
        },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        'model': HealthErrorResponse,
        'description':  'Health error responses',
        },
    }


class AppInfo(BaseModel):
    version: str


class InfoResponse(BaseModel):
    app: AppInfo


# Disallow all routes per default to allow for selectively enabling routes
expose_routes_default = {
    'get_all_route': False,
    'get_one_route': False,
    'delete_all_route': False,
    'delete_one_route': False,
    'create_route': False,
    'update_route': False,
    }


# TODO: Better move the custom status setting to crudrouter subclass, since we
# have one, anyway, for query support.
# Customize some CRUDRouter status code defaults since they're suboptimal
custom_routes_status = {
    'create': status.HTTP_201_CREATED,
    }


def status_code(http_code: int = status.HTTP_200_OK):
    """Dependency function factory: Return a callable that takes a Response arg
    and sets the response status.
    """
    def resp_status_code(response: Response):
        response.status_code = http_code
        return response

    return resp_status_code


# TODO:
# - Use PATCH instead of PUT for update(?)
def crud_routers(models, dependencies=None, responses=None):
    """Create fastapi_crudrouter.SQLAlchemyCRUDRouter objects for the models
    and register the routers with the main FastAPI app.
    """
    routers = []
    for (model_name, model) in models.items():
        expose_routes = dict(expose_routes_default)
        for expose in model.expose_routes:
            route_arg = True
            custom_status = custom_routes_status.get(expose)
            # Use a custom http response status by means of dependency
            if custom_status:
                route_arg = [Depends(status_code(custom_status))]
            expose_routes[f"{expose}_route"] = route_arg

        router = _crudrouter_ext.FilteringSQLAlchemyCRUDRouter(
            schema=model.resource_model,
            db_model=model.resource_model,
            db=_database.get_db,
            prefix=model.resource_name,
            paginate=model.paginate,
            dependencies=dependencies,
            query_params=model.query_params,
            responses=responses,
            **expose_routes
            )
        # TODO:
        # To make our custom response status codes show up in the OAS docs, we
        # need to modify the route objects here, since there's no way to set
        # it properly, in the CRUDRouter constructor.
        # Remove this brittle monkeypatching:
        # - CRUDRouter should set proper route names (through _add_api_route())
        # - CRUDRouter should get support for proper status_code setting
        #   (see also https://github.com/awtkns/fastapi-crudrouter/pull/151,
        #    though I'd prefer a more general approach, maybe with kwargs)
        for route in router.routes:
            if 'POST' in route.methods:
                route.status_code = custom_routes_status.get('create')
            elif 'PUT' in route.methods:
                route.status_code = custom_routes_status.get('update')
        routers.append(router)
    return routers


def health_info_routers(version, models, check_tables=None):
    """Set up the /health and /info API endpoints.

    Returns:
        list[APIRouter]: FastAPI router(s) for app inclusion
    """
    # Create our APIRouter instance that will carry the GET endpoints.
    router = APIRouter()

    # Determine the actual DB queries that shall be checked for healthiness.
    if check_tables is None:
        # The default is to check all modelled database tables.
        check_db_models = [
            model_combo.resource_model for model_combo in models.values()
            ]
    else:
        # Get the model objects to use for health check DB queries, filtered by
        # their names given in check_tables.
        # TODO: Don't let erroneous setup go unnoticed here but this must also
        # be checked at init time!
        try:
            check_db_models = [
                models[table_name] for table_name in check_tables
                ]
        except IndexError as exc:
            raise ValueError(
                f'Not all defined health check tables {check_tables} found in '
                f'DB models ({exc})') from exc

    query_checks = len(check_db_models)

    @router.get('/health', response_model=HealthOkResponse,
                responses=health_responses)
    async def get_health(db: _database.Session=Depends(_database.get_db)):
        if query_checks:
            components = {
                'db': {
                    'queries': {
                        'checks': query_checks,
                        'success': 0,
                        }
                    }
                }
            queries = components['db']['queries']
            for idx, table_model in enumerate(check_db_models):
                count = db.query(table_model).count()
                queries['success'] += 1
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={
                    'status': 'UP',
                    'components': components,
                    }
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={'status': 'UP'})


    @router.get('/info', response_model=InfoResponse)
    async def get_info():
        return InfoResponse(app=AppInfo(version=version))

    return [router]


def oas_router(app, openapi_yaml_url='/openapi.yaml'):
    """Create a router with an additional endpoint to load the OpenAPI API
    definition as a YAML file.
    
    Returns:
        APIRouter: FastAPI router for app inclusion
    """
    router = APIRouter()
  
    # Hook additional yaml version of openapi.json at this endpoint. lru_cache
    # mimicks the  app.openapi() once-only schema generation for the
    # json-to-yaml conversion.
    @router.get(openapi_yaml_url, include_in_schema=False)
    @functools.lru_cache()
    def read_openapi_yaml() -> Response:
        # Retrieve the JSON OAS representation.
        openapi_json = app.openapi()
        yaml_s = io.StringIO()
        yaml.safe_dump(
            openapi_json, yaml_s,
            default_flow_style=False, allow_unicode=True, sort_keys=False
            )
        return Response(yaml_s.getvalue(), media_type='text/yaml')
    
    return router
