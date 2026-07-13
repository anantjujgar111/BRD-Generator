from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: Path = Path("data/uploads")
    output_dir: Path = Path("data/outputs")
    cors_origins: list[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]

    class Config:
        env_prefix = "BRD_"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
