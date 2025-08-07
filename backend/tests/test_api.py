"""API 層級測試，涵蓋 JWT 與產生任務等流程。"""

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


last_producer = None


class DummyProducer:
    """替代真實 Kafka Producer 的簡易模擬物件。"""

    def __init__(self, *args, **kwargs):
        global last_producer
        last_producer = self
        self.sent_messages = []

    def produce(self, topic, value):  # pragma: no cover - simple mock
        self.sent_messages.append((topic, value))

    def flush(self, timeout=None):  # pragma: no cover - simple mock
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


def _get_token():
    exp = (datetime.utcnow() + timedelta(minutes=20)).isoformat()
    payload = {"userSn": "test-user", "exp": exp}
    response = client.post(f"/{os.getenv('BASE_ROUTER')}/api/public/v1/jwt", json=payload)
    return response.json()["token"]


def test_generate_api():
    token = _get_token()
    payload = {
        "campaignSn": "abc123",
        "magicType": "title_optimize",
        "content": "Hello",
    }
    response = client.post(
        f"/{os.getenv('BASE_ROUTER')}/api/public/v1/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert last_producer is not None
    assert len(last_producer.sent_messages) == 1


def test_cors_headers():
    response = client.options(
        f"/{os.getenv('BASE_ROUTER')}/api/public/v1/jwt",
        headers={
            "Origin": "http://localhost:8001",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:8001"


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
