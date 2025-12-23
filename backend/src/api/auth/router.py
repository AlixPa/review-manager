import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from src.config.auth import auth_config
from src.config.env import ENV, ServiceEnv
from src.logger import get_logger
from src.models.jwt import JwtPlayload
from src.modules.authentification import delete_loging_cookies, set_login_cookies

from .service import auth_google_callback_service

router = APIRouter(prefix="/auth")
logger = get_logger()


@router.get("/google/login", response_class=RedirectResponse)
async def auth_google_login() -> RedirectResponse:
    logger.info(f"GET auth_google_login")
    state = secrets.token_urlsafe(16)
    params = urlencode(
        {
            "client_id": auth_config.google.client_id,
            "redirect_uri": auth_config.google.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    response = RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    )
    response.set_cookie(
        auth_config.session.oauth_state_keyword, state, httponly=True, samesite="lax"
    )
    return response


@router.get("/google/callback", response_class=RedirectResponse)
async def auth_google_callback(
    code: str, state: str, request: Request
) -> RedirectResponse:
    logger.info(f"GET auth_google_callback")

    state_cookie = request.cookies.get(auth_config.session.oauth_state_keyword)
    if state_cookie != state:
        raise HTTPException(status_code=400, detail="Invalid state")

    user = await auth_google_callback_service(code)

    response = RedirectResponse(auth_config.callback_redirect)
    response = delete_loging_cookies(response)
    response = set_login_cookies(response, user)

    return response


@router.get("/logout", response_class=RedirectResponse)
async def logout() -> RedirectResponse:
    logger.info(f"GET logout")
    response = RedirectResponse(auth_config.logout_redirect)
    response = delete_loging_cookies(response)
    return response
