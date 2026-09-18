from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import CommandRecord


class CommandRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        owner_id: str,
        query: str,
        action: Optional[str] = None,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        status: str = "completed",
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> CommandRecord:
        record = CommandRecord(
            owner_id=owner_id,
            query=query,
            action=action,
            device_id=device_id,
            device_name=device_name,
            status=status,
            result=result,
            error=error
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_by_owner(self, owner_id: str, limit: int = 50, offset: int = 0) -> List[CommandRecord]:
        query = (
            select(CommandRecord)
            .where(CommandRecord.owner_id == owner_id)
            .order_by(CommandRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def clear_by_owner(self, owner_id: str) -> int:
        statement = delete(CommandRecord).where(CommandRecord.owner_id == owner_id)
        result = await self.session.execute(statement)
        await self.session.flush()
        return result.rowcount
