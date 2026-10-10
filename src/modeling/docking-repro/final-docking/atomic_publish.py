#!/usr/bin/env python3
"""Publish staged outputs with explicit overwrite semantics."""

from __future__ import annotations

import contextlib
import os
import signal
import tempfile
import threading
from pathlib import Path
from types import FrameType
from typing import Iterable, Sequence


class AtomicPublishError(OSError):
    """A staged-output transaction could not be completed safely."""

    def __init__(self, message: str, *, safe_state: bool = True) -> None:
        self.safe_state = safe_state
        super().__init__(message)


class DelayedPublishSignal(BaseException):
    """SIGTERM/SIGINT received after a publish transaction reached a safe state."""

    def __init__(self, signum: int) -> None:
        self.signum = signum
        super().__init__(f"received signal {signum} during output publication")


@contextlib.contextmanager
def defer_publish_signals() -> Iterable[None]:
    """Delay SIGTERM/SIGINT while commit or rollback is in progress."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    received: list[int] = []
    previous_handlers: dict[int, signal.Handlers] = {}

    def _record_signal(signum: int, _frame: FrameType | None) -> None:
        received.append(signum)

    try:
        for signum in (signal.SIGTERM, signal.SIGINT):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, _record_signal)
        yield
    except BaseException as exc:
        if received:
            if isinstance(exc, AtomicPublishError) and not exc.safe_state:
                raise
            raise DelayedPublishSignal(received[-1]) from exc
        raise
    finally:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)

    if received:
        raise DelayedPublishSignal(received[-1])


def _backup_existing_output(target: Path) -> Path:
    descriptor, backup_name = tempfile.mkstemp(
        prefix=f".{target.name}.atomic-publish-backup-",
        dir=target.parent,
    )
    os.close(descriptor)
    backup = Path(backup_name)
    backup.unlink()
    try:
        os.link(target, backup)
    except OSError:
        backup.unlink(missing_ok=True)
        raise
    return backup


def publish_staged_files(
    outputs: Sequence[tuple[Path, Path]], *, overwrite: bool
) -> None:
    """Publish every staged file, or restore the complete previous state."""
    backups: dict[Path, Path | None] = {}
    published: list[Path] = []
    cleanup_backups = True
    with defer_publish_signals():
        try:
            try:
                if overwrite:
                    for _, target in outputs:
                        backups[target] = (
                            _backup_existing_output(target) if target.exists() else None
                        )

                for staged, target in outputs:
                    if overwrite:
                        os.replace(staged, target)
                    else:
                        os.link(staged, target)
                    published.append(target)
            except OSError as exc:
                rollback_errors: list[str] = []
                for target in reversed(published):
                    backup = backups.get(target)
                    try:
                        if backup is None:
                            target.unlink()
                        else:
                            os.replace(backup, target)
                    except FileNotFoundError:
                        pass
                    except OSError as rollback_exc:
                        rollback_errors.append(f"{target}: {rollback_exc}")

                if rollback_errors:
                    cleanup_backups = False
                    details = "; ".join(rollback_errors)
                    recovery_paths = [
                        str(backup) for backup in backups.values() if backup is not None
                    ]
                    recovery_note = ""
                    if recovery_paths:
                        recovery_note = (
                            "; recovery backups retained: "
                            + ", ".join(recovery_paths)
                        )
                    raise AtomicPublishError(
                        f"could not publish all outputs: {exc}; "
                        f"rollback failed: {details}{recovery_note}",
                        safe_state=False,
                    ) from exc
                raise
        except FileExistsError:
            raise
        except AtomicPublishError:
            raise
        except OSError as exc:
            raise AtomicPublishError(f"could not publish all outputs: {exc}") from exc
        finally:
            for staged, _ in outputs:
                staged.unlink(missing_ok=True)
            if cleanup_backups:
                for backup in backups.values():
                    if backup is not None:
                        backup.unlink(missing_ok=True)


def publish_staged_file(staged: Path, target: Path, *, overwrite: bool) -> None:
    """Publish ``staged`` without clobbering ``target`` unless allowed."""
    try:
        publish_staged_files(((staged, target),), overwrite=overwrite)
    except FileExistsError as error:
        raise FileExistsError(
            f"output already exists: {target} (use --overwrite)"
        ) from error
