from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import StrEnum


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
    experiment_id: int
    protocol_id: int
    user_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExperimentStep(BaseModel):
    experiment_step_id: int
    experiment_id: int
    protocol_step_id: int
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExperimentConversation(BaseModel):
    message_id: int
    experiment_id: int
    experiment_step_id: Optional[int] = None
    sender_role: SenderRole
    message_type: MessageType
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
