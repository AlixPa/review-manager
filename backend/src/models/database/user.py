from datetime import datetime, timezone

from pydantic import Field

from .base import BaseTableModel
from .types import UUID4Str


class User(BaseTableModel):
    __tablename__: str = "users"

    public_id: UUID4Str = Field(default_factory=lambda: UUID4Str.new())
    email: str | None = Field(default=None, max_length=255)
    google_sub: str | None = Field(default=None, max_length=255)
    user_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
