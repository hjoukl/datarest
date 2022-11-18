# stdlib imports
import sys

# dependencies import
from fastapi import FastAPI

# local imports
from . import _models
from . import _routes
from ._app_config import config


# Create main FastAPI app with given configuration
fastapi_config = config.datarest.fastapi

app = FastAPI(
    title=fastapi_config.app.title,
    description=fastapi_config.app.description,
    version=fastapi_config.app.version)

models = _models.create_models(config.datarest.datatables)

# Creata FastAPI app routes using CRUDRouter
_routes.create_routes(app, models)
