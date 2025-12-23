import os

from pydantic_settings import BaseSettings, SettingsConfigDict

SITE_URL = str(os.environ.get("SITE_URL", ""))


class JwtConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_")
    # TODO: manage secret
    secret_key: str
    algorithm: str = "HS256"


class GoogleConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GOOGLE_")
    client_id: str
    client_secret: str
    redirect_uri: str = f"{SITE_URL}/api/auth/google/callback"


class SessionConfig(BaseSettings):
    expiration_days: int = 30
    oauth_state_keyword: str = "oauth_state"
    session_token_keyword: str = "session_token"


class AuthConfig(BaseSettings):
    google: GoogleConfig
    jwt: JwtConfig
    session: SessionConfig
    callback_redirect: str = SITE_URL
    logout_redirect: str = SITE_URL


auth_config = AuthConfig(
    google=GoogleConfig(), jwt=JwtConfig(), session=SessionConfig()  # type: ignore
)
