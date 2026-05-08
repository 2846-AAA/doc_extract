import pytest
from unittest.mock import MagicMock, patch
import io
from PIL import Image

from app.extractors.templates import get_template, list_supported_types
from app.core.exceptions import (
    UnsupportedDocumentTypeError, OCRError, LLMError, FileTooLargeError
)


# --- Template tests ---

def test_get_template_aadhaar():
    t = get_template("aadhaar")
    assert t is not None
    assert t.doc_type == "aadhaar"
    assert "name" in t.fields
    assert "aadhaar_number" in t.fields


def test_get_template_pan_card():
    # added PAN card as extra
    t = get_template("pan_card")
    assert t is not None
    assert "pan_number" in t.fields


def test_get_template_invalid_returns_none():
    t = get_template("random_doc_type")
    assert t is None


def test_supported_types_contains_all():
    types = list_supported_types()
    expected = ["aadhaar", "passport", "driving_licence", "invoice", "pan_card"]
    for doc in expected:
        assert doc in types


def test_template_has_prompt_hint():
    for doc_type in list_supported_types():
        t = get_template(doc_type)
        assert t.prompt_hint != ""


# --- OCR service tests ---

def test_ocr_empty_image_raises_error():
    from app.extractors.ocr_service import OCRService

    with patch("pytesseract.image_to_string", return_value="   "):
        svc = OCRService()
        fake_img = io.BytesIO()
        Image.new("RGB", (100, 100), "white").save(fake_img, format="PNG")

        with pytest.raises(OCRError):
            svc.extract_text(fake_img.getvalue())


def test_ocr_returns_text_successfully(sample_image_bytes):
    from app.extractors.ocr_service import OCRService

    with patch("pytesseract.image_to_string", return_value="Rahul Kumar\n1234 5678 9012"):
        svc = OCRService()
        result = svc.extract_text(sample_image_bytes)
        assert "Rahul Kumar" in result


# --- LLM service tests ---

def test_llm_parses_valid_json(mock_ocr_text, mock_extracted_data):
    from app.extractors.llm_service import LLMService
    import json

    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(mock_extracted_data)

    with patch.object(LLMService, "__init__", lambda self: None):
        svc = LLMService.__new__(LLMService)
        svc.model = "gpt-4o-mini"
        svc.client = MagicMock()
        svc.client.chat.completions.create.return_value = mock_response

        template = get_template("aadhaar")
        result = svc.extract_fields(mock_ocr_text, template)

        assert result["name"] == "Rahul Kumar"
        assert result["aadhaar_number"] == "1234 5678 9012"


def test_llm_raises_on_invalid_json(mock_ocr_text):
    from app.extractors.llm_service import LLMService

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "this is not json at all"

    with patch.object(LLMService, "__init__", lambda self: None):
        svc = LLMService.__new__(LLMService)
        svc.model = "gpt-4o-mini"
        svc.client = MagicMock()
        svc.client.chat.completions.create.return_value = mock_response

        template = get_template("aadhaar")
        with pytest.raises(LLMError):
            svc.extract_fields(mock_ocr_text, template)


# --- DB / integration tests ---

@pytest.mark.skip(reason="need real db connection")
def test_save_extraction_to_db():
    from app.db.repository import ExtractionRepository
    from app.db.database import SessionLocal

    db = SessionLocal()
    repo = ExtractionRepository(db)
    record = repo.create(
        doc_type="aadhaar",
        filename="test.jpg",
        raw_text="some raw text",
        extracted_data={"name": "Test User"},
        status="success"
    )
    assert record.id is not None
    db.close()


@pytest.mark.skip(reason="need real db connection")
def test_full_pipeline_with_real_db(sample_image_bytes):
    from app.services.extraction_service import ExtractionService
    from app.db.database import SessionLocal

    with patch("app.extractors.ocr_service.pytesseract.image_to_string",
               return_value="Name: Test\nAadhaar: 0000 0000 0000"):
        with patch("app.extractors.llm_service.LLMService.extract_fields",
                   return_value={"name": "Test", "aadhaar_number": "0000 0000 0000"}):
            db = SessionLocal()
            svc = ExtractionService(db)
            record = svc.process_document(sample_image_bytes, "test.png", "aadhaar")
            assert record.status == "success"
            db.close()
