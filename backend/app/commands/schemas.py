from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProcessCommandRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language voice/text command")


class ProcessCommandResponse(BaseModel):
    command_id: str
    status: str  # completed, failed, confirmation_required, cancelled
    target_device_id: Optional[str] = None
    capability: Optional[str] = None
    speech_response: str
    text_response: str
    requires_confirmation: bool = False
    confirmation_token: Optional[str] = None
    confirmation_prompt: Optional[str] = None


class ConfirmCommandRequest(BaseModel):
    confirmation_token: str = Field(..., min_length=1)
    confirmed: bool = Field(..., description="True to execute, False to cancel")


class CommandHistoryResponse(BaseModel):
    id: str
    query: str
    action: Optional[str] = None
    device_name: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
