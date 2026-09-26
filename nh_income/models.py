"""Domain models for NH Income."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from .constants import WIB


class ClaimStatus(StrEnum):
    """State of a single reward card on the event page."""

    #: Reward was already claimed on the site before this run.
    CLAIMED = "claimed"
    #: Reward belonged to the current day and was claimed by this run.
    SUCCESS = "success"
    #: Reward is still locked/unclaimed (future days).
    FAILED = "failed"


STATUS_LABELS: dict[ClaimStatus, str] = {
    ClaimStatus.SUCCESS: "**Success** ✅",
    ClaimStatus.FAILED: "**Unclaimed** ❌",
    ClaimStatus.CLAIMED: "**Claimed** ✔️",
}


class MultipleUnclaimedError(RuntimeError):
    """Raised when the event page exposes more than one claimable reward."""

    def __init__(self) -> None:
        super().__init__("Found multiple unclaimed rewards! Consider claiming manually.")


@dataclass(slots=True)
class ClaimData:
    """A single reward card scraped from the event dashboard."""

    status: ClaimStatus
    day: int
    item: int
    name: str
    period: int

    def __str__(self) -> str:
        label = STATUS_LABELS.get(self.status, "**Unclaimed!**")
        return f"Item: {self.item}/Day {self.day} ({self.name}): {label}"


@dataclass(slots=True, frozen=True)
class Account:
    """One player account loaded from ``data.json``."""

    email: str
    password: str
    server: int
    discord_id: int = 0
    telegram_id: int = 0

    @property
    def uses_password(self) -> bool:
        return bool(self.password)


@dataclass(slots=True)
class Report:
    """Per-account result of a claim run, ready to be rendered and sent."""

    email: str
    claims: list[ClaimData] = field(default_factory=list)
    discord_id: int = 0
    telegram_id: int = 0
    #: Day number of the highest reward already secured (-1 when none).
    last_claim: int = -1
    #: Human-readable failure description for this account, if any.
    error: str | None = None

    @property
    def masked_email(self) -> str:
        """Email with everything between the first two chars and the @ hidden."""
        local, _, domain = self.email.partition("@")
        if not _:
            return self.email
        return f"{local[:2]}{'*' * max(len(local) - 2, 0)}@{domain}"

    def render(self) -> str:
        """Build the Markdown report sent to Discord/Telegram."""
        now = datetime.now(WIB)
        lines = [
            f"Income report for: **{self.masked_email}**",
            f"**{now.date()}**",
            f"Last claim: {self.last_claim if self.last_claim > 0 else 'No last claim!'}",
        ]
        if self.error:
            lines.append(f"⚠️ {self.error}")
        lines.extend(f"\n{claim}" for claim in self.claims)
        return "\n".join(lines)
