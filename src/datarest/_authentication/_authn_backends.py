import attrs
import ldap3
import functools
import ssl

from ._authn_exceptions import InvalidCredentialsError


# a helper to set proper ldap TLS 
_SSLServer = functools.partial(
    ldap3.Server, use_ssl=True, tls=ldap3.Tls(validate=ssl.CERT_REQUIRED))


@attrs.define
class LDAPAuthService:
    """LDAP authentication backend.

    Uses TLS for LDAP connection.

    Args:
        bind_dn: LDAP bind dn for user authentication ("login") against the
            LDAP server. The user name will be put into the {uid} placeholder.
        server: LDAP server name
    """
    bind_dn: str
    server: ldap3.Server = attrs.field(converter=_SSLServer)
    
    def authenticate(self, username, password):
        """Authenticate with given (user, password)-credentials.

        Args:
            username: user name to put into the LDAP bind dn {uid} placeholder
            password: LDAP password

        Returns:
            LDAP identity of the bound user
        """
        try:
            with ldap3.Connection(
                    self.server, self.bind_dn.format(uid=username), password,
                    auto_bind=True) as conn:
                return conn.extend.standard.who_am_i()
        except ldap3.core.exceptions.LDAPBindError as exc:
            raise InvalidCredentialsError from exc
