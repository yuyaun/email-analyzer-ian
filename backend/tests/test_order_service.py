import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite to avoid requiring PostgreSQL
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.models.order import Order
from app.core.database import Base
import app.services.order_service as order_service

@pytest.fixture
def test_session(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(order_service, "SessionLocal", TestingSessionLocal)
    yield TestingSessionLocal

@pytest.mark.parametrize("name", ["Alice", "Bob"])
def test_create_order(test_session, name):
    order = order_service.create_order(name)
    assert isinstance(order, Order)
    assert order.customer_name == name
