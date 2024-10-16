from dataclasses import dataclass, field
from enum import Enum


class UserRole(Enum):
    ADMIN = 'Admin'
    WAITER = 'Waiter'
    COOK = 'Cook'
    CASHIER = 'Cashier'


@dataclass
class User:
    name: str
    username: str
    email: str
    password_hash: str
    id: int = field(default=None)
    role: UserRole = field(default=UserRole.CASHIER)
    active: bool = field(default=True)
