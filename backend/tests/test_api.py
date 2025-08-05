import os
from datetime import datetime, timedelta

import jwt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


def test_jwt_token():
    exp = (datetime.utcnow() + timedelta(minutes=20)).isoformat()
    payload = {"userSn": "test-user", "exp": exp}
    response = client.post(f"/{os.getenv('BASE_ROUTER')}/api/public/v1/jwt", json=payload)
    assert response.status_code == 200
    token = response.json()["token"]
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    assert decoded["userSn"] == "test-user"


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            f"/{os.getenv('BASE_ROUTER')}/api/internal/v1/readiness",
            {"status": "ready"},
        ),
        (
            f"/{os.getenv('BASE_ROUTER')}/api/internal/v1/liveness",
            {"status": "ok"},
        ),
    ],
)
def test_internal_endpoints(url, expected):
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == expected
