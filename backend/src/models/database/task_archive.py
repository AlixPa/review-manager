from datetime import datetime

from pydantic import Field

from .base import BaseTableModel
from .types import TaskLinesOfCode, TaskReviewPriority, TaskState, TinyBool


class TaskArchive(BaseTableModel):
    __tablename__: str = "task_archives"

    task_id: int = Field(alias="id")
    creator_id: int
    review_priority: TaskReviewPriority
    lines_of_code: TaskLinesOfCode
    has_been_reviewed_once: TinyBool
    pr_link: str
    state: TaskState
    task_created_at: datetime = Field(alias="created_at")
    task_approved_at: datetime | None = Field(alias="approved_at")
