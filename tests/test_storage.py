import pytest

from app.core import storage
from app.core.config import settings

pytestmark = pytest.mark.unit


@pytest.fixture
def build_client(monkeypatch):
    monkeypatch.setattr(settings, "R2_ACCESS_KEY_ID", "key")
    monkeypatch.setattr(settings, "R2_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setattr(settings, "R2_BUCKET_NAME", "photos")
    monkeypatch.setattr(settings, "R2_ACCOUNT_ID", "")
    monkeypatch.setattr(settings, "STORAGE_ENDPOINT_URL", "")
    monkeypatch.setattr(settings, "STORAGE_REGION", "auto")
    storage._client.cache_clear()

    def build(**fields):
        for name, value in fields.items():
            monkeypatch.setattr(settings, name, value)
        return storage._client()

    yield build
    storage._client.cache_clear()


def test_r2_from_account_id_as_before(build_client):
    c = build_client(R2_ACCOUNT_ID="abc123")
    assert c.meta.endpoint_url == "https://abc123.r2.cloudflarestorage.com"
    assert c.meta.region_name == "auto"


def test_explicit_endpoint_takes_precedence(build_client):
    c = build_client(R2_ACCOUNT_ID="abc123", STORAGE_ENDPOINT_URL="https://other.example.com")
    assert c.meta.endpoint_url == "https://other.example.com"


def test_aws_s3_without_endpoint(build_client):
    c = build_client(STORAGE_REGION="us-east-1")
    assert storage.configurado()
    assert c.meta.endpoint_url == "https://s3.amazonaws.com"
    assert c.meta.region_name == "us-east-1"
