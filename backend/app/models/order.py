"""SQLAlchemy 模型：存放訂單資訊。"""

from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Order(Base):
    """對應 `orders` 資料表的 ORM 模型。"""

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)  # 訂單流水號
    customer_name = Column(String)  # 客戶名稱
