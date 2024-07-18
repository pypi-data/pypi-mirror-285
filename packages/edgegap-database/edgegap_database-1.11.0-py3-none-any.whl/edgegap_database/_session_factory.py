import abc

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session


class SessionFactory(abc.ABC):
    @abc.abstractmethod
    def create_session(self, engine: Engine) -> Session:
        pass


class DefaultSessionFactory(SessionFactory):
    """
    Default factory will use session maker to create a session. Parameters are passed to the session maker
    class_=Session, bind=engine, future=True
    """

    def create_session(self, engine: Engine) -> Session:
        session_maker = sessionmaker(class_=Session, bind=engine, future=True)

        return session_maker()
