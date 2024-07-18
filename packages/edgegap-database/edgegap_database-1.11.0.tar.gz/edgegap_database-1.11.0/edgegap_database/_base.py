from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel, AsyncAttrs, table=False):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={'server_default': sa.func.now()},
        nullable=False,
        description='Timestamp when the object was created.',
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now(),
        },
        description='Timestamp when the object was last updated.',
    )
