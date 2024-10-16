from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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