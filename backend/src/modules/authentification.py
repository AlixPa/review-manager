from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Cookie, HTTPException
from fastapi.responses import RedirectResponse
from src.clients.mysql import AMysqlClientReader, AMySqlIdNotFoundError
from src.config.auth import auth_config
from src.config.env import ENV, ServiceEnv
from src.models.database import User
from src.models.jwt import JwtPlayload


async def get_current_user(
    session: str = Cookie(None, alias=auth_config.session.session_token_keyword)
) -> User:
    if not session:
        raise HTTPException(401, "Not logged in")

    try:
        jwt_payload = JwtPlayload(
            **jwt.decode(
                session,
                auth_config.jwt.secret_key,
                algorithms=[auth_config.jwt.algorithm],
            )
        )
    except:
        raise HTTPException(401, "Invalid session")

    ## TODO: do something
    if jwt_payload.exp > datetime.now(timezone.utc):
        pass

    reader = AMysqlClientReader()

    try:
        return await reader.select_by_id(table=User, id=jwt_payload.user_id)
    except AMySqlIdNotFoundError:
        raise HTTPException(401, "User not found")


def set_login_cookies(response: RedirectResponse, user: User) -> RedirectResponse:
    jwt_playload = JwtPlayload(
        user_id=user.id,
        exp=datetime.now(timezone.utc)
        + timedelta(days=auth_config.session.expiration_days),
    )
    jwt_token = jwt.encode(
        payload=jwt_playload.model_dump(),
        key=auth_config.jwt.secret_key,
        algorithm=auth_config.jwt.algorithm,
    )

    response.set_cookie(
        key=auth_config.session.session_token_keyword,
        value=jwt_token,
        httponly=True,
        secure=ENV != ServiceEnv.LOCAL,
        samesite="lax",
        max_age=3600 * 24 * auth_config.session.expiration_days,
        domain=None,  # TODO: needed if backend/frontend different domains
    )
    return response


def delete_loging_cookies(response: RedirectResponse) -> RedirectResponse:
    response.delete_cookie(
        key=auth_config.session.session_token_keyword,
        httponly=True,
        secure=ENV != ServiceEnv.LOCAL,
        samesite="lax",
        domain=None,
    )
    return response
