"""Apply the organization's standard settings to a repository.

* merge policy: rebase only, so every commit of a pull request reaches ``main`` as it
  is and the test-first history stays visible; branches deleted after merge;
* the shared labels of ``labels.toml``;
* for products, the ``willproof-product`` topic that lists them across the organization.

Nothing changes without ``--apply``: by default the script prints the ``gh`` commands::

    python -m tools.setup_repository --repo willproof-labs/edge-smith --product
    python -m tools.setup_repository --repo willproof-labs/edge-smith --product --apply
"""

from __future__ import annotations

import argparse
import shlex
import sys
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.ghcli import GhRunner, SubprocessGh

LABELS_FILE = Path(__file__).resolve().parents[1] / "labels.toml"
PRODUCT_TOPIC = "willproof-product"


@dataclass(frozen=True)
class Label:
    """A label shared by every repository."""

    name: str
    color: str
    description: str


def load_labels(path: Path) -> list[Label]:
    """Read ``labels.toml``."""
    with path.open("rb") as stream:
        return [Label(**item) for item in tomllib.load(stream)["labels"]]


class RepositorySetup:
    """Plan or apply the standard settings of one repository.

    Args:
        gh: Runs ``gh``.
        out: Prints one line.
    """

    def __init__(self, gh: GhRunner, out: Callable[[str], None]) -> None:
        """Store the collaborators."""
        self._gh = gh
        self._out = out

    @staticmethod
    def commands(repo: str, labels: Sequence[Label], product: bool) -> list[list[str]]:
        """Return the ``gh`` commands (without ``gh``) that configure ``repo``."""
        edit = [
            "repo",
            "edit",
            repo,
            "--enable-rebase-merge",
            "--enable-squash-merge=false",
            "--enable-merge-commit=false",
            "--delete-branch-on-merge",
        ]
        if product:
            edit += ["--add-topic", PRODUCT_TOPIC]
        labels_commands = [
            [
                "label",
                "create",
                label.name,
                "--repo",
                repo,
                "--color",
                label.color,
                "--description",
                label.description,
                "--force",
            ]
            for label in labels
        ]
        return [edit, *labels_commands]

    def run(self, repo: str, labels: Sequence[Label], product: bool, apply: bool) -> int:
        """Print the plan, or apply it."""
        if not apply:
            self._out("Dry run: nothing is changed. Add --apply to run these commands.")
        for command in self.commands(repo, labels, product):
            if apply:
                self._gh.run(command)
            else:
                self._out(shlex.join(["gh", *command]))
        if apply:
            self._out(f"{repo}: settings and {len(labels)} labels applied")
        return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Apply WillProof Labs repository settings.")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--product", action="store_true", help="add the product topic")
    parser.add_argument("--labels", type=Path, default=LABELS_FILE)
    parser.add_argument("--apply", action="store_true", help="really change the repository")
    args = parser.parse_args(argv)
    setup = RepositorySetup(SubprocessGh(), print)
    return setup.run(args.repo, load_labels(args.labels), args.product, args.apply)


if __name__ == "__main__":
    sys.exit(main())
