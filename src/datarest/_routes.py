# Use fastapi_crudrouter to generate router endpoints 

from fastapi_crudrouter import SQLAlchemyCRUDRouter as CRUDRouter
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


# TODO:
# - POST -> 201 Created
# - Use PATCH instead of PUT for update

def create_routes(app, models):
    """Create fastapi_crudrouter.SQLAlchemyCRUDRouter objects for the models
    and register the routers with the main FastAPI app.
    """
    for (model_name, model) in models.items():
        expose_routes = dict(expose_routes_default)
        expose_routes.update(
            {
                f"{expose}_route": True
                for expose in model.expose_routes
            })
        router = CRUDRouter(
            schema=model.resource_model,
            db_model=model.resource_model,
            db=_database.get_db,
            prefix=model.resource_name,
            paginate=model.paginate,
            **expose_routes
            )
        app.include_router(router)           
