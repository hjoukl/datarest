import pytest
import os
from unittest.mock import Mock
from fastapi.security import HTTPBasicCredentials

from datarest._cfgfile import TableschemaTable, ExposeRoutesEnum, SchemaSpecEnum, Datatables, AppConfig, Datarest, Fastapi, App, Database, write_app_config

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


# check if _httpbasic_scheme() returns an instance of AuthnScheme with the corrects attributes
def test_httpbasic_scheme(app_config_def):

    try:
        if not os.path.exists('app.yaml'):
            write_app_config('app.yaml', app_config_def)

        from datarest._authn import AuthnScheme, _httpbasic_scheme

        scheme = _httpbasic_scheme()
        assert isinstance(scheme, AuthnScheme)
        assert scheme.CredentialsType == HTTPBasicCredentials
    
    finally:
        os.remove('app.yaml')


def test_oauth2_passwordbearer_scheme_raises_notimplementederror():
    from datarest._authn import _oauth2_passwordbearer_scheme
    
    with pytest.raises(NotImplementedError):
        _oauth2_passwordbearer_scheme()


@pytest.mark.skip
def test_ldap_authentication_successful(app_config_def):

    try: 
        if not os.path.exists('app.yaml'):
            write_app_config('app.yaml', app_config_def)

        from datarest._authn import _ldap_authentication, _httpbasic_scheme

        # Create a mock LDAP configuration
        mock_ldap = Mock()
        mock_ldap.bind_dn = "dummy_bind_dn"
        mock_ldap.server = "ldap://dummy-server"

        mock_auth = Mock()
        mock_auth.authenticate.return_value = "username"
        
        authenticate_func = _ldap_authentication(
            ldap=mock_ldap,
            authn_scheme=_httpbasic_scheme()
        )
        
        credentials = HTTPBasicCredentials(username="user", password="pass")
        result = authenticate_func(credentials)
        assert result == "user"
    
    finally:
        os.remove('app.yaml')






    

