"""Domain models for NH Income.

These dataclasses are intentionally dependency-free so the rest of the
package (HTTP client, notifiers, CLI) only depends on this small core.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

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
