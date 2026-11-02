"""Running the GitHub command line (``gh``), real or faked in tests."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    """The outcome of one ``gh`` call."""

    args: list[str]
    returncode: int
    stdout: str
    stderr: str


class GhRunner(Protocol):
    """Runs ``gh`` with the given arguments (without the ``gh`` program name)."""

    def run(self, args: Sequence[str]) -> CommandResult:
        """Run ``gh *args`` and return its result."""
        ...


class GhError(RuntimeError):
    """A ``gh`` call failed."""


class SubprocessGh:
    """Run the real ``gh``, never through a shell."""

    def run(self, args: Sequence[str]) -> CommandResult:
        """Run ``gh`` and raise :class:`GhError` when it fails."""
        completed = subprocess.run(
            ["gh", *args], capture_output=True, text=True, timeout=120, check=False
        )
        if completed.returncode != 0:
            raise GhError(f"gh {' '.join(args[:3])} failed: {completed.stderr.strip()}")
        return CommandResult(list(args), 0, completed.stdout, completed.stderr)
