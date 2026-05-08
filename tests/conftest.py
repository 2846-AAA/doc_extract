import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import io
from PIL import Image


# We mock the settings to avoid needing a real .env during tests
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key")


@pytest.fixture
def sample_image_bytes():
    """Create a simple test image with some text"""
    img = Image.new("RGB", (400, 200), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_ocr_text():
    return """
    Government of India
    Name: Rahul Kumar
    Date of Birth: 15/08/1995
    Male
    1234 5678 9012
    123 Main Street, Mumbai, Maharashtra 400001
    """


@pytest.fixture
def mock_extracted_data():
    return {
        "name": "Rahul Kumar",
        "date_of_birth": "15/08/1995",
        "gender": "Male",
        "aadhaar_number": "1234 5678 9012",
        "address": "123 Main Street, Mumbai, Maharashtra",
        "pincode": "400001"
    }
