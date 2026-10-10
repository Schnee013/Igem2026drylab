"""Resolve transient-work roots without using the macOS per-user temp tree."""

from __future__ import annotations

import os
from pathlib import Path


def transient_root() -> Path:
    """Return the configured run root, or the stable ``/private/tmp`` fallback."""
    configured = os.environ.get("DOCKING_TEST_TMP_ROOT", "").strip()
    root = Path(configured) if configured else Path("/private/tmp")
    if not root.is_absolute():
        raise RuntimeError("DOCKING_TEST_TMP_ROOT 必须是绝对路径")
    root.mkdir(parents=True, exist_ok=True)
    return root
