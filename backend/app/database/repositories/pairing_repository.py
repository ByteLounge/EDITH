from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import PairingCode


class PairingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, owner_id: str, code: str, expires_at: datetime) -> PairingCode:
        pairing_code = PairingCode(
            owner_id=owner_id,
            code=code,
            expires_at=expires_at,
            is_used=False
        )
        self.session.add(pairing_code)
        await self.session.flush()
        return pairing_code

    async def get_active_code(self, code: str) -> Optional[PairingCode]:
        now = datetime.now(timezone.utc)
        query = select(PairingCode).where(
            PairingCode.code == code,
            PairingCode.is_used == False,
            PairingCode.expires_at > now
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def mark_used(self, pairing_code_id: str) -> Optional[PairingCode]:
        query = select(PairingCode).where(PairingCode.id == pairing_code_id)
        result = await self.session.execute(query)
        record = result.scalar_one_or_none()
        if record:
            record.is_used = True
            await self.session.flush()
        return record
