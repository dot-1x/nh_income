"""Constants for NH Income."""

from __future__ import annotations

from zoneinfo import ZoneInfo

#: Site event time (the dashboard resets on GMT+7).
WIB = ZoneInfo("Asia/Jakarta")

INCOME_URL = "https://kageherostudio.com/event/?event=daily"
LOGIN_URL = "https://kageherostudio.com/event/index_.php?act=login"
CLAIM_URL = "https://kageherostudio.com/event/index_.php?act=daily"
XSS_LOGIN_URL = "https://kageherostudio.com/payment/server_.php?fbid={}&selserver=1"

#: CSS hook classes used by the event page.
CLAIMED_CLASS = "grayscale"
UNCLAIMED_CLASS = "dailyClaim"
CURRENT_CLASS = "reward-star"
