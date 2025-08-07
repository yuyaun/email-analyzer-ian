"""Pydantic 模型：訂單相關 schema。"""

from pydantic import BaseModel


class OrderCreate(BaseModel):
    """建立訂單時所需的資料。"""

    customer_name: str
