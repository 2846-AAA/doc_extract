from sqlalchemy.orm import Session
from app.db.models import ExtractionRecord
from loguru import logger


class ExtractionRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, doc_type: str, filename: str, raw_text: str,
               extracted_data: dict, status: str = "success",
               error_message: str = None) -> ExtractionRecord:
        record = ExtractionRecord(
            doc_type=doc_type,
            filename=filename,
            raw_text=raw_text,
            extracted_data=extracted_data,
            status=status,
            error_message=error_message
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info(f"Saved extraction record id={record.id} doc_type={doc_type}")
        return record

    def get_by_id(self, record_id: int) -> ExtractionRecord | None:
        return self.db.query(ExtractionRecord).filter(
            ExtractionRecord.id == record_id
        ).first()

    def get_all(self, limit: int = 50, offset: int = 0) -> list[ExtractionRecord]:
        return self.db.query(ExtractionRecord)\
            .order_by(ExtractionRecord.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_by_doc_type(self, doc_type: str) -> list[ExtractionRecord]:
        return self.db.query(ExtractionRecord).filter(
            ExtractionRecord.doc_type == doc_type
        ).all()

    def delete(self, record_id: int) -> bool:
        record = self.get_by_id(record_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
