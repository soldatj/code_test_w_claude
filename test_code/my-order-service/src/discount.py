# discount.py
from typing import List

def calculate_discount(items) -> float:
    """
    :
    - 100,000 : 10%
    - 50,000 : 5%
    - 3 : 2% ( )
    - : 15%
    """
    total = sum(item.product.price * item.quantity for item in items)
    discount = 0.0
    
    if total >= 100_000:
        discount = 0.10
    elif total >= 50_000:
        discount = 0.05
    
    if len(items) >= 3:
        discount += 0.02
    
    return min(discount, 0.15)
