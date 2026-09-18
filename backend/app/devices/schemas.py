from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DeviceResponse(BaseModel):
    device_id: str
    owner_id: str
    name: str
    type: str
    platform: str
    status: str
    last_seen: datetime
    capabilities: List[str]
    version: str

    model_config = ConfigDict(from_attributes=True)


class DeviceUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class PairingCodeResponse(BaseModel):
    pairing_code: str
    expires_at: datetime
    expires_in_seconds: int


class PairingClaimRequest(BaseModel):
    pairing_code: str = Field(..., min_length=6, max_length=16)
    device_id: str = Field(..., min_length=3, max_length=64)
    device_name: str = Field(..., min_length=1, max_length=128)
    device_type: str = Field("computer", max_length=64)
    platform: str = Field("windows", max_length=64)
    capabilities: List[str] = Field(default_factory=list)
    version: str = Field("1.0.0", max_length=32)


class PairingClaimResponse(BaseModel):
    device_id: str
    device_token: str
    ws_url: str
    message: str = "Device successfully paired."
