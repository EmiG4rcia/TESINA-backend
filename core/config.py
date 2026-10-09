from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    SALES_TOKEN_EXPIRE_MINUTES: int = 15
    CORS_ORIGINS: str = "http://localhost:5173,https://proyecto-de-gestion-de-restaurante.vercel.app"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
