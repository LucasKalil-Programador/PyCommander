"""
Module defining data classes for products sold by weight and their pricing.

Classes:
    ProductPerKg (dataclass): Data class representing a product sold by weight, including
                              attributes for weight, price per kilogram, unique ID,
                              description, category, and total price calculated.
    KgPrice (dataclass): Data class representing the price per kilogram of a product,
                         including attributes for price, unique ID, and category.
"""
from dataclasses import dataclass, field


@dataclass
class ProductPerKg:
    """Data class representing a product sold by weight.

        Attributes:
            weight (float): The weight of the product in kilograms.
            price_per_kg (float): The price per kilogram of the product.
            id (int, optional): Unique identifier for the product. Defaults to None.
            description (str, optional): A brief description of the product. Defaults to an empty string.
            category (str, optional): The category of the product. Defaults to None.
            total (float): The total price calculated based on weight and price per kilogram.

        Post Initialization:
            total is calculated as weight multiplied by price_per_kg.
    """
    weight: float
    price_per_kg: float
    id: int = field(default=None)
    description: str = field(default='')
    category: str = field(default=None)
    total: float = field(init=False)

    def __post_init__(self):
        self.total = float(self.weight) * float(self.price_per_kg)


@dataclass
class KgPrice:
    """Data class representing a price for a product per kilogram.

        Attributes:
            price (float): The price per kilogram of the product.
            id (int, optional): Unique identifier for the price entry. Defaults to None.
            category (str, optional): The category of the product. Defaults to None.
    """
    price: float
    id: int = field(default=None)
    category: str = field(default=None)