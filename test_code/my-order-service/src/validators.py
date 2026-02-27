# validators.py
from typing import List
from .models import OrderItem

def validate_order_items(items: List[OrderItem]):
    """주문 항목 유효성 검사"""
    if not items:
        raise ValueError("주문 항목이 비어있습니다.")
    
    for item in items:
        if item.quantity <= 0:
            raise ValueError(f"수량은 1 이상이어야 합니다: {item.quantity}")
        
        if not item.product:
            raise ValueError("상품이 없습니다.")
        
        if item.product.price <= 0:
            raise ValueError("가격은 0보다 커야 합니다.")
