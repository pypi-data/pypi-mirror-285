from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from ._configuration import DatabaseConfiguration


class DatabaseEngine:
    __mapping__: dict[str, '__Engine'] = {}
    __instance: '__Engine'

    class __Engine:
        def __init__(self, configuration: DatabaseConfiguration):
            self.__configuration = configuration
            self.__write_engine = create_engine(
                url=str(self.__configuration.uri),
                connect_args=self.__configuration.args or {},
                poolclass=self.__configuration.pool_class or None,
            )
            # https://github.com/sqlalchemy/sqlalchemy/discussions/6921#discussioncomment-1223234
            self.__read_engine = self.__write_engine.execution_options(isolation_level='AUTOCOMMIT')

        def get_engine_write_engine(self) -> Engine:
            """
            Get an engine that can be used for writing to the database. This will be executed in transaction mode.
            """
            return self.__write_engine

        def get_read_engine(self) -> Engine:
            """
            Get an engine that can be used for reading from the database. This will be executed in AUTOCOMMIT
            isolation_level mode.
            """
            return self.__read_engine

    def __init__(self, configuration: DatabaseConfiguration):
        key = configuration.application

        if key not in DatabaseEngine.__mapping__:
            DatabaseEngine.__mapping__[key] = self.__Engine(configuration)

        self.__key = key

    def get_engine(self) -> Engine:
        """
        Same as get_write_engine
        """
        return self.get_write_engine()

    def get_write_engine(self) -> Engine:
        """
        Get an engine that can be used for writing to the database. This will be executed in transaction mode.
        """
        instance: DatabaseEngine.__Engine = DatabaseEngine.__mapping__.get(self.__key)

        return instance.get_engine_write_engine()

    def get_read_engine(self) -> Engine:
        """
        Get an engine that can be used for reading from the database. This will be executed in AUTOCOMMIT
        isolation_level mode.
        """
        instance: DatabaseEngine.__Engine = DatabaseEngine.__mapping__.get(self.__key)

        return instance.get_read_engine()
