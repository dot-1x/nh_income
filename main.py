#!/usr/bin/env python3
"""Backwards-compatible entry point.

Legacy invocations such as ``python main.py --type auto`` and CI workflows
keep working; the implementation now lives in the ``nh_income`` package.
"""

from nh_income.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
