from typing import Annotated

from fastapi import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connections import DBSessionsDep
from database.models.user import User


class QueriesService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_new_user(self, user: User) -> None:
        '''Создает нового пользователя'''
        self.db.add(instance=user)
        await self.db.commit()
        
    async def get_user_by_username(self, username: str) -> User | None:
        '''Возвращает пользователя по username'''
        query = Select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
            
    
def get_queries_service(db: DBSessionsDep) -> QueriesService:
    return QueriesService(db=db)


QueriesServiceDep = Annotated[QueriesService, Depends(get_queries_service)]
