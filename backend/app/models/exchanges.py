from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class ExchangeBase(SQLModel):
    code: str = Field(unique=True, index=True, max_length=20)
    name: str = Field(max_length=100)
    country: str | None = Field(default=None, max_length=50)
    timezone: str | None = Field(default=None, max_length=50)
    is_active: bool = True


class ExchangeCreate(ExchangeBase):
    pass


class ExchangeUpdate(SQLModel):
    code: str | None = Field(default=None, max_length=20)
    name: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=50)
    timezone: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class Exchange(ExchangeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class ExchangePublic(ExchangeBase):
    id: int
    created_at: datetime


class ExchangesPublic(SQLModel):
    data: list[ExchangePublic]
    count: int
