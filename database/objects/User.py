"""
Module defining user roles and a User data class for a restaurant management system.

Classes:
    UserRole (Enum): Enum representing various user roles in the system (Admin, Waiter, Cook, Cashier).
    User (dataclass): Data class representing a user with attributes for name, username, email,
                      password hash, unique ID, role, and active status.
"""
from dataclasses import dataclass, field
from enum import Enum


class UserRole(Enum):
    """Enum representing the different roles a user can have in the system."""
    ADMIN = 'Admin'
    WAITER = 'Waiter'
    COOK = 'Cook'
    CASHIER = 'Cashier'


@dataclass
class User:
    """Data class representing a user in the system.

        Attributes:
            name (str): The user's full name.
            username (str): The user's chosen username.
            email (str): The user's email address.
            password_hash (str): The hashed password for authentication.
            id (int, optional): Unique identifier for the user. Defaults to None.
            role (UserRole, optional): The role of the user. Defaults to CASHIER.
            active (bool, optional): Indicates if the user account is active. Defaults to True.
    """
    name: str
    username: str
    email: str
    password_hash: str
    id: int = field(default=None)
    role: UserRole = field(default=UserRole.CASHIER)
    active: bool = field(default=True)
