from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email.lower().strip())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name
        )
        self.session.add(user)
        await self.session.flush()
        return user
