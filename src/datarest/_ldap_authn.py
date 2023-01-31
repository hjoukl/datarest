import attr
import ldap3
import functools
import ssl


InvalidCredentialsError = ldap3.core.exceptions.LDAPBindError


# a helper to set proper ldap TLS 
_SSLServer = functools.partial(
    ldap3.Server, use_ssl=True, tls=ldap3.Tls(validate=ssl.CERT_REQUIRED))


@attr.s
class LDAPAuth:
    """LDAP (user, password) authentication.

    Uses TLS for LDAP connection.

    Args:
        bind_dn: LDAP bind dn for user authentication ("login") against the
            LDAP server. The username is put into the {uid} placeholder.
        server: LDAP server name
    """
    bind_dn: str = attr.ib()
    server: ldap3.Server = attr.ib(converter=_SSLServer)
    
    def authenticate(self, username, password):
        """Authenticate with given credentials.

        Returns:
            LDAP identity of the bound user
        """
        with ldap3.Connection(
                self.server, self.bind_dn.format(uid=username), password,
                auto_bind=True) as conn:
            return conn.extend.standard.who_am_i()
