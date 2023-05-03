from __future__ import annotations
import traceback
from typing import TYPE_CHECKING, Any, List

from discord import Bot, Embed, Colour, Forbidden

if TYPE_CHECKING:
    from dailyclaim import UserStatus


class DiscordNotifier(Bot):
    def __init__(self, user_status: List[UserStatus]):
        super().__init__("Income notifier")
        self.user_status = user_status

    async def on_ready(self):
        print("Bot discord is ready!")
        for status in self.user_status:
            user = await self.get_or_fetch_user(status.discord)
            if not user:
                print(f"userid {status.discord} not found!")
                continue
            embed = Embed(
                color=Colour.nitro_pink(),
                title="INCOME STATUS",
                description=status.print_status(),
            )
            try:
                await user.send(embed=embed)
            except Forbidden:
                print(f"Failed to send message to {status.discord}")
        await self.close()

    async def on_error(self, *_: Any, **__: Any) -> None:
        traceback.print_exc()
        await self.close()
        raise RuntimeError
