#!/usr/bin/env python3
"""Backwards-compatible entry point.

Translates the legacy interface into the new CLI:

    python main.py --type auto [--amount N]  ->  nh_income claim
    python main.py --type skip --amount N    ->  nh_income skip (requires args)
"""

from __future__ import annotations

import sys

from nh_income.__main__ import main


def legacy(argv: list[str]) -> list[str]:
    """Map ``--type auto|skip`` invocations onto the new subcommands."""
    if "--type" not in argv:
        return argv

    kind = argv[argv.index("--type") + 1]
    rest = []
    skip_next = False
    for arg in argv:
        if skip_next:
            skip_next = False
            continue
        if arg == "--type":
            skip_next = True
            continue
        rest.append(arg)

    command = {"auto": "claim", "skip": "skip"}.get(kind)
    return [command, *rest] if command else argv


if __name__ == "__main__":
    raise SystemExit(main(legacy(sys.argv[1:])))
