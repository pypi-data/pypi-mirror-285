from sqlalchemy.exc import DBAPIError


class DatabaseException(Exception):
    default_message = 'Database Exception'

    def __init__(self, message: str | None = None, exception: type(DBAPIError) = None):
        default_message = str(exception) if exception is not None else self.default_message
        self.message = message or default_message
        self.db_exception = exception


class DatabaseConfigurationExceptions(DatabaseException):
    default_message = 'Database Configuration Exception, please verify your configuration'


class DatabaseUniqueViolationExceptions(DatabaseException):
    default_message = 'Database Unique Violation Exception, please verify your Unique Violation'
