from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from src.config.auth import auth_config
from src.config.env import ENV, ServiceEnv
from src.config.flags import flags_config
from src.logger import get_logger
from src.models.database import User
from src.models.jwt import JwtPlayload
from src.modules.authentification import (
    delete_loging_cookies,
    get_current_user,
    set_login_cookies,
)

from .exceptions import UserNotFound
from .models import GetUserResponse, GetUsersResponseItem, PatchSetUser
from .service import get_users_service, patch_set_user_service

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


@router.patch("/set_user", response_class=RedirectResponse)
async def patch_set_user(request: PatchSetUser) -> RedirectResponse:
    if not flags_config.development_login:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        user = await patch_set_user_service(request.user_public_id)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    response = RedirectResponse(auth_config.callback_redirect)
    response = delete_loging_cookies(response)
    response = set_login_cookies(response, user)

    return response
