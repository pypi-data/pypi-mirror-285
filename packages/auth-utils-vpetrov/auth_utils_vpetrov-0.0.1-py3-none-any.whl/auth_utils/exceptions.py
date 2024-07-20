"""
Exceptions for the winners app.
"""
from fastapi import HTTPException
from pydantic import BaseModel


class AuthorizationException(HTTPException):
    """
    Exception for authorization errors.
    """
    class AuthorizationErrorSchema(BaseModel):
        """
        Schema for the AuthorizationError model.
        """
        detail: str = "You are not authorized to perform this action"

    def __init__(self):
        schema_instance = self.AuthorizationErrorSchema()
        super().__init__(
            status_code=401,
            detail=schema_instance.detail
            )
