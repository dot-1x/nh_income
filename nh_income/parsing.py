"""HTML parsing of the event dashboard."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from .constants import (
    CLAIMED_CLASS,
    CURRENT_CLASS,
    UNCLAIMED_CLASS,
)
from .models import ClaimData, ClaimStatus, MultipleUnclaimedError

USER_ID_SELECTOR = "p.userid"


def is_logged_in(soup: BeautifulSoup) -> bool:
    """The dashboard renders a ``<p class="userid">`` only after a valid login."""
    return soup.select_one(USER_ID_SELECTOR) is not None


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def parse_dashboard(soup: BeautifulSoup) -> tuple[list[ClaimData], ClaimData | None]:
    """Extract every reward card and the card claimable right now.

    Returns ``(all_cards, current)`` where ``current`` is ``None`` when
    today's reward is missing or already claimed.
    """
    cards = soup.select(f"div.{UNCLAIMED_CLASS}")
    current_tags = soup.select(f"div.{CURRENT_CLASS}")
    if len(current_tags) > 1:
        raise MultipleUnclaimedError

    claims: list[ClaimData] = []
    current: ClaimData | None = None
    for day, card in enumerate(cards, start=1):
        classes: list[str] = card.get("class", [])
        data = ClaimData(
            status=ClaimStatus.CLAIMED if CLAIMED_CLASS in classes else ClaimStatus.FAILED,
            day=day,
            item=_to_int(card.get("data-id")),
            name=str(card.get("data-name", "Unknown")),
            period=_to_int(card.get("data-period")),
        )
        claims.append(data)
        if card in current_tags:
            current = data
    return claims, current


def first_claimable_tag(soup: BeautifulSoup) -> Tag | None:
    """Return the raw ``reward-star`` tag without building the full report."""
    return soup.select_one(f"div.{CURRENT_CLASS}")
