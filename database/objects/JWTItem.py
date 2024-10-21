"""
Module defining a JWTItem data class for handling JSON Web Tokens.

Classes:
    JWTItem (dataclass): Data class representing a JWT item with attributes for the unique
                         identifier (jti), user ID, and expiration time of the token.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JWTItem:
    """Data class representing a JSON Web Token (JWT) item.

        Attributes:
            jti (str): The unique identifier for the JWT.
            user_id (int): The ID of the user associated with the JWT.
            expires_at (datetime): The expiration date and time of the JWT.
    """
    jti: str
    user_id: int
    expires_at: datetime
