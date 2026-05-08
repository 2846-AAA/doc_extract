from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class ExtractionRecord(Base):
    __tablename__ = "extraction_records"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(String(50), nullable=False)
    filename = Column(String(255))
    raw_text = Column(Text)
    extracted_data = Column(JSON)
    status = Column(String(20), default="success")  # success / failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ExtractionRecord id={self.id} doc_type={self.doc_type}>"
