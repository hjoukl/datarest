import pytest

from fastapi import FastAPI

from datarest._routes import create_routes, expose_routes_default
from datarest._database import get_db
from datarest._app import app, models


# Wie lässt sich hier ein Test aufsetzen -> App, Database und Model hier neu formulieren und darauf die Routen testen?
# gerneric app und generic model übergeben und testen ob router in app inkkludiert ist
# routes checken
# muss echtes fastapi-objekt übergeben werden?