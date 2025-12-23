from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from src.models.database import TaskLinesOfCode, TaskReviewPriority, UUID4Str


class PostTaskRequest(BaseModel):
    pr_link: str
    priority: TaskReviewPriority
    lines_of_code: TaskLinesOfCode
    reviewers_id: list[UUID4Str]


class GetTasksCommonResponseItemReviewer(BaseModel):
    public_id: UUID4Str
    user_name: str


class GetTasksCommonResponseItem(BaseModel):
    task_id: int
    creator_user_name: str
    creator_public_id: str
    review_priority: int
    lines_of_code: TaskLinesOfCode
    has_been_reviewed_once: bool
    created_at: datetime
    approved_at: datetime | None
    state: int
    reward: int
    pr_link: str
    pr_number: int | None
    github_repo: str | None
    reviewers: list[GetTasksCommonResponseItemReviewer]


class GetMyTasksResponseItem(GetTasksCommonResponseItem):
    pass


class GetTodoResponseItem(GetTasksCommonResponseItem):
    pass


class UpdateAction(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    CHANGES_ADDRESSED = "changes_addressed"
    RE_OPEN_QUICK_REVIEW = "re_open_quick_review"
    RE_OPEN_RESET_REVIEW = "re_open_reset_review"


class PatchUpdateRequest(BaseModel):
    action: UpdateAction
