import secrets
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./dblens_meta.db"
    DBLENS_SECRET_KEY: str = secrets.token_urlsafe(32)
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    LOCAL_DEV_AUTH_ENABLED: bool = True
    RUOYI_BASE_URL: str = "http://192.168.0.140/prod-api"
    RUOYI_USERINFO_PATH: str = "/system/user/getInfo"
    RUOYI_TOKEN_HEADER: str = "Authorization"
    RUOYI_TIMEOUT_SECONDS: int = 10
    AI_PROVIDER: str = "ark"
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/coding/v3"
    AI_MODEL: str = "glm-5.2"
    AI_TIMEOUT_SECONDS: int = 60

    model_config = ConfigDict(env_file=".env")


def sync_database_url(database_url: str) -> str:
    if database_url.startswith("mysql+aiomysql://"):
        return database_url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    return database_url


settings = Settings()
