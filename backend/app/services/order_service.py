"""與訂單相關的服務函式。"""

from app.models.order import Order
from app.core.database import SessionLocal

def create_order(customer_name: str):
    """建立一筆新的訂單並寫入資料庫。"""
    db = SessionLocal()
    order = Order(customer_name=customer_name)
    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()
    return order
