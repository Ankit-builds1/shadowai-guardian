from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NVIDIA_NIM_API_KEY: str = ""
    NVIDIA_NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_NIM_MODEL: str = "meta/llama-3.1-8b-instruct"
    DATABASE_URL: str = "sqlite+aiosqlite:///./shadowai.db"
    SECRET_KEY: str = "shadowai_secret_123"

    class Config:
        env_file = ".env"


settings = Settings()
