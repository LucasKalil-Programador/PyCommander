from dataclasses import dataclass, field


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