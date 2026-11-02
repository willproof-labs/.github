"""Tests for tools/setup_repository.py and tools/bootstrap_project.py (gh is faked)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from tools.bootstrap_project import Backlog, ProjectBootstrap
from tools.ghcli import CommandResult
from tools.setup_repository import Label, RepositorySetup, load_labels

ROOT = Path(__file__).resolve().parents[1]


class FakeGh:
    """Records gh calls and answers from a function."""

    def __init__(self, answer=None) -> None:  # type: ignore[no-untyped-def]
        self.calls: list[list[str]] = []
        self.answer = answer or (lambda args: "")

    def run(self, args: Sequence[str]) -> CommandResult:
        self.calls.append(list(args))
        return CommandResult(list(args), 0, self.answer(list(args)), "")


# --- labels and repository settings ------------------------------------------------------
def test_the_organization_label_file_is_valid() -> None:
    labels = load_labels(ROOT / "labels.toml")
    names = [label.name for label in labels]

    assert len(names) == len(set(names))
    assert {"type:bug", "type:feature", "type:experiment", "upstream"} <= set(names)
    assert all(len(label.color) == 6 for label in labels)


def test_dry_run_prints_commands_and_changes_nothing() -> None:
    gh = FakeGh()
    lines: list[str] = []
    setup = RepositorySetup(gh, lines.append)

    setup.run("willproof-labs/edge-smith", [Label("type:bug", "d73a4a", "Broken")], True, False)

    assert gh.calls == []
    plan = "\n".join(lines)
    assert "--enable-rebase-merge" in plan
    assert "--enable-squash-merge=false" in plan
    assert "--add-topic willproof-product" in plan
    assert "gh label create type:bug" in plan


def test_apply_runs_the_same_commands() -> None:
    gh = FakeGh()

    RepositorySetup(gh, lambda line: None).run(
        "willproof-labs/edge-smith", [Label("type:bug", "d73a4a", "Broken")], False, True
    )

    edit = next(call for call in gh.calls if call[:2] == ["repo", "edit"])
    assert "--enable-merge-commit=false" in edit
    assert "--delete-branch-on-merge" in edit
    assert "--add-topic" not in edit  # not a product: no topic
    assert any(call[:2] == ["label", "create"] for call in gh.calls)


# --- project bootstrap -------------------------------------------------------------------
def write_backlog(tmp_path: Path) -> Path:
    path = tmp_path / "backlog.toml"
    path.write_text(
        '[[milestones]]\ntitle = "Phase 1"\ndescription = "Core"\n'
        '[[issues]]\ntitle = "First"\nbody = "Do it"\nlabels = ["type:bug"]\n'
        'milestone = "Phase 1"\n'
        '[[issues]]\ntitle = "Second"\nbody = "Then"\nlabels = []\nmilestone = "Phase 1"\n'
        '[[issues]]\ntitle = "Elsewhere"\nbody = "In the hub"\nlabels = []\n'
        'repo = "willproof-labs/willproof"\n',
        encoding="utf-8",
    )
    return path


def test_backlog_issues_default_to_the_main_repository(tmp_path: Path) -> None:
    backlog = Backlog.load(write_backlog(tmp_path))

    repos = [issue.repo or "default" for issue in backlog.issues]

    assert repos == ["default", "default", "willproof-labs/willproof"]


def test_bootstrap_dry_run_plans_every_object(tmp_path: Path) -> None:
    gh = FakeGh()
    lines: list[str] = []

    ProjectBootstrap(gh, "willproof-labs/edge-smith", "edge-smith", lines.append).run(
        Backlog.load(write_backlog(tmp_path)), apply=False
    )

    plan = "\n".join(lines)
    assert gh.calls == []
    assert "gh project create --owner willproof-labs --title edge-smith" in plan
    assert "--repo willproof-labs/willproof --title Elsewhere" in plan


def test_bootstrap_apply_is_idempotent(tmp_path: Path) -> None:
    def answer(args: list[str]) -> str:
        if args[:2] == ["issue", "list"]:
            return json.dumps([{"title": "First"}])
        if args[:1] == ["api"] and "milestones" in args[1]:
            return json.dumps([{"title": "Phase 1"}])
        if args[:2] == ["project", "list"]:
            return json.dumps({"projects": [{"title": "edge-smith", "number": 7}]})
        if args[:2] == ["issue", "create"]:
            return "https://github.com/willproof-labs/x/issues/9\n"
        return ""

    gh = FakeGh(answer)

    ProjectBootstrap(gh, "willproof-labs/edge-smith", "edge-smith", lambda line: None).run(
        Backlog.load(write_backlog(tmp_path)), apply=True
    )

    created = [call for call in gh.calls if call[:2] == ["issue", "create"]]
    titles = [call[call.index("--title") + 1] for call in created]
    assert titles == ["Second", "Elsewhere"]  # "First" already exists
    assert not any(call[:2] == ["project", "create"] for call in gh.calls)
    assert not any("POST" in call for call in gh.calls)  # milestone already exists
    assert [
        "project",
        "item-add",
        "7",
        "--owner",
        "willproof-labs",
        "--url",
        "https://github.com/willproof-labs/x/issues/9",
    ] in gh.calls


def test_the_lab_backlog_is_valid() -> None:
    backlog = Backlog.load(ROOT / "project" / "lab-backlog.toml")
    labels = {label.name for label in load_labels(ROOT / "labels.toml")}

    assert backlog.issues
    for issue in backlog.issues:
        assert issue.repo, "lab issues always name their repository"
        assert set(issue.labels) <= labels, issue.title
