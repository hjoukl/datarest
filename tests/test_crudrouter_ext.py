import pytest
import frictionless
from typing import Type
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datarest._crudrouter_ext import FilteringSQLAlchemyCRUDRouter, query_factory
#from models import Base, Item

@pytest.fixture
def schema():

    data = [["id","name", "age", "income"],
        [1, "Patrick", 28, "3550.50"],
        [2, "Vivienne", 36, "2852.35"]]
    
    test_resource = frictionless.describe(data)
    
    return test_resource.schema

@pytest.fixture
def query_params():
    query_params = ["id", "name"]

    return query_params

def test_query_factory(schema, query_params):
    # Test that the function returns the expected query for a given filter
    breakpoint()
    query = query_factory(Type(schema), query_params)

    # query-factory wird kein "normales" schema übergeben -> schema: Type[SCHEMA]
        # wie lässt sich das auf gerneric schema übertragen?
    
    

"""
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app = FastAPI()

app.include_router(
    FilteringSQLAlchemyCRUDRouter(
        schema=Item,
        db_model=Item,
        db=TestingSessionLocal(),
        query_params=["name", "description", "price"],
        prefix="/items",
        tags=["items"],
    )
)


client = TestClient(app)


def test_create_item():
    item_data = {"name": "test", "description": "testing", "price": 1.0}
    response = client.post("/items/", json=item_data)
    assert response.status_code == 201
    item = response.json()
    assert "id" in item
    for key in item_data:
        assert item_data[key] == item[key]


def test_get_all_items():
    response = client.get("/items/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1


def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    item = response.json()
    assert item["name"] == "test"


def test_update_item():
    item_data = {"name": "updated", "description": "updated", "price": 2.0}
    response = client.put("/items/1", json=item_data)
    assert response.status_code == 200
    item = response.json()
    for key in item_data:
        assert item_data[key] == item[key]


def test_delete_item():
    response = client.delete("/items/1")
    assert response.status_code == 204
    response = client.get("/items/1")
    assert response.status_code == 404

"""