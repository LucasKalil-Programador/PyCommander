from dataclasses import dataclass, field


@dataclass
class Product:
    name: str
    price: float
    stock: int
    id: int = field(default=None)
    description: str = field(default='')
    category: str = field(default=None)
    active: bool = field(default=True)
