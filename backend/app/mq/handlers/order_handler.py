"""Kafka 訂單相關事件的處理函式。"""

import json
from app.services.order_service import create_order

def handle_order_created(message: str):
    """處理訂單建立事件並寫入資料庫。"""
    data = json.loads(message)
    customer_name = data.get("customer_name", "unknown")
    create_order(customer_name)
