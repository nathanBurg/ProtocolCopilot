from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import StrEnum
import uuid


class SenderRole(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class MessageType(StrEnum):
    INSTRUCTION = "instruction"
    OBSERVATION = "observation"
    QUESTION = "question"
    RESPONSE = "response"
    SUMMARY = "summary"


class Experiment(BaseModel):
    experiment_id: uuid.UUID
    protocol_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExperimentStep(BaseModel):
    experiment_step_id: uuid.UUID
    experiment_id: uuid.UUID
    protocol_step_id: uuid.UUID
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExperimentConversation(BaseModel):
    message_id: uuid.UUID
    experiment_id: uuid.UUID
    experiment_step_id: Optional[uuid.UUID] = None
    sender_role: SenderRole
    message_type: MessageType
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# Request/Response Models
class StartExperimentRequest(BaseModel):
    protocol_id: str
    user_id: Optional[str] = None

class StartExperimentResponse(BaseModel):
    experiment_id: str
    status: str
    message: str

class StopExperimentRequest(BaseModel):
    experiment_id: str
    end_time: Optional[datetime] = None

class StopExperimentResponse(BaseModel):
    experiment_id: str
    status: str
    message: str
