import logging
from contextlib import contextmanager
from typing import NewType

from sqlmodel import Session

from ._configuration import DatabaseConfiguration
from ._engine import DatabaseEngine
from ._session_factory import SessionFactory

logger = logging.getLogger(__name__)

ReadSession = NewType('ReadSession', Session)
WriteSession = NewType('WriteSession', Session)


class DatabaseSession:
    @staticmethod
    @contextmanager
    def get_session(configuration: DatabaseConfiguration):
        engine = DatabaseEngine(configuration).get_write_engine()
        session = Session(engine)

        try:
            yield session
        finally:
            session.close()

    @staticmethod
    @contextmanager
    def get_write_session(configuration: DatabaseConfiguration, session_factory: SessionFactory):
        engine = DatabaseEngine(configuration).get_write_engine()
        session = session_factory.create_session(engine)

        try:
            yield session
        finally:
            session.close()

    @staticmethod
    @contextmanager
    def get_read_session(configuration: DatabaseConfiguration, session_factory: SessionFactory):
        engine = DatabaseEngine(configuration).get_read_engine()
        session = session_factory.create_session(engine)

        try:
            yield session
        finally:
            session.close()
