from datetime import datetime

from pydantic import BaseModel
from src.models.database import UUID4Str


class GetUsersResponseItem(BaseModel):
    public_id: UUID4Str
    user_name: str
    reward_since_last_tuesday: int


class GetUserResponse(BaseModel):
    public_id: UUID4Str
    user_name: str


class PatchSetTestUser(BaseModel):
    test_user_id: int
