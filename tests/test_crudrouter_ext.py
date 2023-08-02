import pytest
import frictionless
import os
from pydantic import Field
from typing import Type, List
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi_crudrouter.core.sqlalchemy import SCHEMA

from datarest._crudrouter_ext import FilteringSQLAlchemyCRUDRouter, query_factory
from datarest._data_resource_models import create_model_from_tableschema




# global variable
generated_model = None

@pytest.fixture
def model():

    global generated_model
    if generated_model is not None:
        return generated_model

    data = [["id","name", "age", "income"],
        [1, "Patrick", 28, "3550.50"],
        [2, "Vivienne", 36, "2852.35"]]
    
    test_resource = frictionless.describe(data)
    test_resource.schema.primary_key.append("id")
    test_resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type':'uuid4_base64',
                    'id_src_fields': ['id']
                    }
    (id_columns, model) = create_model_from_tableschema('TestModel', test_resource.schema)

    # store model in global varibale
    generated_model = model

    return model

@pytest.fixture
def query_params():
    query_params = ['name', 'age']

    return query_params

@pytest.fixture
def router(model, query_params):

    Base = declarative_base()

    class MyModel(Base):
        __tablename__ = "testmodel"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)
        income = Column(Float)

    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app = FastAPI()

    router = FilteringSQLAlchemyCRUDRouter(
    schema=model,
    db_model=MyModel,
    db=TestingSessionLocal,
    query_params=query_params,
    response_model_exclude_none=True,
)
    return router


# check if query_params are set
def test_query_factory(model, query_params):

    query = query_factory(model, query_params)

    assert query is not None
    assert hasattr(query, 'age') == True
    assert hasattr(query, 'name') == True


# no query_params are given
def test_query_factory_empty_params(model):

    query = query_factory(model)
    assert query is None


# invalid field as query_param -> TO-DO: Add Exception-Handling when a query-parameter doesn't exist in the dataset
@pytest.mark.skip
def test_query_factory_invalid_query_params(model):

    invalid_params = ['invalid_field', 'age']
    query = query_factory(model, invalid_params)
    
    assert query is None


def test_filtering_sqlalchemy_crud_router(router):

    try:
        # check if query_params are set accordingly
        assert 'name' in router.filter_params_cls.__dict__.keys()
        assert 'age' in router.filter_params_cls.__dict__.keys()

        assert router.response_model_exclude_none is True

    finally:
        os.remove("test.db")


    # TO-DO: Check responses from server

    """
    app.include_router(router)
    client = TestClient(app)

    # test get_all method
    with TestingSessionLocal() as session:

        # Test data
        data = [
            MyModel(name="Patrick", age=28, income="3550.50"),
            MyModel(name="Vivienne", age=36, income="2852.35"),
        ]
        
        session.add_all(data)
        session.commit()

        url = "/testmodel/"
        response = client.get(url)

        breakpoint()

        assert response.status_code == 200
        results = response.json()
        assert len(results) == len(data)
    """
