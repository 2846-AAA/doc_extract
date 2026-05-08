from loguru import logger
from sqlalchemy.orm import Session

from app.extractors.ocr_service import OCRService
from app.extractors.llm_service import LLMService
from app.extractors.templates import get_template
from app.db.repository import ExtractionRepository
from app.db.models import ExtractionRecord
from app.core.exceptions import (
    UnsupportedDocumentTypeError, OCRError, LLMError,
    FileTooLargeError, DocumentProcessingError
)
from app.core.config import settings


class ExtractionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = ExtractionRepository(db)
        self.ocr = OCRService()
        self.llm = LLMService()

    def process_document(self, file_bytes: bytes, filename: str, doc_type: str) -> ExtractionRecord:
        """
        Main pipeline: validate -> OCR -> LLM -> save to DB
        """
        # check file size
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            raise FileTooLargeError(size_mb, settings.MAX_FILE_SIZE_MB)

        # check doc type
        template = get_template(doc_type)
        if not template:
            raise UnsupportedDocumentTypeError(doc_type)

        logger.info(f"Processing {doc_type} document: {filename} ({size_mb:.2f}MB)")

        raw_text = ""
        extracted_data = {}
        status = "success"
        error_msg = None

        # OCR step
        try:
            if filename.lower().endswith(".pdf"):
                raw_text = self.ocr.extract_text_from_pdf(file_bytes)
            else:
                raw_text = self.ocr.extract_text(file_bytes)
        except OCRError as e:
            logger.warning(f"OCR failed for {filename}: {e}")
            status = "failed"
            error_msg = str(e)
            # still save the record even on failure
            return self.repo.create(
                doc_type=doc_type,
                filename=filename,
                raw_text="",
                extracted_data={},
                status=status,
                error_message=error_msg
            )

        # LLM extraction step
        try:
            extracted_data = self.llm.extract_fields(raw_text, template)
        except LLMError as e:
            logger.warning(f"LLM extraction failed: {e}")
            status = "partial"
            error_msg = str(e)
            # return with raw text but empty extraction

        record = self.repo.create(
            doc_type=doc_type,
            filename=filename,
            raw_text=raw_text,
            extracted_data=extracted_data,
            status=status,
            error_message=error_msg
        )

        logger.info(f"Extraction complete: record id={record.id}")
        return record

    def get_record(self, record_id: int) -> ExtractionRecord | None:
        return self.repo.get_by_id(record_id)

    def list_records(self, limit: int = 50, offset: int = 0) -> list[ExtractionRecord]:
        return self.repo.get_all(limit=limit, offset=offset)
