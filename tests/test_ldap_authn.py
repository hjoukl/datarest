import pytest
from unittest.mock import Mock

from datarest._ldap_authn import LDAPAuth, InvalidCredentialsError


def test_ldap_authentication_successful():
    # Mock the LDAPAuth class
    mock_ldap_class = Mock(LDAPAuth)
    mock_ldap_instance = mock_ldap_class.return_value
    
    # Configure the mock instance
    mock_ldap_instance.authenticate.return_value = "uid=testuser,ou=users,dc=example,dc=com"
    
    # Call the method under test
    result = mock_ldap_instance.authenticate("testuser", "password")
    
    assert result == "uid=testuser,ou=users,dc=example,dc=com"


def test_ldap_authentication_failed():
    # Mock the LDAPAuth class and instance
    mock_ldap_class = Mock(LDAPAuth)
    mock_ldap_instance = mock_ldap_class.return_value
        
    # Configure the mock instance for failed authentication
    mock_ldap_instance.authenticate.side_effect = InvalidCredentialsError
        
    with pytest.raises(InvalidCredentialsError):
        mock_ldap_instance.authenticate("testuser", "wrong_password")


def test_create_ldap_auth_instance():
    # Call the function to create an LDAPAuth instance
    ldap_auth_instance = LDAPAuth("uid={},ou=users,dc=example,dc=com", "ldap://mock-server")
    
    # Check if an instance was created
    assert isinstance(ldap_auth_instance, LDAPAuth)
    assert ldap_auth_instance.bind_dn == "uid={},ou=users,dc=example,dc=com"
    assert ldap_auth_instance.server.host == "mock-server"





    

