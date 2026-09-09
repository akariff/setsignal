import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def _env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean environment flag using common truthy values."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Configuration settings
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
PARALLEL_API_KEY: str = os.getenv("PARALLEL_API_KEY", "").strip()

# Gemini Model Selection (default: gemini-3.8-flash)
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

# Synthetic UI preview fixtures. This is configuration, not a secret.
ENABLE_UI_PREVIEW: bool = _env_flag("ENABLE_UI_PREVIEW", False)

# Server Port
PORT: int = int(os.getenv("PORT", "8080"))


def has_gemini_credentials() -> bool:
    """Check if valid Gemini API key is configured."""
    return bool(GEMINI_API_KEY)


def has_parallel_credentials() -> bool:
    """Check if valid Parallel API key is configured."""
    return bool(PARALLEL_API_KEY)


def get_missing_credentials() -> list[str]:
    """Return a list of missing required credential names."""
    missing = []
    if not has_gemini_credentials():
        missing.append("GEMINI_API_KEY")
    if not has_parallel_credentials():
        missing.append("PARALLEL_API_KEY")
    return missing
