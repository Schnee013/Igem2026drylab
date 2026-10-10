"""Resolve configured Docking inputs and results from the drylab root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = CODE_ROOT.parents[3]


def resolve_paths(root: Path | None = None) -> dict[str, Path]:
    root = (root or REPOSITORY_ROOT).expanduser().resolve()
    configured = json.loads((CODE_ROOT / "configs" / "paths.json").read_text())
    result = {}
    for name, value in configured.items():
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Expected repository-relative path for {name}: {value}")
        result[name] = root / relative
    return result


def resolve_recorded_path(value: str, *, anchor: Path) -> Path:
    """Read repository-relative records and batch-local output records."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] in {"experiments", "src", "docs", "environments"}:
        return REPOSITORY_ROOT / path
    return anchor / path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    args = parser.parse_args()
    paths = resolve_paths(args.root)
    if args.name not in paths:
        parser.error(f"Unknown path name: {args.name}")
    print(paths[args.name])
