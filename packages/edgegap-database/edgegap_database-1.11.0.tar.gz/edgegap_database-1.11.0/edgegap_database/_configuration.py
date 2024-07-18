import logging
from typing import Any

from pydantic import BaseModel, Field, PostgresDsn

from .models import SQLiteDsn

logger = logging.getLogger(__name__)


class DatabaseConfiguration(BaseModel):
    uri: SQLiteDsn | PostgresDsn | str = Field(..., description='The URI of the database')
    async_uri: SQLiteDsn | PostgresDsn | str | None = Field(None, description='The Async URI of the database')
    application: str = Field(..., description='The Name of the Application for the DB connection')
    args: dict = Field(default={}, description='Extra Arguments for the DB connection')
    pool_class: Any | None = Field(default=None, description='The Pool class for the DB connection')
