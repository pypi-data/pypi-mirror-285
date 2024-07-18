"""Altissimo API Class file."""
import datetime
import os

import jwt

from flask import abort
from flask import g
from flask import request


class API:
    """Altissimo API Class."""

    def __init__(self, auth_key=None):
        """Initialize an API object."""
        self.auth_header = None
        self.auth_key = auth_key
        self.auth_token = None
        self.auth_token_info = None

    def authorize_request(self):
        """Authorize an API request."""
        print("Checking Auth Header...")
        self.check_auth_header()
        print("Checking Auth Header Bearer...")
        self.check_auth_header_bearer()
        print("Checking Auth Token...")
        self.check_auth_token()
        print("Validating Auth Token...")
        self.validate_auth_token()
        return True

    def check_auth_header(self):
        """Check the auth header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            abort(401, "Required Authorization header not found.")
            return None
        self.auth_header = auth_header
        return auth_header

    def check_auth_header_bearer(self):
        """Check the auth header bearer."""
        if not self.auth_header.lower().startswith("bearer "):
            abort(401, "Invalid Authorization header. Bearer type required.")
            return None
        return True

    def check_auth_token(self):
        """Check the auth token."""
        auth_token = self.auth_header.split(" ")[1]
        if not auth_token:
            abort(401, "Required Bearer token not found.")
            return None
        self.auth_token = auth_token
        return auth_token

    def create_jwt(self, data, aud=None, iss=None, seconds=3600, sub=None):
        """Create a JWT."""
        payload = {
            "aud": aud,
            "exp": datetime.datetime.now() + datetime.timedelta(seconds=seconds),
            "iat": datetime.datetime.now(),
            "iss": iss,
            "nbf": datetime.datetime.now(),
            "sub": sub,
            "data": data,
        }
        return jwt.encode(payload, self.auth_key, algorithm="HS256")

    def validate_auth_token(
        self,
        algorithms=None,
        options=None,
        audience=None,
        issuer=None,
        leeway=None,
    ):
        """Validate the auth token (JWT)."""
        if not algorithms:
            algorithms = ["HS256"]
        if not leeway:
            leeway = 10
        if not options:
            options = {
                "require": ["exp", "iat", "nbf"],
                "verify_aud": False,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": False,
                "verify_nbf": True,
            }

        try:
            payload = jwt.decode(
                self.auth_token,
                self.auth_key,
                algorithms=algorithms,
                options=options,
                audience=audience,
                issuer=issuer,
                leeway=leeway,
            )
        except jwt.exceptions.ExpiredSignatureError:
            abort(401, "Token expired.")
            return None
        except jwt.exceptions.InvalidAudienceError:
            abort(401, "Invalid audience.")
            return None
        except jwt.exceptions.InvalidIssuerError:
            abort(401, "Invalid issuer.")
            return None
        except jwt.exceptions.MissingRequiredClaimError as e:
            abort(401, f"Missing required claim. [{e}]")
            return None
        except jwt.exceptions.InvalidTokenError:
            abort(401, "Invalid token.")
            return None

        if not payload:
            abort(401, "Invalid token. Missing payload.")
            return None

        data = payload.get("data", {})
        if not data:
            abort(401, "Invalid token. Missing data.")
            return None

        self.auth_token_info = payload

        return True
