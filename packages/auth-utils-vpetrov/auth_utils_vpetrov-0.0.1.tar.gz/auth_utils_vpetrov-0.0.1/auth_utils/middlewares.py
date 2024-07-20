"""
Necessary middlewares for the app.
"""
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from user_utils.schemas import User, Admin
from . import exceptions



oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8001/create/user")


def require_admin_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Middleware to require an admin user.
    """
    # Request user from auth app.
    print(token)
    # Mock
    admin = {
        "id": 1,
        "is_admin": True,
        "name": "Admin User",
        "email": "admin@domain.com"
    }
    if not admin:
        raise exceptions.AuthorizationException()
    return Admin(**admin)


def require_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Middleware to require a user.
    """
    # Request user from auth app.
    print(token)
    # Mock
    user = {
        "id": 1,
        "name": "Name",
        "last_name": "Last Name",
        "email": "email@domain.com",
        "phone": "+56912345678",
        "rut": "11.111.111-1",
        "birth_date": "1990-01-01"
    }
    if not user:
        raise exceptions.AuthorizationException()
    return User(**user)
