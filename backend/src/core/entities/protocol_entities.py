from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import StrEnum
import uuid


class IngestionStatus(StrEnum):
    PENDING = "pending"
    INGESTED = "ingested"
    FAILED = "failed"


class ProtocolDocument(BaseModel):
    document_id: uuid.UUID
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
    protocol_id: uuid.UUID
    document_id: uuid.UUID
    protocol_name: str
    description: Optional[str] = None
    created_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProtocolStep(BaseModel):
    protocol_step_id: uuid.UUID
    protocol_id: uuid.UUID
    step_number: int
    step_name: str
    instruction: str
    expected_duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateProtocolPreviewRequest(BaseModel):
    filename: str
    file_type: str
    file_extension: str
    file_content: bytes
    file_size: Optional[int] = None
    description: Optional[str] = None
    created_by_user_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class ProtocolPreviewResponse(BaseModel):
    protocol: Protocol
    protocol_steps: List[ProtocolStep]
    object_url: str

    class Config:
        from_attributes = True