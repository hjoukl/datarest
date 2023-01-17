# Use fastapi_crudrouter to generate router endpoints

from fastapi import Depends, Response, status

from . import _crudrouter_ext
from . import _database


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

    def resp_status_code(response: Response):
        response.status_code = http_code
        return response

    return resp_status_code


# TODO:
# - Use PATCH instead of PUT for update(?)
def create_routes(app, models):
    """Create fastapi_crudrouter.SQLAlchemyCRUDRouter objects for the models
    and register the routers with the main FastAPI app.
    """
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
            query_params=model.query_params,
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
        app.include_router(router)
