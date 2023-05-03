from __future__ import annotations
import asyncio
import traceback

from typing import TYPE_CHECKING, List, Optional
from telegram import Bot
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CallbackContext

if TYPE_CHECKING:
    from dailyclaim import UserStatus


class TeleBot(Bot):
    def __init__(self, token):
        super().__init__(token)


class TeleNotifier(ApplicationBuilder):
    def __init__(self, token: str, user_status: List[UserStatus]):
        super().__init__()
        self.notifier = TeleBot(token)
        self.user_status = user_status
        self.app = self.bot(self.notifier).build()
        self.app.add_error_handler(self.on_error)

    def run(self):
        job_q = self.app.job_queue
        if not job_q:
            raise ValueError("Job Queue not found!")
        job_q.run_once(self.send_msgs, 5)
        self.app.run_polling()

    async def on_error(self, _: Optional[object], context: CallbackContext):
        asyncio.get_running_loop().stop()
        traceback.print_exception(context.error)

    async def send_msgs(self, _: CallbackContext):
        print("Bot telegram is ready")
        for status in self.user_status:
            try:
                await self.notifier.send_message(status.tele, status.print_status())
            except BadRequest as exc:
                print(f"raised exception for '{status.tele}' with exc:", exc)
        asyncio.get_running_loop().stop()
