"""Local environment-file loader for development secrets."""

from pathlib import Path
import os


def load_env_local(path: str | Path | None = None) -> None:
    """Load KEY=VALUE pairs from .env_local without overriding existing env vars."""
    env_path = Path(path) if path is not None else Path(__file__).resolve().parent / ".env_local"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value
