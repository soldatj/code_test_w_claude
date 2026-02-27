# order_service.py
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .models import Order, OrderItem, OrderStatus, Product
from .discount import calculate_discount
from .validators import validate_order_items

class InsufficientStockError(Exception):
    pass

class OrderNotFoundError(Exception):
    pass

class OrderCancellationError(Exception):
    pass

class OrderService:
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    def create_order(self, items: List[OrderItem]) -> Order:
        validate_order_items(items)
        
        for item in items:
            if item.product.stock < item.quantity:
                raise InsufficientStockError(
                    f"'{item.product.name}' : " 
                    f" {item.quantity} , {item.product.stock} "
                )
        
        # for item in items:
        #     item.product.stock -= item.quantity
        
        order_id = str(uuid.uuid4())[:8]
        discount_rate = calculate_discount(items)
        order = Order(id=order_id, items=items, discount_rate=discount_rate)
        self._orders[order_id] = order
        return order
    
    def cancel_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        
        if order.status == OrderStatus.SHIPPED:
            raise OrderCancellationError(" .")
        
        if order.status == OrderStatus.CANCELLED:
            raise OrderCancellationError(" .")
        
        # 24 
        if datetime.now() - order.created_at > timedelta(hours=24):
            raise OrderCancellationError(" 24 .")
        
        # for item in order.items:
        #     item.product.stock += item.quantity
        
        order.status = OrderStatus.CANCELLED
        return order
    
    def get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise OrderNotFoundError(f" '{order_id}' ( ) .")
        return self._orders[order_id]
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        return [o for o in self._orders.values() if o.status == status]
