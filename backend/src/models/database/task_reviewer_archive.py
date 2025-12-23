from pydantic import Field

from .base import BaseTableModel


class TaskReviewerArchive(BaseTableModel):
    __tablename__: str = "task_reviewer_archives"

    task_reviewers_id: int = Field(alias="id")
    user_id: int
    task_id: int
