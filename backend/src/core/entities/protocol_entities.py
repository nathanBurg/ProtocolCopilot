from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import StrEnum


class IngestionStatus(StrEnum):
    PENDING = "pending"
    INGESTED = "ingested"
    FAILED = "failed"


class ProtocolDocument(BaseModel):
    document_id: int
    document_name: str
    description: Optional[str] = None
    object_url: str
    mime_type: Optional[str] = None
    ingestion_status: IngestionStatus = IngestionStatus.PENDING
    ingested_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Protocol(BaseModel):
    protocol_id: int
    document_id: int
    protocol_name: str
    description: Optional[str] = None
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProtocolStep(BaseModel):
    protocol_step_id: int
    protocol_id: int
    step_number: int
    step_name: str
    instruction: str
    expected_duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True