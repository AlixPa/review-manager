from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_serializer, field_validator


class BaseTableModel(BaseModel):
    __tablename__: str

    id: int = Field(default_factory=lambda: -1)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_datetimes(cls, v):
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)
        return v

    @field_serializer("*", when_used="always")
    def serialize_enums(self, v):
        if isinstance(v, Enum):
            return v.value
        return v
