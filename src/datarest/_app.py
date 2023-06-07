# stdlib imports
import sys

# dependencies import
from fastapi import Depends, FastAPI, APIRouter

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

# Create the API/ORM data models.
models = _models.create_models(config.datarest.datatables)

# Add-ons:
# additional dependencies for authentication, additional response models
dependencies = []
responses = {}

if fastapi_config.authn is not None:
    # Add proper FastAPI auth dependencies if authentication is configured. 
    authn_dependencies = _authn.create_authn(fastapi_config.authn)
    # Wrap authn dependency callables with Depends() for FastAPI dependency
    # injection.
    dependencies.extend(
        Depends(authn_dep) for authn_dep in authn_dependencies)
    # Set up additional 401 responses so that it shows up in OpenAPI docs.
    responses.update({
        '401': {"description": "Unauthorized"},
        })

# Create FastAPI app routes using CRUDRouter.
_routes.create_routes(
    app=app,
    models=models,
    dependencies=dependencies,
    responses=responses,
    )
