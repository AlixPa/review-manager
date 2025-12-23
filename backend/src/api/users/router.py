from fastapi import APIRouter, Depends, HTTPException, status
from src.config.flags import FLAG_MOCK_TEST_USER
from src.logger import get_logger
from src.models.database import User
from src.modules.authentification import get_current_user

from .exceptions import UserNotFound
from .models import GetUserResponse, GetUsersResponseItem, PatchSetTestUser
from .service import get_users_service, patch_set_test_user_service

router = APIRouter(prefix="/users")
logger = get_logger()


@router.get("", response_model=list[GetUsersResponseItem])
async def get_users() -> list[GetUsersResponseItem]:
    user_reward_ls = await get_users_service()
    return [
        GetUsersResponseItem(
            public_id=u.public_id, user_name=u.user_name, reward_since_last_tuesday=r
        )
        for u, r in user_reward_ls
    ]


@router.get("/me", response_model=GetUserResponse)
async def get_me(user: User = Depends(get_current_user)) -> GetUserResponse:
    logger.info("GET get_me")

    return GetUserResponse(
        public_id=user.public_id,
        user_name=user.user_name,
    )


@router.patch("/set_test_user", status_code=status.HTTP_204_NO_CONTENT)
async def patch_set_test_user(request: PatchSetTestUser) -> None:
    if not FLAG_MOCK_TEST_USER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        await patch_set_test_user_service(request.test_user_id)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
