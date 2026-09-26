"""Discord DM notifications built on a minimal, short-lived bot client."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import Colour, Embed

if TYPE_CHECKING:
    from ..models import Report

logger = logging.getLogger(__name__)


class _ReportSender(discord.Client):
    """Logs in, DMs every recipient their report, and shuts down."""

    def __init__(self, reports: list[Report]) -> None:
        super().__init__()
        self._reports = reports

    async def on_ready(self) -> None:
        logger.info("Discord bot ready, sending %d report(s)", len(self._reports))
        for report in self._reports:
            try:
                user = await self.fetch_user(report.discord_id)
            except discord.NotFound:
                logger.warning("Discord user %s not found", report.discord_id)
                continue
            except discord.Forbidden:
                logger.warning("Not allowed to DM discord user %s", report.discord_id)
                continue
            embed = Embed(
                color=Colour.nitro_pink(),
                title="INCOME STATUS",
                description=report.render(),
            )
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                logger.warning("Failed to send message to %s", report.discord_id)
        await self.close()


async def send_discord_reports(reports: list[Report], token: str) -> None:
    """Send each report as a DM from the bot identified by ``token``."""
    client = _ReportSender(reports)
    try:
        await client.start(token)
    except discord.LoginFailure:
        raise RuntimeError("An improper Discord token was passed!") from None
    finally:
        if not client.is_closed():
            await client.close()
