from datetime import datetime

from pydantic import BaseModel
from src.models.database import UUID4Str, TaskLinesOfCode, TaskReviewPriority


class GetRewardsResponseItem(BaseModel):
    creator_public_id: UUID4Str
    creator_user_name: str
    lines_of_code: TaskLinesOfCode
    review_priority: TaskReviewPriority
    pr_link: str
    pr_number: int | None
    repo: str | None
    points: int
    was_quick_review: bool
    rewarded_at: datetime
