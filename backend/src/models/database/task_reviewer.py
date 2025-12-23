from .base import BaseTableModel


class TaskReviewer(BaseTableModel):
    __tablename__: str = "task_reviewers"

    user_id: int
    task_id: int
