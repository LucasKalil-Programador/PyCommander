from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    ADMIN = 'Admin'
    WAITER = 'Waiter'
    COOK = 'Cook'
    CASHIER = 'Cashier'


class OrderStatus(Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'
    CANCELLED = 'Cancelled'


class PaymentMethod(Enum):
    CASH = 'Cash'
    CARD = 'Card'
    PIX = 'Pix'
    OTHERS = 'Others'


@dataclass
class RestaurantOrder:
    number: int
    entry_time: datetime
    id: int = field(default=None)
    exit_time: datetime = field(default=None)
    status: OrderStatus = field(default=OrderStatus.OPEN)
    note: str = field(default='')
    payment_method: PaymentMethod = field(default=None)
    total_amount: float = field(default=0.00)
    paid: bool = field(default=False)


@dataclass
class OrderStatusHistory:
    restaurant_order_id: int
    status: OrderStatus
    change_time: datetime = field(default_factory=datetime.now)
    id: int = field(default=None)
    note: str = field(default='')


@dataclass
class Product:
    name: str
    price: float
    stock: int
    id: int = field(default=None)
    description: str = field(default='')
    category: str = field(default=None)
    active: bool = field(default=True)


@dataclass
class ProductPerKg:
    weight: float
    price_per_kg: float
    id: int = field(default=None)
    description: str = field(default='')
    category: str = field(default=None)
    total: float = field(init=False)

    def __post_init__(self):
        self.total = self.weight * self.price_per_kg


@dataclass
class KgPrice:
    price: float
    id: int = field(default=None)
    category: str = field(default=None)


@dataclass
class OrderItem:
    restaurant_order_id: int
    quantity: int = field(default=1)
    id: int = field(default=None)
    product_id: int = field(default=None)
    product_per_kg_id: int = field(default=None)

    def __post_init__(self):
        if (self.product_id is not None and self.product_per_kg_id is not None) or (self.product_id is None and self.product_per_kg_id is None):
            raise ValueError("Either 'product_id' or 'product_per_kg_id' must be provided, but not both.")


@dataclass
class User:
    name: str
    username: str
    email: str
    password_hash: str
    id: int = field(default=None)
    role: UserRole = field(default=UserRole.CASHIER)
    active: bool = field(default=True)


@dataclass
class JWTItem:
    jti: str
    user_id: int
    expires_at: datetime
