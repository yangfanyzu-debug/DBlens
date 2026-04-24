import secrets
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./dblens_meta.db"
    DBLENS_SECRET_KEY: str = secrets.token_urlsafe(32)
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    RUOYI_BASE_URL: str = "http://192.168.0.140/prod-api"
    RUOYI_USERINFO_PATH: str = "/system/user/getInfo"
    RUOYI_TOKEN_HEADER: str = "Authorization"
    RUOYI_TIMEOUT_SECONDS: int = 10

    model_config = ConfigDict(env_file=".env")


settings = Settings()
