# models.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"

@dataclass
class Product:
    id: str
    name: str
    price: float
    stock: int

@dataclass
class OrderItem:
    product: Product
    quantity: int
    
    @property
    def subtotal(self) -> float:
        return self.product.price * self.quantity

@dataclass
class Order:
    id: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    discount_rate: float = 0.0
    
    @property
    def total(self) -> float:
        raw_total = sum(item.subtotal for item in self.items)
        return round(raw_total * (1 - self.discount_rate), 2)
