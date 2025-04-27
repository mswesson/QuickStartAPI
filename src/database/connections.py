from functools import lru_cache
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings


class DataBase:
    def __init__(self, url: str) -> None:
        self.url = url
        self.engine = create_async_engine(self.url, echo=settings.DEBUG)
        self.session_factory = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        '''Генератор асинхронной сессии для Depends'''
        async with self.session_factory() as session:
            yield session


class DevDatabase(DataBase):
    def __init__(self):
        super().__init__(settings.DATABASE_DEV_URL)


class ProdDatabase(DataBase):
    def __init__(self):
        super().__init__(settings.DATABASE_PROD_URL)


@lru_cache
def get_db_instance() -> DataBase:
    return DevDatabase() if settings.DEBUG else ProdDatabase()


async def get_db(db_instance: DataBase = Depends(get_db_instance)) -> AsyncGenerator[AsyncSession]:    
    async for session in db_instance.get_session():
        yield session


DBSessionsDep = Annotated[AsyncSession, Depends(get_db)]
