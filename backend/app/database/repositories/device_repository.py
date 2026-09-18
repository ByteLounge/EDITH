from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Device


class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        query = select(Device).where(Device.device_id == device_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_token(self, device_token: str) -> Optional[Device]:
        query = select(Device).where(Device.device_token == device_token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: str) -> List[Device]:
        query = select(Device).where(Device.owner_id == owner_id).order_by(Device.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        device_id: str,
        owner_id: str,
        name: str,
        type: str,
        platform: str,
        device_token: str,
        capabilities: Optional[List[str]] = None,
        version: str = "1.0.0"
    ) -> Device:
        device = Device(
            device_id=device_id,
            owner_id=owner_id,
            name=name,
            type=type,
            platform=platform,
            device_token=device_token,
            capabilities=capabilities or [],
            version=version,
            status="offline"
        )
        self.session.add(device)
        await self.session.flush()
        return device

    async def update_status(
        self,
        device_id: str,
        status: str,
        connection_id: Optional[str] = None
    ) -> Optional[Device]:
        device = await self.get_by_id(device_id)
        if device:
            device.status = status
            device.last_seen = datetime.now(timezone.utc)
            if connection_id is not None:
                device.connection_id = connection_id
            await self.session.flush()
        return device

    async def update_capabilities(self, device_id: str, capabilities: List[str]) -> Optional[Device]:
        device = await self.get_by_id(device_id)
        if device:
            device.capabilities = capabilities
            device.last_seen = datetime.now(timezone.utc)
            await self.session.flush()
        return device

    async def update_name(self, device_id: str, name: str) -> Optional[Device]:
        device = await self.get_by_id(device_id)
        if device:
            device.name = name
            await self.session.flush()
        return device

    async def delete(self, device_id: str) -> bool:
        device = await self.get_by_id(device_id)
        if device:
            await self.session.delete(device)
            await self.session.flush()
            return True
        return False
