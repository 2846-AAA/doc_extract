from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.core.dependencies import get_db
from app.core.exceptions import (
    UnsupportedDocumentTypeError, FileTooLargeError,
    DocumentProcessingError, bad_request, not_found, server_error
)
from app.services.extraction_service import ExtractionService
from app.models.schemas import ExtractionResponse, ExtractionListItem, SupportedTypesResponse
from app.extractors.templates import list_supported_types

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/tiff",
    "application/pdf"
}


@router.post("/extract", response_model=ExtractionResponse)
async def extract_document(
    file: UploadFile = File(...),
    doc_type: str = Query(..., description="Document type: aadhaar, passport, driving_licence, invoice, pan_card"),
    db: Session = Depends(get_db)
):
    # validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise bad_request(f"Unsupported file type: {file.content_type}. Allowed: JPG, PNG, TIFF, PDF")

    file_bytes = await file.read()

    if not file_bytes:
        raise bad_request("Uploaded file is empty")

    service = ExtractionService(db)

    try:
        record = service.process_document(
            file_bytes=file_bytes,
            filename=file.filename or "unknown",
            doc_type=doc_type
        )
        return ExtractionResponse.model_validate(record)

    except UnsupportedDocumentTypeError as e:
        raise bad_request(e.message)
    except FileTooLargeError as e:
        raise bad_request(e.message)
    except Exception as e:
        logger.exception(f"Unexpected error during extraction: {e}")
        raise server_error("Document processing failed. Check server logs.")


@router.get("/extractions", response_model=list[ExtractionListItem])
def list_extractions(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    service = ExtractionService(db)
    records = service.list_records(limit=limit, offset=offset)
    return [ExtractionListItem.model_validate(r) for r in records]


@router.get("/extractions/{record_id}", response_model=ExtractionResponse)
def get_extraction(record_id: int, db: Session = Depends(get_db)):
    service = ExtractionService(db)
    record = service.get_record(record_id)
    if not record:
        raise not_found(f"Extraction record {record_id} not found")
    return ExtractionResponse.model_validate(record)


@router.get("/supported-types", response_model=SupportedTypesResponse)
def get_supported_types():
    return SupportedTypesResponse(supported_types=list_supported_types())


@router.delete("/extractions/{record_id}")
def delete_extraction(record_id: int, db: Session = Depends(get_db)):
    from app.db.repository import ExtractionRepository
    repo = ExtractionRepository(db)
    deleted = repo.delete(record_id)
    if not deleted:
        raise not_found(f"Record {record_id} not found")
    return {"message": f"Record {record_id} deleted"}
