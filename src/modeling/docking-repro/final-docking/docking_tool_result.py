"""Internal result receipt shared by the independent Docking CLIs and GUI."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


RESULT_SCHEMA = "docking-tool-result/v1"
RESULT_PATH_ENV = "DOCKING_TOOL_RESULT_PATH"
ARTIFACT_KINDS = {"file", "directory"}


class ToolResultError(RuntimeError):
    """The optional internal result receipt could not be written or read."""


@dataclass(frozen=True)
class ToolArtifact:
    path: Path
    label: str
    kind: str = "file"

    def as_json(self) -> dict[str, str]:
        return {"path": str(self.path), "label": self.label, "kind": self.kind}


def write_tool_result(artifacts: Iterable[ToolArtifact] = ()) -> None:
    """Write a receipt when the GUI supplied an internal receipt path.

    Normal CLI invocations do not set ``RESULT_PATH_ENV`` and therefore retain
    their existing stdout and stderr behavior.
    """

    receipt_value = os.environ.get(RESULT_PATH_ENV, "")
    if not receipt_value:
        return
    receipt_path = Path(receipt_value).expanduser()
    normalized = tuple(_normalize_artifact(artifact) for artifact in artifacts)
    paths = [artifact.path for artifact in normalized]
    if len(paths) != len(set(paths)):
        raise ToolResultError("result receipt contains duplicate artifact paths")
    payload = {
        "schema": RESULT_SCHEMA,
        "artifacts": [artifact.as_json() for artifact in normalized],
    }
    _write_json_atomic(receipt_path, payload)


def read_tool_result(path: Path) -> tuple[ToolArtifact, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ToolResultError(f"could not read tool result receipt {path}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema") != RESULT_SCHEMA:
        raise ToolResultError(f"unsupported tool result receipt schema in {path}")
    rows = payload.get("artifacts")
    if not isinstance(rows, list):
        raise ToolResultError(f"tool result receipt has no artifact list: {path}")
    artifacts: list[ToolArtifact] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ToolResultError(f"artifact {index} is not an object")
        artifact_path = row.get("path")
        label = row.get("label")
        kind = row.get("kind")
        if not isinstance(artifact_path, str) or not artifact_path:
            raise ToolResultError(f"artifact {index} has no path")
        if not isinstance(label, str) or not label:
            raise ToolResultError(f"artifact {index} has no label")
        if kind not in ARTIFACT_KINDS:
            raise ToolResultError(f"artifact {index} has invalid kind: {kind!r}")
        artifacts.append(ToolArtifact(Path(artifact_path), label, kind))
    if len({artifact.path for artifact in artifacts}) != len(artifacts):
        raise ToolResultError("tool result receipt contains duplicate artifact paths")
    return tuple(artifacts)


def _normalize_artifact(artifact: ToolArtifact) -> ToolArtifact:
    if artifact.kind not in ARTIFACT_KINDS:
        raise ToolResultError(f"invalid artifact kind: {artifact.kind!r}")
    if not artifact.label:
        raise ToolResultError("artifact label must not be empty")
    path = artifact.path.expanduser().resolve()
    if artifact.kind == "file" and not path.is_file():
        raise ToolResultError(f"artifact file does not exist: {path}")
    if artifact.kind == "directory" and not path.is_dir():
        raise ToolResultError(f"artifact directory does not exist: {path}")
    return ToolArtifact(path=path, label=artifact.label, kind=artifact.kind)


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)
    except OSError as exc:
        raise ToolResultError(f"could not write tool result receipt {path}: {exc}") from exc
