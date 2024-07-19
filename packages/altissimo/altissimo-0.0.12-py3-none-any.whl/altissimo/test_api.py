"""Altissimo API Tests file."""
import jwt
# import pytest
# import werkzeug.exceptions

from .api import API
import altissimo.api


class Request:

    def __init__(self, headers):
        self.headers = headers


audience = "https://audience"
issuer = "auth@altissimo.io"
secret_key = "randomsecretkey"
auth_token = API(secret_key).create_jwt(
    {"user": {}},
    aud=audience,
    iss=issuer,
)
empty_auth_token = jwt.encode({}, secret_key, algorithm="HS256")
dataless_auth_token = API(secret_key).create_jwt({})
expired_auth_token = API(secret_key).create_jwt({"user": {}}, seconds=-3600)
invalid_auth_token = "abcdefg"

auth_header = {"Authorization": f"Bearer {auth_token}"}
bad_auth_header = {"Authorization": "Bacon "}
dataless_auth_header = {"Authorization": f"Bearer {dataless_auth_token}"}
empty_auth_header = {"Authorization": f"Bearer {empty_auth_token}"}
expired_auth_header = {"Authorization": f"Bearer {expired_auth_token}"}
invalid_auth_header = {"Authorization": f"Bearer {invalid_auth_token}"}


def test_authorize_request(mocker):
    """Test authorize_request."""
    a = API(secret_key)
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.authorize_request() is True
    mocked_abort.assert_not_called()


def test_check_auth_header(mocker):
    """Test check_auth_header."""
    a = API()
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == request.headers["Authorization"]
    mocked_abort.assert_not_called()


def test_check_auth_header_missing(mocker):
    """Test check_auth_header with missing header."""
    a = API()
    request = Request({})
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() is None
    mocked_abort.assert_called_once_with(401, "Required Authorization header not found.")


def test_check_auth_header_bearer(mocker):
    """Test check_auth_header_bearer."""
    a = API()
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header()
    assert a.check_auth_header_bearer() is True
    mocked_abort.assert_not_called()


def test_check_auth_header_bearer_missing(mocker):
    """Test check_auth_header_bearer with missing bearer."""
    a = API()
    request = Request(bad_auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header()
    assert a.check_auth_header_bearer() is None
    mocked_abort.assert_called_once_with(401, "Invalid Authorization header. Bearer type required.")


def test_check_auth_token(mocker):
    """Test check_auth_token."""
    a = API()
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header()
    assert a.check_auth_token() == auth_token
    mocked_abort.assert_not_called()


def test_check_auth_token_missing(mocker):
    """Test check_auth_token with missing token."""
    a = API()
    request = Request(bad_auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header()
    assert a.check_auth_token() is None
    mocked_abort.assert_called_once_with(401, "Required Bearer token not found.")


def test_validate_auth_token(mocker):
    """Test validate_auth_token."""
    a = API(secret_key)
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header()
    assert a.check_auth_token() == auth_token
    assert a.validate_auth_token() is True
    mocked_abort.assert_not_called()


def test_validate_auth_token_expired(mocker):
    """Test validate_auth_token for expired token."""
    a = API(secret_key)
    request = Request(expired_auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == expired_auth_header["Authorization"]
    assert a.check_auth_token() == expired_auth_token
    assert a.validate_auth_token() is None
    mocked_abort.assert_called_once_with(401, "Token expired.")


def test_validate_auth_token_invalid(mocker):
    """Test validate_auth_token for invalid token."""
    a = API(secret_key)
    request = Request(invalid_auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == invalid_auth_header["Authorization"]
    assert a.check_auth_token() == invalid_auth_token
    assert a.validate_auth_token() is None
    mocked_abort.assert_called_once_with(401, "Invalid token.")


def test_validate_auth_token_audience(mocker):
    """Test validate_auth_token incorrect audience."""
    a = API(secret_key)
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == auth_header["Authorization"]
    assert a.check_auth_token() == auth_token
    assert a.validate_auth_token(
        audience="http://example.net",
        options={
            "require": ["aud"],
            "verify_aud": True,
        },
    ) is None
    mocked_abort.assert_called_once_with(401, "Invalid audience.")


def test_validate_auth_token_empty(mocker):
    """Test validate_auth_token for no payload."""
    a = API(secret_key)
    request = Request(empty_auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == empty_auth_header["Authorization"]
    assert a.check_auth_token() == empty_auth_token
    assert a.validate_auth_token(options={"require": []}) is None
    mocked_abort.assert_called_once_with(401, "Invalid token. Missing payload.")


def test_validate_auth_token_issuer(mocker):
    """Test validate_auth_token invalid issuer."""
    a = API(secret_key)
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == auth_header["Authorization"]
    assert a.check_auth_token() == auth_token
    assert a.validate_auth_token(
        issuer="invalid-issuer",
        options={
            "require": ["iss"],
            "verify_iss": True,
        },
    ) is None
    mocked_abort.assert_called_once_with(401, "Invalid issuer.")


def test_validate_auth_token_missing_claim(mocker):
    """Test validate_auth_token missingd claim."""
    a = API(secret_key)
    request = Request(auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == auth_header["Authorization"]
    assert a.check_auth_token() == auth_token
    assert a.validate_auth_token(
        options={
            "require": ["sub"],
        },
    ) is None
    mocked_abort.assert_called_once_with(401, "Missing required claim. [Token is missing the \"sub\" claim]")


def test_validate_auth_token_missing_data(mocker):
    """Test validate_auth_token missingd data."""
    a = API(secret_key)
    request = Request(dataless_auth_header)
    mocker.patch.object(altissimo.api, "request", request)
    mocked_abort = mocker.patch.object(altissimo.api, "abort")
    assert a.check_auth_header() == dataless_auth_header["Authorization"]
    assert a.check_auth_token() == dataless_auth_token
    assert a.validate_auth_token() is None
    mocked_abort.assert_called_once_with(401, "Invalid token. Missing data.")
