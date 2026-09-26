"""Configuration: account list loading and environment settings."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .models import Account

logger = logging.getLogger(__name__)

load_dotenv()

#: Environments (e.g. GitHub Actions) do not have a ``data.json`` next to the
#: repo root by default; the workflow passes the path explicitly.
DEFAULT_DATA_FILE = Path(os.getenv("NH_DATA_FILE", "data.json"))


class ConfigError(ValueError):
    """Raised when ``data.json`` is missing or contains invalid records."""


@dataclass(slots=True, frozen=True)
class Settings:
    """Runtime settings resolved from the environment."""

    discord_token: str | None = None
    telegram_token: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            discord_token=os.getenv("DISCORDTOKEN") or None,
            telegram_token=os.getenv("TELETOKEN") or None,
        )


def _as_int(value: object, field_name: str, email: str) -> int:
    """Coerce JSON scalars (``"14"``, ``14``, ``None``) into ints."""
    if value is None or value == "":
        return 0
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Account {email!r}: invalid {field_name}: {value!r}") from exc


def parse_account(raw: dict[str, object]) -> Account:
    """Validate and coerce a single ``data.json`` record."""
    email = str(raw.get("email", "")).strip()
    if not email:
        raise ConfigError("Every account needs a non-empty 'email' field.")

    server = _as_int(raw.get("server"), "server", email)
    if server <= 0:
        raise ConfigError(f"Account {email!r}: 'server' must be a positive integer.")

    return Account(
        email=email,
        password=str(raw.get("password") or ""),
        server=server,
        discord_id=_as_int(raw.get("discord_id"), "discord_id", email),
        telegram_id=_as_int(raw.get("tele_id"), "tele_id", email),
    )


def load_accounts(path: Path = DEFAULT_DATA_FILE) -> list[Account]:
    """Load and validate the account list from a ``data.json`` file."""
    if not path.is_file():
        raise ConfigError(f"Data file not found: {path}")

    try:
        raw_accounts = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Data file {path} is not valid JSON: {exc}") from exc

    if not isinstance(raw_accounts, list):
        raise ConfigError(f"Data file {path} must contain a JSON array of accounts.")

    accounts = [parse_account(raw) for raw in raw_accounts]
    logger.info("Loaded %d account(s) from %s", len(accounts), path)
    return accounts
