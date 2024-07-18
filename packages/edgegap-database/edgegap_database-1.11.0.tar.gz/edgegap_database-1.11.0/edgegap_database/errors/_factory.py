from sqlalchemy.exc import DatabaseError, IntegrityError

from ._exceptions import DatabaseException, DatabaseUniqueViolationExceptions


class DatabaseExceptionFactory:
    @staticmethod
    def handle(e: Exception):
        match e:
            case IntegrityError():
                raise DatabaseUniqueViolationExceptions(exception=e) from e
            case DatabaseError():
                raise DatabaseException(exception=e) from e
            case _:
                raise e
