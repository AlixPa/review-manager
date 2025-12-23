from datetime import datetime, timezone

from pydantic import Field

from .base import BaseTableModel
from .types import TaskLinesOfCode, TaskReviewPriority, TinyBool, UUID4Str


class Reward(BaseTableModel):
    __tablename__: str = "rewards"

    user_id: int
    task_id: int
    points: int
    pr_link: str
    was_quick_review: TinyBool
    creator_public_id: UUID4Str
    creator_user_name: str
    review_priority: TaskReviewPriority
    lines_of_code: TaskLinesOfCode
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
