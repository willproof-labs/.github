"""Create a GitHub project (board) with its milestones and issues from a backlog file.

Each product keeps the seed of its backlog in ``.github/project/backlog.toml``; the lab
board's seed is ``project/lab-backlog.toml`` in this repository. Issues go to the main
repository unless they name another one (``repo = "owner/name"``), so one board can
gather issues of several repositories. Labels must exist first: apply them with
``tools.setup_repository``.

The script is idempotent (existing milestones and issues, matched by title, are left
alone) and changes nothing without ``--apply``. ``gh`` needs the ``project`` scope::

    gh auth refresh -s project
    python -m tools.bootstrap_project --repo willproof-labs/edge-smith --title edge-smith
        --backlog ../edge-smith/.github/project/backlog.toml   (one line)
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.ghcli import GhRunner, SubprocessGh


@dataclass(frozen=True)
class Milestone:
    """A milestone of the main repository."""

    title: str
    description: str


@dataclass(frozen=True)
class Issue:
    """An issue to create; ``repo`` is None for the main repository."""

    title: str
    body: str
    labels: tuple[str, ...]
    milestone: str | None = None
    repo: str | None = None


@dataclass(frozen=True)
class Backlog:
    """The seed of a board."""

    milestones: tuple[Milestone, ...]
    issues: tuple[Issue, ...]

    @classmethod
    def load(cls, path: Path) -> Backlog:
        """Read a backlog TOML file."""
        with path.open("rb") as stream:
            data: dict[str, Any] = tomllib.load(stream)
        return cls(
            milestones=tuple(Milestone(**item) for item in data.get("milestones", [])),
            issues=tuple(
                Issue(
                    title=item["title"],
                    body=item["body"].strip(),
                    labels=tuple(item.get("labels", [])),
                    milestone=item.get("milestone"),
                    repo=item.get("repo"),
                )
                for item in data.get("issues", [])
            ),
        )


class ProjectBootstrap:
    """Plan or create the board, milestones and issues of a backlog.

    Args:
        gh: Runs ``gh``.
        repo: Main repository, ``owner/name``.
        title: Title of the GitHub project (board), owned by the repository's owner.
        out: Prints one line.
    """

    def __init__(self, gh: GhRunner, repo: str, title: str, out: Callable[[str], None]) -> None:
        """Store the target."""
        self._gh = gh
        self._repo = repo
        self._owner = repo.split("/", 1)[0]
        self._title = title
        self._out = out

    def _json(self, *args: str) -> Any:
        return json.loads(self._gh.run(list(args)).stdout or "null")

    def _milestone_command(self, milestone: Milestone) -> list[str]:
        return [
            "api",
            "--method",
            "POST",
            f"repos/{self._repo}/milestones",
            "-f",
            f"title={milestone.title}",
            "-f",
            f"description={milestone.description}",
        ]

    def _issue_command(self, issue: Issue) -> list[str]:
        command = [
            "issue",
            "create",
            "--repo",
            issue.repo or self._repo,
            "--title",
            issue.title,
            "--body",
            issue.body,
        ]
        if issue.milestone:
            command += ["--milestone", issue.milestone]
        return command + [item for label in issue.labels for item in ("--label", label)]

    def run(self, backlog: Backlog, apply: bool) -> int:
        """Print the plan, or apply it."""
        if apply:
            self._apply(backlog)
            return 0
        self._out("Dry run: nothing is changed. Add --apply to run these commands.")
        plan = [
            *(self._milestone_command(milestone) for milestone in backlog.milestones),
            ["project", "create", "--owner", self._owner, "--title", self._title],
            *(self._issue_command(issue) for issue in backlog.issues),
        ]
        for command in plan:
            self._out(shlex.join(["gh", *command]))
        return 0

    def _project_number(self) -> str:
        listing = self._json("project", "list", "--owner", self._owner, "--format", "json")
        for project in (listing or {}).get("projects", []):
            if project.get("title") == self._title:
                return str(project["number"])
        created = self._json(
            "project", "create", "--owner", self._owner, "--title", self._title, "--format", "json"
        )
        self._out(f"project created: {self._title}")
        return str(created["number"])

    def _existing_titles(self, repo: str) -> set[str]:
        items = self._json(
            "issue", "list", "--repo", repo, "--state", "all", "--limit", "1000", "--json", "title"
        )
        return {item["title"] for item in items or []}

    def _apply(self, backlog: Backlog) -> None:
        existing = self._json("api", f"repos/{self._repo}/milestones?state=all&per_page=100")
        titles = {item["title"] for item in existing or []}
        for milestone in backlog.milestones:
            if milestone.title not in titles:
                self._gh.run(self._milestone_command(milestone))
                self._out(f"milestone created: {milestone.title}")
        number = self._project_number()
        known: dict[str, set[str]] = {}
        for issue in backlog.issues:
            repo = issue.repo or self._repo
            if repo not in known:
                known[repo] = self._existing_titles(repo)
            if issue.title in known[repo]:
                self._out(f"issue exists, skipped: {issue.title}")
                continue
            url = self._gh.run(self._issue_command(issue)).stdout.strip()
            self._gh.run(["project", "item-add", number, "--owner", self._owner, "--url", url])
            self._out(f"issue created: {issue.title}")


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Create a board from a backlog file.")
    parser.add_argument("--repo", required=True, help="main repository, owner/name")
    parser.add_argument("--title", required=True, help="title of the GitHub project")
    parser.add_argument("--backlog", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="really create the objects")
    args = parser.parse_args(argv)
    bootstrap = ProjectBootstrap(SubprocessGh(), args.repo, args.title, print)
    return bootstrap.run(Backlog.load(args.backlog), apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
