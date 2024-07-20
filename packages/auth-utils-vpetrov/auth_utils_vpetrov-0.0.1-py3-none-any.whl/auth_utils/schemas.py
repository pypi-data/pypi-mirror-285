"""
Schemas for the winners_app app
"""
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    """
    Base schema for Tokens.
    """
    access_token: str = Field(..., description="The access Bearer token")


class TokenData(BaseModel):
    """
    Base schema for TokenData.
    """
    email: EmailStr
    password: str
    exp: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(minutes=43200),
    )


class ValidationCode(BaseModel):
    """
    Base schema for Validation.
    """
    code: str = Field(
        ..., description="The validation code", max_length=6, min_length=6)
