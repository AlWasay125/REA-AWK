from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    database_url: str = "sqlite:///./reverseai.db"
    redis_url: str = "redis://localhost:6379/0"
    artifact_storage_path: str = "./backend/data/artifacts"
    report_storage_path: str = "./backend/data/reports"
    max_upload_size_mb: int = 100
    ghidra_install_dir: str | None = None
    ghidra_project_root: str = "./backend/data/ghidra"
    local_llm_base_url: str = "http://localhost:11434"
    local_llm_model: str | None = None
    external_inference_enabled: bool = False
    external_provider: str | None = None
    external_api_key: str | None = None
    max_agent_steps: int = 20
    max_job_duration_seconds: int = 1800

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


settings = Settings()
