import logging

from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl

from ._configuration import DatabaseConfiguration
from .models import SQLiteDsn

logger = logging.getLogger(__name__)


class DatabaseConfigurationFactory:
    @staticmethod
    def __parse(conf: DatabaseConfiguration) -> DatabaseConfiguration:
        if conf.uri.startswith('postgresql'):
            conf.args.update({
                'application_name': conf.application,
                'options': '-c timezone=utc',
            })

        return conf

    @classmethod
    def from_uri(cls, uri: str | MultiHostUrl | PostgresDsn | SQLiteDsn, name: str) -> DatabaseConfiguration:
        configuration = DatabaseConfiguration(uri=str(uri), application=name)

        return cls.__parse(configuration)
