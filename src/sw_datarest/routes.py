# using fastapi_crudrouter to generate router endpoints 
from fastapi_crudrouter import SQLAlchemyCRUDRouter as CRUDRouter
from . import database

def create_routes(app, models):
    """When generating routes, the SQLAlchemyCRUDRouter will 
    automatically tie into the database using SQLAlchemy models.
    """
    for (model_name, model) in models.items():
        router = CRUDRouter(
            schema=model.resource_model,
            create_schema=model.resource_model,
            db_model=database.get_table_cls(model.dbtable),
            db=database.get_db,
            prefix=model.resource_name
            )
        #includes router in app
        app.include_router(router)           


