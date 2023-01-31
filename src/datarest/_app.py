# stdlib imports
import sys

# dependencies import
from fastapi import FastAPI, APIRouter

# local imports
from . import _authn
from . import _models
from . import _routes
from ._app_config import config


# Create main FastAPI app with given configuration.
fastapi_config = config.datarest.fastapi

app = FastAPI(
    title=fastapi_config.app.title,
    description=fastapi_config.app.description,
    version=fastapi_config.app.version)

dependencies = []
responses = {}
if fastapi_config.authn is not None:
    # Add proper FastAPI auth dependencies if authentication is configured. 
    authn_dependencies = _authn.create_authn(fastapi_config.authn)
    dependencies.extend(authn_dependencies)
    # Set up additional 401 responses so that it shows up in OpenAPI docs.
    responses.update({
        '401': {"description": "Unauthorized"},
        })

# Create the API/ORM data models.
models = _models.create_models(config.datarest.datatables)

# Create FastAPI app routes using CRUDRouter.
_routes.create_routes(
    app=app,
    models=models,
    dependencies=dependencies,
    responses=responses,
    )
