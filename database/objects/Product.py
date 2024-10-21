"""
Module defining a Product data class for the inventory system.

Classes:
    Product (dataclass): Data class representing a product with attributes for name, price,
                         stock quantity, unique ID, description, category, and active status.
"""
from dataclasses import dataclass, field


@dataclass
class Product:
    """Data class representing a product in the inventory system.

        Attributes:
            name (str): The name of the product.
            price (float): The price of the product.
            stock (int): The quantity of the product available in stock.
            id (int, optional): Unique identifier for the product. Defaults to None.
            description (str, optional): A brief description of the product. Defaults to an empty string.
            category (str, optional): The category of the product. Defaults to None.
            active (bool, optional): Indicates if the product is active for sale. Defaults to True.
    """
    name: str
    price: float
    stock: int
    id: int = field(default=None)
    description: str = field(default='')
    category: str = field(default=None)
    active: bool = field(default=True)
