from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.device_service import DeviceService
from app.devices.schemas import (
    DeviceResponse,
    DeviceUpdateRequest,
    PairingCodeResponse,
    PairingClaimRequest,
    PairingClaimResponse
)
from app.auth.dependencies import get_current_user
from app.database.models import User

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    devices = await service.list_user_devices(current_user.id)
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    device = await service.get_device(current_user.id, device_id)
    return device


@router.get("/{device_id}/capabilities", response_model=List[str])
async def get_device_capabilities(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    device = await service.get_device(current_user.id, device_id)
    return device.capabilities or []


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    req: DeviceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    updated = await service.update_device_name(current_user.id, device_id, req)
    return updated


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    await service.delete_device(current_user.id, device_id)
    return None


@router.post("/pair/code", response_model=PairingCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_pairing_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DeviceService(db)
    pairing_code = await service.generate_pairing_code(current_user.id)
    return pairing_code


@router.post("/pair/claim", response_model=PairingClaimResponse)
async def claim_pairing_code(
    req: PairingClaimRequest,
    db: AsyncSession = Depends(get_db)
):
    """Called by the Device Agent to exchange a 6-digit pairing code for a long-lived device token."""
    service = DeviceService(db)
    claim_result = await service.claim_pairing_code(req)
    return claim_result
