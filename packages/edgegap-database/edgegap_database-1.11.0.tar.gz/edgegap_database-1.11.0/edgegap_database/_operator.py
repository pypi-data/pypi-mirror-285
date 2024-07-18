import logging
from contextlib import contextmanager
from typing import Any, TypeVar

from sqlalchemy.engine import ScalarResult, TupleResult
from sqlmodel import Session, SQLModel
from sqlmodel.sql import expression

from .errors import DatabaseExceptionFactory

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=SQLModel)


class DatabaseOperator:
    def __init__(self, session: Session):
        self.__session = session

    @contextmanager
    def handle_exception(self):
        try:
            yield
        except Exception as e:
            DatabaseExceptionFactory.handle(e)

    def all(self, statement: expression.Select | expression.SelectOfScalar) -> Any:
        return self.__session.exec(statement).all()

    def first(self, statement: expression.Select | expression.SelectOfScalar) -> Any:
        return self.__session.exec(statement).first()

    def exec(self, statement: expression.Select | expression.SelectOfScalar) -> TupleResult | ScalarResult:
        result = self.__session.exec(statement)
        self.__session.commit()

        return result

    def create(self, model: T) -> T:
        with self.handle_exception():
            self.__session.add(model)
            self.__session.commit()
            self.__session.refresh(model)

            return model

    def update(self, model: T) -> T:
        with self.handle_exception():
            self.__session.add(model)
            self.__session.commit()
            self.__session.refresh(model)

            return model

    def update_many(self, models: list[T]) -> list[T]:
        with self.handle_exception():
            for model in models:
                self.__session.add(model)

            self.__session.commit()

            for model in models:
                self.__session.refresh(model)

            return models

    def delete(self, model: T) -> T:
        with self.handle_exception():
            self.__session.delete(model)
            self.__session.commit()

            return model

    def delete_many(self, models: list[T]) -> list[T]:
        with self.handle_exception():
            for model in models:
                self.__session.delete(model)

            self.__session.commit()

            return models
