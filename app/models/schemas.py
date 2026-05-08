from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ExtractionResponse(BaseModel):
    id: int
    doc_type: str
    filename: Optional[str]
    raw_text: Optional[str]
    extracted_data: Optional[dict[str, Any]]
    status: str
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractionListItem(BaseModel):
    id: int
    doc_type: str
    filename: Optional[str]
    status: str
    created_at: datetime
    extracted_data: Optional[dict[str, Any]]

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str


class SupportedTypesResponse(BaseModel):
    supported_types: list[str]
