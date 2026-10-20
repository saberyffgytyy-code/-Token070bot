import os
from typing import Set


def parse_admin_ids(raw_value: str) -> Set[int]:
    result: Set[int] = set()
    if not raw_value:
        return result

    for item in raw_value.split(","):
        value = item.strip()
        if not value:
            continue
        try:
            result.add(int(value))
        except ValueError as exc:  # pragma: no cover - surfaced in validation
            raise ValueError(f"Invalid ADMIN_IDS value: {value!r}") from exc
    return result


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = parse_admin_ids(os.getenv("ADMIN_IDS", ""))
BOT_DB_PATH = os.getenv("BOT_DB_PATH", "data/search_history.db")


def validate_config() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is required.")
    if not ADMIN_IDS:
        raise RuntimeError("ADMIN_IDS environment variable is required and must include at least one Telegram user ID.")
