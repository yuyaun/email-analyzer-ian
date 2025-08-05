from app.models.order import Order
from app.core.database import SessionLocal

def create_order(customer_name: str):
    db = SessionLocal()
    order = Order(customer_name=customer_name)
    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()
    return order