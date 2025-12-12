from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "my_super_secret"
    
    github_client_id: str = "FAKE_CLI"
    github_client_secret: str = "FAKE_SECRET"
    github_redirect_url: str = "http://localhost:8000/auth/github/callback"
    
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 21
    
    news_cache_ttl: int = 300
    user_cache_ttl: int = 600

    class Config:
        env_file=".env"
        extra="ignore"

settings = Settings()
