"""Telegram DM notifications via the plain async bot API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import telegram
from telegram.error import BadRequest, Forbidden

if TYPE_CHECKING:
    from ..models import Report

logger = logging.getLogger(__name__)


async def send_telegram_reports(reports: list[Report], token: str) -> None:
    """Send each report as a message from the bot identified by ``token``."""
    async with telegram.Bot(token) as bot:
        logger.info("Telegram bot ready, sending %d report(s)", len(reports))
        for report in reports:
            try:
                await bot.send_message(
                    chat_id=report.telegram_id,
                    text=report.render(),
                )
            except BadRequest as exc:
                logger.error(
                    "Telegram rejected chat %s: %s",
                    report.telegram_id,
                    exc,
                )
            except Forbidden:
                logger.warning("Bot blocked by telegram user %s", report.telegram_id)
