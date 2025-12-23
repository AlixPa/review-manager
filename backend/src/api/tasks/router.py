from fastapi import APIRouter, Depends, HTTPException, status
from src.logger import get_logger
from src.models.database import TaskState, User
from src.modules.authentification import get_current_user
from src.modules.normalize_url import normalize_github_url

from .exceptions import (
    CreatorNotFound,
    PrLinkAlreadyExists,
    TaskAndUserMismatch,
    TaskNotFound,
    UserNotReviewer,
)
from .models import (
    GetMyTasksResponseItem,
    GetTasksCommonResponseItemReviewer,
    GetTodoResponseItem,
    PatchUpdateRequest,
    PostTaskRequest,
)
from .service import (
    delete_task_service,
    get_created_service,
    get_todo_service,
    patch_task_service,
    post_task_service,
)

router = APIRouter(prefix="/tasks")
logger = get_logger()


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def post_task(
    request: PostTaskRequest, user: User = Depends(get_current_user)
) -> None:
    logger.info(f"POST post_task, {request!r}")

    try:
        await post_task_service(
            user,
            request.pr_link,
            request.priority,
            request.lines_of_code,
            request.reviewers_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )
    except PrLinkAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A task with this PR link already exists.",
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, user: User = Depends(get_current_user)) -> None:
    try:
        await delete_task_service(user, task_id)
    except TaskNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found.",
        )
    except TaskAndUserMismatch:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User not authorized to perfom action on the task.",
        )


@router.patch("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_task(
    task_id: int, request: PatchUpdateRequest, user: User = Depends(get_current_user)
) -> None:
    logger.info(f"GET patch_task, {task_id=} {request!r}")

    try:
        await patch_task_service(user, task_id, request.action)
    except (TaskNotFound, CreatorNotFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task or creator not found.",
        )
    except (TaskAndUserMismatch, UserNotReviewer):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User not authorized to perfom action on the task.",
        )


@router.get("/todo", response_model=list[GetTodoResponseItem])
async def get_todo(
    state: TaskState, user: User = Depends(get_current_user)
) -> list[GetTodoResponseItem]:
    logger.info(f"GET get_todo, {state!r}")

    task_user_reviewers_ls = await get_todo_service(user, state)
    return [
        GetTodoResponseItem(
            task_id=t.id,
            creator_user_name=u.user_name,
            creator_public_id=u.public_id,
            review_priority=t.review_priority,
            lines_of_code=t.lines_of_code,
            created_at=t.created_at,
            approved_at=t.approved_at,
            state=t.state.value,
            reward=t.calculate_reward(),
            has_been_reviewed_once=t.has_been_reviewed_once,
            pr_link=t.pr_link,
            pr_number=gu.pull_request_number if gu else None,
            github_repo=gu.repo if gu else None,
            reviewers=[
                GetTasksCommonResponseItemReviewer(
                    public_id=r.public_id, user_name=r.user_name
                )
                for r in rs
            ],
        )
        for t, u, gu, rs in [
            (t, u, normalize_github_url(t.pr_link), rs)
            for t, u, rs in task_user_reviewers_ls
        ]
    ]


@router.get("/my_tasks", response_model=list[GetMyTasksResponseItem])
async def get_created(
    state: TaskState, user: User = Depends(get_current_user)
) -> list[GetMyTasksResponseItem]:
    logger.info(f"GET get_created, {state!r}")

    task_reviewers_ls = await get_created_service(user, state)
    return [
        GetMyTasksResponseItem(
            task_id=t.id,
            creator_user_name=user.user_name,
            creator_public_id=user.public_id,
            review_priority=t.review_priority,
            lines_of_code=t.lines_of_code,
            created_at=t.created_at,
            approved_at=t.approved_at,
            state=t.state.value,
            reward=t.calculate_reward(),
            has_been_reviewed_once=t.has_been_reviewed_once,
            pr_link=t.pr_link,
            github_repo=gu.repo if gu else None,
            pr_number=gu.pull_request_number if gu else None,
            reviewers=[
                GetTasksCommonResponseItemReviewer(
                    public_id=r.public_id, user_name=r.user_name
                )
                for r in rs
            ],
        )
        for t, rs, gu in [
            (t, rs, normalize_github_url(t.pr_link)) for t, rs in task_reviewers_ls
        ]
    ]
