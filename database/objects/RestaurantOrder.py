"""
Module defining order statuses, payment methods, and data classes for restaurant orders.

Enums:
    OrderStatus: Enum representing the possible statuses of a restaurant order (Open, Closed, Cancelled).
    PaymentMethod: Enum representing the available payment methods for a restaurant order
                   (Cash, Card, Pix, Others).

Classes:
    RestaurantOrder (dataclass): Data class representing a restaurant order, including attributes
                                 for order number, entry and exit times, status, notes, payment
                                 method, total amount, and payment status.
    OrderStatusHistory (dataclass): Data class representing the history of status changes for
                                    a restaurant order, including attributes for the order ID,
                                    status at the time of change, change time, and notes.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """Enum representing the possible statuses of a restaurant order."""
    OPEN = 'Open'
    CLOSED = 'Closed'
    CANCELLED = 'Cancelled'


class PaymentMethod(Enum):
    """Enum representing the available payment methods for a restaurant order."""
    CASH = 'Cash'
    CARD = 'Card'
    PIX = 'Pix'
    OTHERS = 'Others'


@dataclass
class RestaurantOrder:
    """Data class representing a restaurant order.

        Attributes:
            number (int): The order number.
            entry_time (datetime): The time when the order was placed.
            id (int, optional): Unique identifier for the order. Defaults to None.
            exit_time (datetime, optional): The time when the order was completed. Defaults to None.
            status (OrderStatus, optional): The current status of the order. Defaults to OPEN.
            note (str, optional): Any additional notes related to the order. Defaults to an empty string.
            payment_method (PaymentMethod, optional): The method of payment used for the order. Defaults to None.
            total_amount (float, optional): The total amount for the order. Defaults to 0.00.
            paid (bool, optional): Indicates if the order has been paid. Defaults to False.
    """
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
    """Data class representing the history of status changes for a restaurant order.

        Attributes:
            restaurant_order_id (int): The ID of the associated restaurant order.
            status (OrderStatus): The status of the order at the time of the change.
            change_time (datetime, optional): The time when the status was changed. Defaults to the current time.
            id (int, optional): Unique identifier for the status history entry. Defaults to None.
            note (str, optional): Any additional notes related to the status change. Defaults to an empty string.
    """
    restaurant_order_id: int
    status: OrderStatus
    change_time: datetime = field(default_factory=datetime.now)
    id: int = field(default=None)
    note: str = field(default='')