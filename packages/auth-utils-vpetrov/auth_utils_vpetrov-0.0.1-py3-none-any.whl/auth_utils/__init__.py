"""
This module is used to provide the necessary classes and exceptions
for the authentication and authorization of users.
"""
from user_utils.schemas import User
from user_utils.schemas import Admin as AdminUser
from .exceptions import AuthorizationException
from .middlewares import require_admin_user, require_user

from .schemas import Token, TokenData, ValidationCode

__all__ = [
    "User",
    "AdminUser",
    "AuthorizationException",
    "require_admin_user",
    "require_user",
    "Token",
    "TokenData",
    "ValidationCode",
]
