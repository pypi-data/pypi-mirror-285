import logging
from contextlib import asynccontextmanager
from typing import NewType

from sqlmodel.ext.asyncio.session import AsyncSession

from edgegap_database._configuration import DatabaseConfiguration

from ._async_engine import AsyncDatabaseEngine
from ._async_session_factory import AsyncSessionFactory

logger = logging.getLogger(__name__)

AsyncReadSession = NewType('AsyncReadSession', AsyncSession)
AsyncWriteSession = NewType('AsyncWriteSession', AsyncSession)


class AsyncDatabaseSession:
    @staticmethod
    @asynccontextmanager
    async def get_session(configuration: DatabaseConfiguration):
        engine = AsyncDatabaseEngine(configuration).get_write_engine()
        session = AsyncSession(engine)

        try:
            yield session
        finally:
            await session.close()

    @staticmethod
    @asynccontextmanager
    async def get_write_session(configuration: DatabaseConfiguration, session_factory: AsyncSessionFactory):
        engine = AsyncDatabaseEngine(configuration).get_write_engine()
        session = session_factory.create_session(engine)

        try:
            yield session
        finally:
            await session.close()

    @staticmethod
    @asynccontextmanager
    async def get_read_session(configuration: DatabaseConfiguration, session_factory: AsyncSessionFactory):
        engine = AsyncDatabaseEngine(configuration).get_read_engine()
        session = session_factory.create_session(engine)

        try:
            yield session
        finally:
            await session.close()
