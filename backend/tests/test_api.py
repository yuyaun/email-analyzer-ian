import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# Use in-memory SQLite by patching the database engine before app import
import app.core.database as database
database.engine = create_engine("sqlite:///:memory:")
database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
database.Base.metadata.create_all(bind=database.engine)

import confluent_kafka


class DummyProducer:
    def __init__(self, *args, **kwargs):
        pass

    def list_topics(self, timeout=1):  # pragma: no cover - simple mock
        return {}


confluent_kafka.Producer = DummyProducer

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize(
    "url,expected",
    [
        (f"/{os.getenv('BASE_ROUTER')}/api/internal/v1/readiness", {"status": "ready"}),
        (f"/{os.getenv('BASE_ROUTER')}/api/internal/v1/liveness", {"status": "ok"}),
        (f"/{os.getenv('BASE_ROUTER')}/api/mcm/v1/products/", {"product": "Sample product"}),
        (f"/{os.getenv('BASE_ROUTER')}/api/scm/v1/orders/", {"orders": []}),
    ],
)
def test_endpoints(url, expected):
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == expected
