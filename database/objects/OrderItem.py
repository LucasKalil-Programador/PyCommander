"""
Module defining an OrderItem data class for restaurant orders.

Classes:
    OrderItem (dataclass): Data class representing an item in a restaurant order, including
                           attributes for the order ID, quantity, unique ID, and product IDs.
                           It enforces that either a product ID or a product ID for weight
                           must be provided, but not both.
"""
from dataclasses import dataclass, field


@dataclass
class OrderItem:
    """Data class representing an item in a restaurant order.

        Attributes:
            restaurant_order_id (int): The ID of the associated restaurant order.
            quantity (int, optional): The quantity of the product ordered. Defaults to 1.
            id (int, optional): Unique identifier for the order item. Defaults to None.
            product_id (int, optional): The ID of the product. Defaults to None.
            product_per_kg_id (int, optional): The ID of the product sold by weight. Defaults to None.

        Raises:
            ValueError: If both 'product_id' and 'product_per_kg_id' are provided or if both are None.
    """
    restaurant_order_id: int
    quantity: int = field(default=1)
    id: int = field(default=None)
    product_id: int = field(default=None)
    product_per_kg_id: int = field(default=None)

    def __post_init__(self):
        if (self.product_id is not None and self.product_per_kg_id is not None) or (self.product_id is None and self.product_per_kg_id is None):
            raise ValueError("Either 'product_id' or 'product_per_kg_id' must be provided, but not both.")