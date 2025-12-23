from datetime import datetime, timezone

from src.clients.mysql import (
    AMysqlClientReader,
    AMysqlClientWriter,
    AMySqlDuplicateError,
    AMySqlIdNotFoundError,
)
from src.models.database import (
    Reward,
    Task,
    TaskArchive,
    TaskLinesOfCode,
    TaskReviewer,
    TaskReviewerArchive,
    TaskReviewPriority,
    TaskState,
    User,
    UUID4Str,
)
from src.modules.normalize_url import normalize_github_url

from .exceptions import (
    CreatorNotFound,
    PrLinkAlreadyExists,
    TaskAndUserMismatch,
    TaskNotFound,
    UserNotReviewer,
)
from .models import UpdateAction


async def post_task_service(
    user: User,
    pr_link: str,
    priority: TaskReviewPriority,
    lines_of_code: TaskLinesOfCode,
    reviewers_id: list[UUID4Str],
) -> None:
    reviewers_id = [ri for ri in reviewers_id if ri != user.public_id]
    if not reviewers_id:
        raise ValueError("Cannot post a task without reviewers selected.")
    if not (github_url := normalize_github_url(pr_link)):
        raise ValueError("Unvalid pr link.")
    if (
        priority == TaskReviewPriority.FULL_REVIEW
        and lines_of_code == TaskLinesOfCode.ABOVE_1200
    ):
        raise ValueError("Cannot do full review on more than 1200 lines of code pr.")

    reader = AMysqlClientReader()
    users = await reader.select(table=User, cond_in=dict(public_id=reviewers_id))

    writer = AMysqlClientWriter()

    pr_link = f"https://github.com/{github_url.owner}/{github_url.repo}/pull/{github_url.pull_request_number}"
    task = Task(
        creator_id=user.id,
        review_priority=priority,
        lines_of_code=lines_of_code,
        pr_link=pr_link,
        state=TaskState.PENDING_REVIEW,
    )

    try:
        await writer.insert_one(task)
    except AMySqlDuplicateError:
        raise PrLinkAlreadyExists()

    task_reviewers = [TaskReviewer(user_id=u.id, task_id=task.id) for u in users]

    await writer.insert(task_reviewers)


async def get_todo_service(
    user: User, state: TaskState
) -> list[tuple[Task, User, list[User]]]:
    """
    Returns tasks assignated to the user.
    tuples of (task, task creator, task reviewers)
    """
    reader = AMysqlClientReader()

    user_task_reviewers = await reader.select(
        table=TaskReviewer, cond_equal=dict(user_id=user.id)
    )

    tasks = await reader.select(
        table=Task,
        cond_in=dict(id=list({r.task_id for r in user_task_reviewers})),
        cond_equal=dict(state=state.value),
    )
    tasks_reviewers = await reader.select(
        table=TaskReviewer, cond_in=dict(task_id=[t.id for t in tasks])
    )

    users = await reader.select(
        table=User,
        cond_in=dict(
            id=list(
                {t.creator_id for t in tasks}.union(
                    {tr.user_id for tr in tasks_reviewers}
                )
            )
        ),
    )
    user_id_to_user_map: dict[int, User] = {u.id: u for u in users}

    return [
        (
            t,
            user_id_to_user_map[t.creator_id],
            [
                user_id_to_user_map[tr.user_id]
                for tr in tasks_reviewers
                if tr.task_id == t.id
            ],
        )
        for t in tasks
    ]


async def get_created_service(
    user: User, state: TaskState
) -> list[tuple[Task, list[User]]]:
    """
    Return tasks with their list of reviewers
    """
    reader = AMysqlClientReader()

    tasks = await reader.select(
        table=Task, cond_equal=dict(creator_id=user.id, state=state.value)
    )

    task_reviewers = await reader.select(
        table=TaskReviewer,
        cond_in=dict(task_id=[t.id for t in tasks]),
        cond_non_equal=dict(user_id=user.id),
    )

    users = await reader.select(
        table=User, cond_in=dict(id=list({u.user_id for u in task_reviewers}))
    )
    user_id_to_user_map: dict[int, User] = {u.id: u for u in users}

    task_id_to_reviewers_map: dict[int, list[User]] = dict()
    for tr in task_reviewers:
        task_id_to_reviewers_map.setdefault(tr.task_id, list()).append(
            user_id_to_user_map[tr.user_id]
        )

    return [(t, task_id_to_reviewers_map[t.id]) for t in tasks]


async def _validate_and_get_task(
    user: User, task_id: int, *, task_belongs_to_user: bool
) -> Task:
    reader = AMysqlClientReader()

    try:
        task = await reader.select_by_id(table=Task, id=task_id)
    except AMySqlIdNotFoundError:
        raise TaskNotFound()

    if task.creator_id != user.id and task_belongs_to_user:
        raise TaskAndUserMismatch()

    return task


async def _patch_approval_service(user: User, task_id: int, *, approved: bool) -> None:
    task = await _validate_and_get_task(user, task_id, task_belongs_to_user=False)

    reader = AMysqlClientReader()

    try:
        creator = await reader.select_by_id(table=User, id=task.creator_id)
    except AMySqlIdNotFoundError:
        raise CreatorNotFound()

    if not await reader.select(
        table=TaskReviewer, cond_equal=dict(user_id=user.id, task_id=task.id)
    ):
        raise UserNotReviewer()

    writer = AMysqlClientWriter()

    await writer.insert_one(
        Reward(
            user_id=user.id,
            task_id=task.id,
            points=task.calculate_reward(),
            was_quick_review=task.has_been_reviewed_once,
            pr_link=task.pr_link,
            creator_public_id=creator.public_id,
            creator_user_name=creator.user_name,
            review_priority=task.review_priority,
            lines_of_code=task.lines_of_code,
        )
    )

    state = TaskState.APPROVED.value if approved else TaskState.PENDING_CHANGES.value
    approved_at = datetime.now(timezone.utc) if approved else None
    await writer.update_by_id(
        table=Task,
        id=task.id,
        col_to_value_map=dict(
            has_been_reviewed_once=1, state=state, approved_at=approved_at
        ),
    )


async def _patch_changes_addressed_service(user: User, task_id: int) -> None:
    task = await _validate_and_get_task(user, task_id, task_belongs_to_user=True)

    writer = AMysqlClientWriter()

    await writer.update_by_id(
        table=Task,
        id=task.id,
        col_to_value_map=dict(state=TaskState.PENDING_REVIEW.value),
    )


async def _patch_task_re_open(
    user: User, task_id: int, *, reset_has_been_reviewed_once: bool
) -> None:
    task = await _validate_and_get_task(user, task_id, task_belongs_to_user=True)

    writer = AMysqlClientWriter()

    await writer.update_by_id(
        table=Task,
        id=task.id,
        col_to_value_map=dict(
            state=TaskState.PENDING_REVIEW.value,
            approved_at=None,
            has_been_reviewed_once=not reset_has_been_reviewed_once,
        ),
    )


async def patch_task_service(user: User, task_id: int, action: UpdateAction) -> None:
    match action:
        case UpdateAction.APPROVE:
            await _patch_approval_service(user, task_id, approved=True)
        case UpdateAction.REQUEST_CHANGES:
            await _patch_approval_service(user, task_id, approved=False)
        case UpdateAction.CHANGES_ADDRESSED:
            await _patch_changes_addressed_service(user, task_id)
        case UpdateAction.RE_OPEN_QUICK_REVIEW:
            await _patch_task_re_open(user, task_id, reset_has_been_reviewed_once=False)
        case UpdateAction.RE_OPEN_RESET_REVIEW:
            await _patch_task_re_open(user, task_id, reset_has_been_reviewed_once=True)


async def delete_task_service(user: User, task_id: int) -> None:
    task = await _validate_and_get_task(user, task_id, task_belongs_to_user=True)

    writer = AMysqlClientWriter()

    await writer.delete_by_id(table=Task, id=task.id)
    task_reviewers = await writer.delete(
        table=TaskReviewer, cond_equal=dict(task_id=task.id)
    )

    await writer.insert_one(
        TaskArchive.model_validate(task.model_dump(), by_alias=True)
    )
    await writer.insert(
        [
            TaskReviewerArchive.model_validate(tr.model_dump(), by_alias=True)
            for tr in task_reviewers
        ]
    )
