from pathlib import Path
from typing import Annotated

from platformdirs import PlatformDirs
from pydantic import AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

dirs = PlatformDirs("sid-edit-ui", "LarsHutzelmann")


def _create_dirs(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True)
    elif not path.is_dir():
        raise ValueError(f"Path {path} already exists but is no directory")
    return path


class Settings(BaseSettings):
    upload_dir: Annotated[Path, AfterValidator(_create_dirs)] = (
        dirs.user_cache_path / "upload"
    )

    model_config = SettingsConfigDict(
        env_prefix="seu_", env_file=("/etc/.env", ".env"), env_file_encoding="utf-8"
    )
