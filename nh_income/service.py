"""Run-level orchestration: claim for every account and build reports."""

from __future__ import annotations

import asyncio
import logging

import httpx

from .client import MAX_CONCURRENCY, NhClient
from .models import Account, MultipleUnclaimedError, Report

logger = logging.getLogger(__name__)


async def _run_account(
    account: Account,
    transport: httpx.AsyncBaseTransport,
    semaphore: asyncio.Semaphore,
    fast: bool,
) -> Report:
    """Process a single account, converting every failure into a report."""
    async with semaphore:
        try:
            async with NhClient(account, transport) as client:
                result = await (client.claim_fast() if fast else client.claim_daily())
        except MultipleUnclaimedError as exc:
            logger.error("%s: %s", account.email, exc)
            return Report(email=account.email, error=str(exc))
        except Exception as exc:  # noqa: BLE001 - one bad account must not kill the run
            logger.exception("Unhandled error while processing %s", account.email)
            return Report(email=account.email, error=str(exc))
    return result.to_report()


async def claim_all(accounts: list[Account], *, fast: bool = False) -> list[Report]:
    """Claim daily income for every account concurrently.

    A single shared transport keeps one warm connection pool for all
    per-account clients; the semaphore caps how many accounts run at once.
    Failures are captured per account instead of cancelling the whole batch.
    """
    if not accounts:
        return []

    transport = httpx.AsyncHTTPTransport(retries=2)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [
        asyncio.create_task(_run_account(account, transport, semaphore, fast))
        for account in accounts
    ]
    reports = await asyncio.gather(*tasks)
    await transport.aclose()
    return list(reports)
