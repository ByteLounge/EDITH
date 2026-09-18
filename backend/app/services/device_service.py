from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.device_repository import DeviceRepository
from app.database.repositories.pairing_repository import PairingRepository
from app.database.models import Device, PairingCode
from app.auth.security import generate_device_token, generate_pairing_code
from app.config.settings import settings
from app.devices.schemas import (
    DeviceResponse,
    DeviceUpdateRequest,
    PairingCodeResponse,
    PairingClaimRequest,
    PairingClaimResponse
)


class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.pairing_repo = PairingRepository(db)

    async def list_user_devices(self, owner_id: str) -> List[Device]:
        return await self.device_repo.list_by_owner(owner_id)

    async def get_device(self, owner_id: str, device_id: str) -> Device:
        device = await self.device_repo.get_by_id(device_id)
        if not device or device.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found."
            )
        return device

    async def generate_pairing_code(self, owner_id: str) -> PairingCodeResponse:
        code = generate_pairing_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.DEFAULT_PAIRING_EXPIRY_MINUTES)
        pairing_record = await self.pairing_repo.create(
            owner_id=owner_id,
            code=code,
            expires_at=expires_at
        )
        return PairingCodeResponse(
            pairing_code=pairing_record.code,
            expires_at=pairing_record.expires_at,
            expires_in_seconds=settings.DEFAULT_PAIRING_EXPIRY_MINUTES * 60
        )

    async def claim_pairing_code(self, req: PairingClaimRequest) -> PairingClaimResponse:
        active_code = await self.pairing_repo.get_active_code(req.pairing_code)
        if not active_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired pairing code."
            )

        # Mark code as used
        await self.pairing_repo.mark_used(active_code.id)

        # Check if device ID already exists for this owner or in registry
        existing_device = await self.device_repo.get_by_id(req.device_id)
        device_token = generate_device_token()

        if existing_device:
            if existing_device.owner_id != active_code.owner_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Device ID is already registered to another user."
                )
            # Re-pairing: update existing device
            existing_device.name = req.device_name
            existing_device.type = req.device_type
            existing_device.platform = req.platform
            existing_device.device_token = device_token
            existing_device.capabilities = req.capabilities
            existing_device.version = req.version
            existing_device.status = "connecting"
            existing_device.last_seen = datetime.now(timezone.utc)
            await self.db.flush()
            device = existing_device
        else:
            # Create fresh device
            device = await self.device_repo.create(
                device_id=req.device_id,
                owner_id=active_code.owner_id,
                name=req.device_name,
                type=req.device_type,
                platform=req.platform,
                device_token=device_token,
                capabilities=req.capabilities,
                version=req.version
            )

        ws_url = f"/ws/device?token={device_token}"
        return PairingClaimResponse(
            device_id=device.device_id,
            device_token=device_token,
            ws_url=ws_url,
            message=f"Device '{device.name}' successfully paired."
        )

    async def update_device_name(self, owner_id: str, device_id: str, req: DeviceUpdateRequest) -> Device:
        device = await self.get_device(owner_id, device_id)
        updated = await self.device_repo.update_name(device.device_id, req.name)
        return updated

    async def delete_device(self, owner_id: str, device_id: str) -> bool:
        device = await self.get_device(owner_id, device_id)
        return await self.device_repo.delete(device.device_id)

    async def resolve_device_by_hint(
        self,
        owner_id: str,
        hint: Optional[str] = None
    ) -> Tuple[Optional[Device], Optional[str]]:
        """
        Natural Language Device Resolution.
        Resolves terms like "my laptop", "computer", "phone", or a device name.
        Returns (device, error_message).
        """
        devices = await self.device_repo.list_by_owner(owner_id)
        if not devices:
            return None, "No devices are registered to your account."

        # If no hint provided and only 1 device exists, use it
        if not hint or not hint.strip():
            if len(devices) == 1:
                return devices[0], None
            return None, f"You have {len(devices)} devices. Please specify which device to use."

        hint_clean = hint.lower().strip()

        # 1. Exact match on device_id
        for dev in devices:
            if dev.device_id.lower() == hint_clean:
                return dev, None

        # 2. Exact match on name
        for dev in devices:
            if dev.name.lower() == hint_clean:
                return dev, None

        # 3. Substring / keyword matching
        matches = []
        for dev in devices:
            dev_name = dev.name.lower()
            dev_type = dev.type.lower()
            dev_plat = dev.platform.lower()

            if (hint_clean in dev_name or
                hint_clean in dev_type or
                hint_clean in dev_plat or
                ("laptop" in hint_clean and (dev_type == "computer" or "laptop" in dev_name)) or
                ("computer" in hint_clean and (dev_type == "computer" or "pc" in dev_name)) or
                ("pc" in hint_clean and dev_type == "computer") or
                ("phone" in hint_clean and dev_type == "phone") or
                ("mobile" in hint_clean and dev_type == "phone")):
                matches.append(dev)

        if len(matches) == 1:
            return matches[0], None
        elif len(matches) > 1:
            names = ", ".join([f"'{d.name}'" for d in matches])
            return None, f"I found multiple matching devices ({names}). Which one should I use?"

        return None, f"I couldn't find a device matching '{hint}'. Available devices: {', '.join([d.name for d in devices])}."
