import json
from app.services.order_service import create_order

def handle_order_created(message: str):
    data = json.loads(message)
    customer_name = data.get("customer_name", "unknown")
    create_order(customer_name)