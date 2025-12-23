from datetime import datetime, timezone

import jwt
from fastapi import Cookie, HTTPException
from src.clients.mysql import AMysqlClientReader, AMySqlIdNotFoundError
from src.config.auth import auth_config
from src.config.flags import FLAG_MOCK_TEST_USER
from src.config.path import path_config
from src.models.database import User, UUID4Str
from src.models.jwt import JwtPlayload


async def get_current_user(
    session: str = Cookie(None, alias=auth_config.session.session_token_keyword)
) -> User:
    if FLAG_MOCK_TEST_USER:
        try:
            with open(path_config.current_mock_user_json_file, "r") as f:
                return User.model_validate_json(f.read())
        except Exception as e:
            raise ValueError(f"Could not load mock user. {type(e)}, {str(e)}")
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
