from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BRD_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    upload_dir: Path = Path("data/uploads")
    output_dir: Path = Path("data/outputs")
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ]
    )
    anthropic_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096

    @property
    def resolved_anthropic_api_key(self) -> str | None:
        import os

        return self.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")

    @property
    def llm_enabled(self) -> bool:
        return bool(self.resolved_anthropic_api_key)


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
