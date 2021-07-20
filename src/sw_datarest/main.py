# main.py
# stdlib imports
import sys

# dependencies import
from fastapi import FastAPI

# local imports
from .app_config import config
from . import models
from . import routes


# main app
fastapi_config = config.datarest.fastapi
#create the API with config attitutdes 
app = FastAPI(
    title=fastapi_config.app.title,
    description=fastapi_config.app.description,
    version=fastapi_config.app.version)

#assign pydantic model to app_models
app_models = models.create_pydantic_models(config)
#create the function to execute CRUD-Operations
routes.create_routes(app, app_models)


def main():
    """starts uvicorn server
    Returns: function to start uvicorn server + commandline arguments passed to the script
    """
    import uvicorn
    import sys
    return uvicorn.main(['sw_datarest.main:app'] + sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())

