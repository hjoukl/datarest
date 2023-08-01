import pytest
import frictionless
import os
from fastapi import FastAPI
from fastapi.routing import APIRoute

from datarest._cfgfile import TableschemaTable, ExposeRoutesEnum, SchemaSpecEnum, Datatables, AppConfig, Datarest, Fastapi, App, Database, write_app_config

from datarest._models import create_models, ModelCombo

# global variable
generated_model_def = None

@pytest.fixture
def models_def():

    global generated_model_def
    if generated_model_def is not None:
        return generated_model_def

    # generate a test-model object and return it so that other test functions may use it
    data = [["id","name", "age", "income"],
        [1, "Patrick", 28, "3550.50"],
        [2, "Vivienne", 36, "2852.35"]]
    
    test_resource = frictionless.describe(data)
    test_resource.schema.primary_key.append("id")
    test_resource.schema.custom['x_datarest_primary_key_info'] = {
                    'id_type':'uuid4_base64',
                    'id_src_fields': ['id']
                    }
    
    test_resource.to_yaml("test.yaml")

    model_def = TableschemaTable(
        dbtable='test_table',
        paginate=10,
        expose_routes=[ExposeRoutesEnum.get_one], 
        query_params=[],
        schema_spec=SchemaSpecEnum.data_resource,
        schema="test.yaml",
    )

    datatables = Datatables(__root__={"test_table": model_def})
    models_def = create_models(datatables)

    # store model in global varibale
    generated_model_def = models_def

    return models_def


@pytest.fixture
def app_config_def():
    # create mock app_config
    app_config_def = AppConfig(datarest=Datarest(
        fastapi=Fastapi(
            app=App(
                title="Test API",
                description="Test Description",
                version="1.0.0",
                ),
                authn=None
            ),
        database=Database(
            connect_string="sqlite:///test.db",
        ),
        datatables=Datatables(__root__={
            "table1": TableschemaTable(
                schema_spec="https://specs.frictionlessdata.io/data-resource/",
                schema="test.yaml",
                dbtable="table1",
                expose_routes=[ExposeRoutesEnum.get_one],
            ),
        }),
    ))
    return app_config_def


@pytest.fixture
def app_def():

    # generate a default test_app
    app_def = FastAPI(title="test-app", description="test-app to check create_routes function", version=1.0)

    return app_def


def test_create_routes_default_routes(models_def, app_def, app_config_def):

    try:
        write_app_config('app.yaml', app_config_def)
        # import has to be done here, since create_routes triggers the _cfgfile.py-module which needs an app.yaml object
        from datarest._routes import create_routes

        create_routes(app_def, models_def)

        api_routes = [route for route in app_def.routes if isinstance(route, APIRoute)]

        assert '/test_table/{item_id}' == api_routes[0].path and {"GET"} == api_routes[0].methods

    finally:
        os.remove("test.yaml")
        os.remove("app.yaml")


def test_create_routes_multiple_routes(models_def, app_def, app_config_def):
    
    try:

        setattr(app_config_def.datarest.datatables.__dict__["__root__"]["table1"], "expose_routes", [ExposeRoutesEnum.get_one, 
                                                                                                    ExposeRoutesEnum.create, 
                                                                                                    ExposeRoutesEnum.delete_all, 
                                                                                                    ExposeRoutesEnum.delete_one,    
                                                                                                    ExposeRoutesEnum.get_all,    
                                                                                                    ExposeRoutesEnum.update,
                                                                                                    ])
        
        models_def['test_table'] = ModelCombo(
            resource_name='test_table',
            resource_model=models_def['test_table'].resource_model,
            resource_collection_model=models_def['test_table'].resource_collection_model,
            dbtable=models_def['test_table'].dbtable,
            id_columns=models_def['test_table'].id_columns,
            expose_routes=[ExposeRoutesEnum.get_one,
                        ExposeRoutesEnum.create, 
                        ExposeRoutesEnum.delete_all, 
                        ExposeRoutesEnum.delete_one, 
                        ExposeRoutesEnum.get_all, 
                        ExposeRoutesEnum.update],
            query_params=models_def["test_table"].query_params,
            paginate=models_def["test_table"].paginate,
            )
        
                                               
        write_app_config('app.yaml', app_config_def)
        # import has to be done here, since create_routes triggers the _cfgfile.py-module which needs an app.yaml object
        from datarest._routes import create_routes

        create_routes(app_def, models_def)

        api_routes = [route for route in app_def.routes if isinstance(route, APIRoute)]

         # Assertion 1: Check if the path and methods of the custom "get_one" route are correct
        get_one_route = next(route for route in api_routes if route.path == '/table1/{item_id}' and "GET" in route.methods)
        assert get_one_route is not None

        # Assertion 2: Check if the path and methods of the custom "create" route are correct
        create_route = next(route for route in api_routes if route.path == '/table1' and "POST" in route.methods)
        assert create_route is not None

        # Assertion 3: Check if the path and methods of the custom "delete_all" route are correct
        delete_all_route = next(route for route in api_routes if route.path == '/table1' and "DELETE" in route.methods)
        assert delete_all_route is not None

        # Assertion 4: Check if the path and methods of the custom "delete_one" route are correct
        delete_one_route = next(route for route in api_routes if route.path == '/table1/{item_id}' and "DELETE" in route.methods)
        assert delete_one_route is not None

        # Assertion 5: Check if the path and methods of the custom "get_all" route are correct
        get_all_route = next(route for route in api_routes if route.path == '/table1' and "GET" in route.methods)
        assert get_all_route is not None

        # Assertion 6: Check if the path and methods of the custom "update" route are correct
        update_route = next(route for route in api_routes if route.path == '/table1/{item_id}' and "PUT" in route.methods)
        assert update_route is not None


    finally:
        os.remove("app.yaml")