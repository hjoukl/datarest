# stdlib imports
import sys

# dependencies import
from fastapi import Depends, FastAPI, APIRouter

# local imports
from . import _models
from . import _routes
from ._app_config import config


# Create main FastAPI app with given configuration.
fastapi_config = config.datarest.fastapi
prefix = fastapi_config.app.prefix or ''

app = FastAPI(
    title=fastapi_config.app.title,
    description=fastapi_config.app.description,
    version=fastapi_config.app.version,
    docs_url=f'{prefix}/docs',
    redoc_url=f'{prefix}/redoc',
    openapi_url=f'{prefix}/openapi.json',
    )

# Create the API/ORM data models.
models = _models.create_models(config.datarest.datatables)

# Add-ons:
# Prepare additional dependencies for authentication, additional response
# models to hand over to CRUDRouter.
dependencies = []
responses = {}

if fastapi_config.authn is not None:
    from ._authentication import _authn 
    # Add proper FastAPI auth dependencies if authentication is configured.
    authentication = _authn.from_config(
        app=app, authn_config=fastapi_config.authn, prefix=prefix)

    # Add authentication dependencies to the CRUDRouter dependencies.
    dependencies.extend(authentication.dependencies)

    # Add the authentication's custom routers to the main app, if any.
    for router in authentication.routers:
        app.include_router(router, tags=['Authentication'], prefix=prefix)

    # Set up additional 401 responses so that it shows up in OpenAPI docs.
    responses.update({
        '401': {"description": "Unauthorized"},
        })

# Create FastAPI app routes.
# using CRUDRouter.
crud_routers = _routes.crud_routers(
    models=models,
    dependencies=dependencies,
    responses=responses,
    )
health_info_routers = _routes.health_info_routers(
    version=fastapi_config.app.version,
    models=models
    )

for router in crud_routers:
    app.include_router(router, prefix=prefix)

for router in health_info_routers:
    app.include_router(
        router, tags=['Health'], prefix=prefix)

# TODO: Make /openapi.yaml URL configurable.
oas_router = _routes.oas_router(app)
app.include_router(oas_router, prefix=prefix)

