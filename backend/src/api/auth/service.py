import httpx
from src.clients.mysql.async_client import AMysqlClientReader, AMysqlClientWriter
from src.config.auth import auth_config
from src.models.database import User


async def auth_google_callback_service(code: str) -> User:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": auth_config.google.client_id,
                "client_secret": auth_config.google.client_secret,
                "redirect_uri": auth_config.google.redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        tokens = token_resp.json()
        access_token = tokens["access_token"]

        user_resp = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile = user_resp.json()

    reader = AMysqlClientReader()
    if users := await reader.select(
        table=User, cond_equal=dict(google_sub=profile["sub"])
    ):
        user = users[0]
    else:
        writer = AMysqlClientWriter()
        user = User(
            email=profile["email"],
            google_sub=profile["sub"],
            user_name=profile["name"],
        )
        await writer.insert_one(user)

    return user
