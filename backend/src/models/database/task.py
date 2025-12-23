from datetime import datetime, timezone

from pydantic import Field

from .base import BaseTableModel
from .types import TaskLinesOfCode, TaskReviewPriority, TaskState, TinyBool


class Task(BaseTableModel):
    __tablename__: str = "tasks"

    creator_id: int
    review_priority: TaskReviewPriority
    lines_of_code: TaskLinesOfCode
    has_been_reviewed_once: TinyBool = False
    pr_link: str
    state: TaskState
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: datetime | None = None

    def calculate_reward(self) -> int:
        match self.review_priority:
            # Approve only is no big money
            case TaskReviewPriority.APPROVE_ONLY:
                return 5
            # Based on evidendence is medium money
            case TaskReviewPriority.BASED_ON_EVIDENCE:
                if self.has_been_reviewed_once:
                    return 10
                match self.lines_of_code:
                    case TaskLinesOfCode.UNDER_100:
                        return 10
                    case TaskLinesOfCode.UNDER_500:
                        return 15
                    case TaskLinesOfCode.UNDER_1200:
                        return 20
                    case TaskLinesOfCode.ABOVE_1200:
                        return 25
            # Full review is big money
            case TaskReviewPriority.FULL_REVIEW:
                # Full review on big pr is muri
                if self.lines_of_code == TaskLinesOfCode.ABOVE_1200:
                    raise ValueError("Cannot full review, too many lines.")
                if self.has_been_reviewed_once:
                    return 10
                match self.lines_of_code:
                    case TaskLinesOfCode.UNDER_100:
                        return 15
                    case TaskLinesOfCode.UNDER_500:
                        return 30
                    case TaskLinesOfCode.UNDER_1200:
                        return 60
