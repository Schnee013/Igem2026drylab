"""Shared external process runner with streaming output and signal forwarding."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import FrameType
from typing import IO, Mapping, Sequence


StreamTarget = IO[str] | IO[bytes]
DEFAULT_SIGNAL_GRACE_SECONDS = 1.0


def _write_stream(target: StreamTarget, data: bytes) -> None:
    if not data:
        return
    if "b" in getattr(target, "mode", ""):
        target.write(data)  # type: ignore[arg-type]
    else:
        target.write(data.decode("utf-8", errors="replace"))  # type: ignore[arg-type]
    target.flush()


def _read_pipe(pipe_fd: int, captured: bytearray, target: StreamTarget) -> None:
    try:
        while True:
            chunk = os.read(pipe_fd, 8192)
            if not chunk:
                return
            captured.extend(chunk)
            _write_stream(target, chunk)
    except OSError:
        return


def _capture_pipe(pipe_fd: int, captured: bytearray) -> None:
    try:
        while True:
            chunk = os.read(pipe_fd, 8192)
            if not chunk:
                return
            captured.extend(chunk)
    except OSError:
        return


def _signal_process_group(
    process: subprocess.Popen[bytes], process_group_id: int | None, signum: int
) -> None:
    try:
        if process_group_id is not None and hasattr(os, "killpg"):
            os.killpg(process_group_id, signum)
        else:
            process.send_signal(signum)
    except ProcessLookupError:
        return


def _process_group_exists(
    process: subprocess.Popen[bytes], process_group_id: int | None
) -> bool:
    if process_group_id is None or not hasattr(os, "killpg"):
        return process.poll() is None
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _stop_process_group(
    process: subprocess.Popen[bytes],
    process_group_id: int | None,
    signum: int,
    grace_seconds: float,
) -> int:
    """Stop the original child process group, even if its leader exits first."""
    _signal_process_group(process, process_group_id, signum)
    grace_deadline = time.monotonic() + max(0.0, grace_seconds)

    while time.monotonic() < grace_deadline:
        group_exists = _process_group_exists(process, process_group_id)
        returncode = process.poll()
        if not group_exists and returncode is not None:
            return returncode
        time.sleep(0.02)

    if _process_group_exists(process, process_group_id):
        _signal_process_group(process, process_group_id, signal.SIGKILL)

    confirmation_deadline = time.monotonic() + 2.0
    while time.monotonic() < confirmation_deadline:
        group_exists = _process_group_exists(process, process_group_id)
        returncode = process.poll()
        if not group_exists and returncode is not None:
            return returncode
        time.sleep(0.02)

    # SIGKILL has already been sent to the recorded group. Reap the direct
    # child without waiting indefinitely for a non-child zombie to be reaped.
    if process.poll() is None:
        try:
            return process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait()
    assert process.returncode is not None
    return process.returncode


def _join_pipe_threads(
    process: subprocess.Popen[bytes],
    stdout_thread: threading.Thread,
    stderr_thread: threading.Thread,
    *,
    bounded: bool,
) -> None:
    threads = (stdout_thread, stderr_thread)
    if bounded:
        deadline = time.monotonic() + 2.0
        for thread in threads:
            thread.join(timeout=max(0.0, deadline - time.monotonic()))
    else:
        for thread in threads:
            thread.join()

    process.stdout.close()  # type: ignore[union-attr]
    process.stderr.close()  # type: ignore[union-attr]
    for thread in threads:
        if thread.is_alive():
            thread.join(timeout=0.2)


def run_external(
    argv: Sequence[str | os.PathLike[str]],
    *,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    text: bool = True,
    timeout: float | None = None,
    stdout: StreamTarget | None = None,
    stderr: StreamTarget | None = None,
    forward_stdout: bool = True,
    forward_stderr: bool = True,
    signal_grace_seconds: float = DEFAULT_SIGNAL_GRACE_SECONDS,
    check: bool = False,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    """Run one argv-array command, stream both channels, and capture them.

    The child is placed in its own process group on POSIX platforms. When the
    wrapper receives SIGTERM or SIGINT while the child is active, the signal is
    forwarded to that process group so a GUI cancel does not leave the real
    scientific child running after the Python wrapper exits.
    """
    if not argv:
        raise ValueError("argv must not be empty")
    command = [str(part) for part in argv]
    stdout_target = sys.stdout if stdout is None else stdout
    stderr_target = sys.stderr if stderr is None else stderr
    received_signal: list[int] = []
    previous_handlers: dict[int, signal.Handlers] = {}

    def _forward_signal(signum: int, _frame: FrameType | None) -> None:
        received_signal.append(signum)

    can_install_handlers = threading.current_thread() is threading.main_thread()
    if can_install_handlers:
        try:
            for signum in (signal.SIGTERM, signal.SIGINT):
                previous_handlers[signum] = signal.getsignal(signum)
                signal.signal(signum, _forward_signal)
        except BaseException:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)
            raise

    try:
        process = subprocess.Popen(
            command,
            cwd=str(Path(cwd)) if cwd is not None else None,
            env=dict(env) if env is not None else None,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        # start_new_session makes the direct child the leader of a new session
        # and process group before exec. Keep that immutable ID; looking it up
        # after the leader exits loses access to still-running descendants.
        process_group_id = process.pid if os.name == "posix" else None
        assert process.stdout is not None
        assert process.stderr is not None

        captured_stdout = bytearray()
        captured_stderr = bytearray()
        stdout_thread = threading.Thread(
            target=_read_pipe if forward_stdout else _capture_pipe,
            args=(
                (process.stdout.fileno(), captured_stdout, stdout_target)
                if forward_stdout
                else (process.stdout.fileno(), captured_stdout)
            ),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_read_pipe if forward_stderr else _capture_pipe,
            args=(
                (process.stderr.fileno(), captured_stderr, stderr_target)
                if forward_stderr
                else (process.stderr.fileno(), captured_stderr)
            ),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        returncode: int
        timeout_deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            if received_signal:
                returncode = _stop_process_group(
                    process,
                    process_group_id,
                    received_signal[0],
                    signal_grace_seconds,
                )
                break

            now = time.monotonic()
            returncode = process.poll()
            if (
                returncode is not None
                and not _process_group_exists(process, process_group_id)
                and not stdout_thread.is_alive()
                and not stderr_thread.is_alive()
            ):
                break

            if timeout_deadline is not None and now >= timeout_deadline:
                _stop_process_group(process, process_group_id, signal.SIGTERM, 2.0)
                _join_pipe_threads(process, stdout_thread, stderr_thread, bounded=True)
                output: str | bytes
                error_output: str | bytes
                if text:
                    output = captured_stdout.decode("utf-8", errors="replace")
                    error_output = captured_stderr.decode("utf-8", errors="replace")
                else:
                    output = bytes(captured_stdout)
                    error_output = bytes(captured_stderr)
                raise subprocess.TimeoutExpired(
                    command,
                    timeout,
                    output=output,
                    stderr=error_output,
                )

            time.sleep(0.02)

        _join_pipe_threads(
            process,
            stdout_thread,
            stderr_thread,
            bounded=bool(received_signal),
        )
        if received_signal:
            returncode = 128 + received_signal[-1]

        completed_stdout: str | bytes
        completed_stderr: str | bytes
        if text:
            completed_stdout = captured_stdout.decode("utf-8", errors="replace")
            completed_stderr = captured_stderr.decode("utf-8", errors="replace")
        else:
            completed_stdout = bytes(captured_stdout)
            completed_stderr = bytes(captured_stderr)
        completed = subprocess.CompletedProcess(
            command,
            returncode,
            stdout=completed_stdout,
            stderr=completed_stderr,
        )
        if check:
            completed.check_returncode()
        return completed
    finally:
        if can_install_handlers:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)
