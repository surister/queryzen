import pytest

from queryzen import exceptions, QueryZen


def test_instantiate_queryzen_client_without_valid_credentials(queryzen):
    """
    Test that instantiating a QueryZen client without a valid credentials raises an exception.
    All operations must proceed through queryzen client so if auth failed here, the client won't be authorized.
    """
    with pytest.raises(exceptions.AuthenticationError):
        QueryZen(user='bad-email@test.com', password='test')

