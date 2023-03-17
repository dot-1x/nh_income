import asyncio
import os
from enum import Enum, auto
from datetime import datetime, timedelta
from calendar import monthrange
from typing import List, NamedTuple, TypedDict

import httpx
from discord import Bot, Embed, Colour, Forbidden
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

OWNERBOT = os.getenv("DISCORDUSER", "0")  # CHANGE THIS WITH YOUR DISCORD ACCOUNT
USER = os.getenv("KGUSER")
PASSWORD = os.getenv("KGPASSWORD")

DATE = datetime.utcnow() + timedelta(hours=7)  # GMT + 7 datetime
SERVER = os.getenv("SELSERVER", "1")  # IK its weird
PERIOD = DATE.month
STARTNUMBER = os.getenv("STARTINGNUMBER", "45")  # item starting number of current month
TOKEN = os.getenv("TOKEN")
_, DAYS = monthrange(DATE.year, DATE.month)

bot = Bot()


class Response(TypedDict):
    message: str
    data: str


class ClaimStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()
    CLAIMED = auto()


class DataTup(NamedTuple):
    status: ClaimStatus
    day: int
    item: int
    name: str


MSGSMAP = {
    ClaimStatus.SUCCESS: "**Succes** :ballot_box_with_check:",
    ClaimStatus.FAILED: "**Failed** :x:",
    ClaimStatus.CLAIMED: "**Claimed** :white_check_mark:",
}


async def perform_claim(session: httpx.AsyncClient, data: dict):
    resp = await session.post(
        "https://kageherostudio.com/event/index_.php?act=daily", data=data
    )
    resdata: Response = resp.json()
    await asyncio.sleep(0)
    return resdata["message"] == "success"


async def login():
    if USER is None or PASSWORD is None:
        raise ValueError("Username and Password must not NONE!")

    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=5*60)) as ses:
        # get the cookie first
        await ses.get("https://kageherostudio.com/event/?event=daily")

        # perform login
        await ses.post(
            "https://kageherostudio.com/event/index_.php?act=login",
            data={"txtuserid": USER, "txtpassword": PASSWORD},
        )
        resp = await ses.get("https://kageherostudio.com/event/?event=daily")
        page = BeautifulSoup(resp.content, "html.parser")

        results: List[DataTup] = [
            DataTup(ClaimStatus.FAILED, -1, -1, "")
        ] * DAYS  # pre allocation memory

        for day, element in enumerate(page.find_all("div", "grayscale"), start=1):
            results[day - 1] = DataTup(
                ClaimStatus.CLAIMED, day, int(element["data-id"]), element["data-name"]
            )

        # do the reward claiming
        for day, num in enumerate(
            range(
                int(STARTNUMBER),
                int(STARTNUMBER) + DAYS,
            ),
            start=1,
        ):
            if num in results[day - 1]:
                continue
            item = page.find("div", {"data-id": num})
            result = await perform_claim(
                ses, data={"itemId": num, "periodId": PERIOD, "selserver": int(SERVER)}
            )
            results[day - 1] = DataTup(
                ClaimStatus.SUCCESS if result else ClaimStatus.FAILED,
                day,
                num,
                item["data-name"],
            )
            if result:  # ignoring rest as it will trigger fail to save time
                break

    await asyncio.sleep(0)

    if not TOKEN:  # check without sending to discord bot
        print(
            *[
                f"Item {item}/Day {day}: "
                + (f'Claimed ({name})' if status in [ClaimStatus.SUCCESS, ClaimStatus.CLAIMED]
                else f'Failed ({name})')
                for status, day, item, name in results
                if item
            ],
            sep="\n",
        )
    return results


@bot.add_listener
async def on_ready():
    try:
        results = await login()
    except Exception as e:  # catch anything
        bot.loop.stop()
        return

    embed = Embed(
        colour=Colour.nitro_pink(),
        title="Claim daily report!",
        description=f"**{DATE.strftime('%d/%m/%Y')}**\n"
        + "\n".join(
            f"Item {item}/Day {day} ({name}): " + MSGSMAP[res]
            for res, day, item, name in results
        ),
        timestamp=datetime.now(),
    )
    user = await bot.get_or_fetch_user(int(OWNERBOT))
    if not user:
        print("User not found!")
    else:
        try:
            await user.send(embed=embed)
        except Forbidden:
            bot.loop.stop()
            return
    bot.loop.stop()


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        asyncio.run(login())
