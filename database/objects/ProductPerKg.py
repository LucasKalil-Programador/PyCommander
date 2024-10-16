from dataclasses import dataclass, field


@dataclass
class ProductPerKg:
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
    price: float
    id: int = field(default=None)
    category: str = field(default=None)