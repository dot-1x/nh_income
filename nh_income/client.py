"""Async HTTP client for the KageHero Studio daily income event."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

import httpx
from bs4 import BeautifulSoup

from . import parsing
from .constants import (
    CLAIM_URL,
    INCOME_URL,
    LOGIN_URL,
    XSS_LOGIN_URL,
)
from .models import Account, ClaimData, ClaimStatus, Report

logger = logging.getLogger(__name__)

#: Network timeouts: connect fast, read generously (the site can be slow).
TIMEOUT = httpx.Timeout(connect=15.0, read=60.0, write=30.0, pool=30.0)

#: Upper bound of accounts processed at the same time; protects the shared
#: connection pool and keeps us polite towards the origin server.
MAX_CONCURRENCY = 5


def _to_int(value: object, default: int = 0) -> int:
    """Coerce an HTML ``data-*`` attribute to an int."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


class LoginError(RuntimeError):
    """Raised when an account could not log in to the event dashboard."""


@dataclass(slots=True)
class ClaimResult:
    """Outcome of processing a single account."""

    account: Account
    claims: list[ClaimData] = field(default_factory=list)
    success: bool = False
    error: str | None = None

    @property
    def failed(self) -> bool:
        return self.error is not None

    def to_report(self) -> Report:
        secured = [
            claim.day
            for claim in self.claims
            if claim.status in (ClaimStatus.CLAIMED, ClaimStatus.SUCCESS)
        ]
        return Report(
            email=self.account.email,
            claims=self.claims,
            discord_id=self.account.discord_id,
            telegram_id=self.account.telegram_id,
            last_claim=max(secured, default=-1),
            error=self.error,
        )


class NhClient:
    """One authenticated session for a single account.

    Cookie jars are per-instance, so every account needs its own client;
    connection pooling is shared through the ``transport`` instead.
    """

    def __init__(self, account: Account, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.account = account
        self._transport = transport
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> NhClient:
        self._client = httpx.AsyncClient(
            transport=self._transport,
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *_exc: object) -> None:
        if self._client:
            await self._client.aclose()

    # -- low level helpers -------------------------------------------------

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("NhClient must be used as an async context manager.")
        return self._client

    async def _get_dashboard(self) -> BeautifulSoup:
        response = await self.client.get(INCOME_URL)
        response.raise_for_status()
        return BeautifulSoup(await response.aread(), "html.parser")

    async def login(self) -> None:
        """Establish a session (password login or fbid fast-login)."""
        await self._get_dashboard()  # pick up initial cookies
        if self.account.uses_password:
            response = await self.client.post(
                LOGIN_URL,
                data={
                    "txtuserid": self.account.email,
                    "txtpassword": self.account.password,
                },
            )
            response.raise_for_status()
        else:
            response = await self.client.get(XSS_LOGIN_URL.format(self.account.email))
            response.raise_for_status()

    # -- high level operations ---------------------------------------------

    async def fetch_state(self) -> tuple[list[ClaimData], ClaimData | None]:
        """Log in and return the reward cards plus the claimable one."""
        await self.login()
        soup = await self._get_dashboard()
        if not parsing.is_logged_in(soup):
            raise LoginError(f"Failed to login for {self.account.email}")
        return parsing.parse_dashboard(soup)

    async def submit_claim(self, item_id: int, period: int) -> bool:
        """POST a claim for ``item_id`` and report whether it succeeded."""
        response = await self.client.post(
            CLAIM_URL,
            data={
                "itemId": item_id,
                "periodId": period,
                "selserver": self.account.server,
            },
        )
        response.raise_for_status()
        payload = response.json()
        logger.info(
            "Claim response for %s (item=%s period=%s): %s",
            self.account.email,
            item_id,
            period,
            payload,
        )
        return str(payload.get("message", "")).lower() == "success"

    async def claim_daily(self) -> ClaimResult:
        """Claim today's reward, returning a fully populated result."""
        try:
            claims, today = await self.fetch_state()
        except LoginError as exc:
            logger.warning("%s", exc)
            return ClaimResult(account=self.account, error=str(exc))

        if today is None:
            logger.info("Nothing to claim for %s (already claimed or locked)", self.account.email)
            return ClaimResult(account=self.account, claims=claims)

        logger.info("Claiming item %s for %s", today.item, self.account.email)
        success = await self.submit_claim(today.item, today.period)
        if success:
            today.status = ClaimStatus.SUCCESS
            logger.info("Successfully claimed income for %s", self.account.email)
        else:
            logger.warning("Failed to claim income for %s", self.account.email)
        return ClaimResult(account=self.account, claims=claims, success=success)

    async def claim_fast(self) -> ClaimResult:
        """Optimized path: read the dashboard once and claim immediately."""
        await self.login()
        soup = await self._get_dashboard()
        if not parsing.is_logged_in(soup):
            logger.warning("Failed to login for %s", self.account.email)
            return ClaimResult(account=self.account, error="login failed")

        today = parsing.first_claimable_tag(soup)
        if today is None:
            logger.info("Nothing to claim for %s (already claimed or locked)", self.account.email)
            return ClaimResult(account=self.account)

        success = await self.submit_claim(
            _to_int(today.get("data-id"), 0),
            _to_int(today.get("data-period"), 0),
        )
        claims = [
            ClaimData(
                status=ClaimStatus.CLAIMED,
                day=-1,
                item=_to_int(card.get("data-id")),
                name=str(card.get("data-name", "Unknown")),
                period=_to_int(card.get("data-period")),
            )
            for card in soup.select(f"div.{CLAIMED_CLASS}")
        ]
        claims.sort(key=lambda claim: claim.item)
        return ClaimResult(account=self.account, claims=claims, success=success)

    async def skip_income(self, amount: int) -> ClaimResult:
        """Claim today's reward ``amount`` times in parallel (testing tool)."""
        claims, today = await self.fetch_state()
        if today is None:
            raise LookupError("Today's income is already claimed.")
        async with asyncio.TaskGroup() as tg:
            for _ in range(amount):
                tg.create_task(self.submit_claim(today.item, today.period))
        logger.info("Skip-claimed item %s x%d for %s", today.item, amount, self.account.email)
        return ClaimResult(account=self.account, claims=claims, success=True)
