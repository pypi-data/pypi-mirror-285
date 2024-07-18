import abc

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


class AsyncSessionFactory(abc.ABC):
    @abc.abstractmethod
    def create_session(self, engine: AsyncEngine) -> AsyncSession:
        pass


class AsyncDefaultSessionFactory(AsyncSessionFactory):
    """
    Default factory will use async session maker to create a session. Parameters are passed to the async session maker
    class_=AsyncSession, bind=engine, future=True
    """

    def create_session(self, engine: AsyncEngine) -> AsyncSession:
        session_maker = async_sessionmaker(class_=AsyncSession, bind=engine, future=True)

        return session_maker()
