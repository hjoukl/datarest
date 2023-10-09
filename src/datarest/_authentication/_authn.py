from fastapi import FastAPI

from .._cfgfile import Authn, AuthnBackendEnum, AuthnEnum
from ._authn_backends import LDAPAuthService
from ._authn_frontends import http_basic_auth, oauth2_passwordbearer_auth
from ._authn_exceptions import InvalidCredentialsError
from ._authn_common import Authentication


authn_frontend_factories = {
    AuthnEnum.HTTPBasic: http_basic_auth,
    AuthnEnum.OAuth2PasswordBearer: oauth2_passwordbearer_auth,
    }


authn_backends = {
    AuthnBackendEnum.LDAP: LDAPAuthService,
    }


# Hack: The prefix parameter is needed due to FastAPI not properly respecting a
# router URL prefix wrt an OAuth2PasswordRequestForm, as it seems.
# For now, provide the URL prefix (used for putting all service endpoints under
# a common "API/Service name" prefix) and prepend it manually.
def from_config(
        app: FastAPI, authn_config: Authn, prefix=''
        ) -> Authentication:
    """Create an return an authentication setup according to the given
    configuration.
    """
    backend_config = authn_config.authn_backend
    AuthnBackend = authn_backends[backend_config.authn_backend_type]
    authn_backend = AuthnBackend(
        **backend_config.dict(exclude={'authn_backend_type'})
        )

    frontend_config = authn_config.authn
    authentication = authn_frontend_factories[frontend_config.authn_type](
        authn_backend=authn_backend,
        app=app,
        prefix=prefix,
        **dict(frontend_config)
        )
    return authentication
