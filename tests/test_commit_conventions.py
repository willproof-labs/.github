"""Tests for tools/commit_conventions.py: commit messages, branch names and the TDD rule."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools.commit_conventions import (
    Commit,
    check_branch,
    check_message,
    check_range,
    check_tdd_order,
)

GOOD = "feat(engines): add the ONNX Runtime engine\n\nWhy it matters.\n\nRefs #12\n"


def test_a_conventional_message_with_a_reference_passes() -> None:
    assert check_message(GOOD) == []


@pytest.mark.parametrize(
    "header",
    [
        "test: specify the ONNX engine",
        "fix: read multi-word principals",
        "docs(readme): add a pitch",
        "feat!: rename the command",
        "refactor(core)!: split the registry",
    ],
)
def test_every_documented_form_of_header_is_accepted(header: str) -> None:
    assert check_message(f"{header}\n\nRefs #3\n") == []


@pytest.mark.parametrize(
    ("message", "fragment"),
    [
        ("Add an engine\n\nRefs #1\n", "type"),
        ("feature: add an engine\n\nRefs #1\n", "type"),
        ("feat:add an engine\n\nRefs #1\n", "type"),
        ("feat: add an engine\n", "Refs #"),
        ("feat: " + "x" * 80 + "\n\nRefs #1\n", "72"),
    ],
)
def test_bad_messages_explain_what_is_wrong(message: str, fragment: str) -> None:
    problems = check_message(message)

    assert problems
    assert any(fragment in problem for problem in problems)


def test_closes_and_fixes_also_count_as_references() -> None:
    assert check_message("fix: handle empty files\n\nCloses #8\n") == []
    assert check_message("fix: handle empty files\n\nFixes #8, #9\n") == []


def test_git_comment_lines_are_ignored() -> None:
    assert check_message(GOOD + "# Please enter the commit message\n# On branch feat/12-x\n") == []


@pytest.mark.parametrize(
    "message",
    ["Merge branch 'main' into feat/3-x\n", 'Revert "feat: x"\n', "fixup! feat: x\n"],
)
def test_merges_reverts_and_autosquash_commits_are_exempt(message: str) -> None:
    assert check_message(message) == []


# --- TDD order -----------------------------------------------------------------------------
def commit(message: str, author: str = "Wilson FRED") -> Commit:
    return Commit(sha="0" * 40, author=author, message=message)


def test_a_feature_must_follow_a_test_commit() -> None:
    commits = [commit("feat: add x\n\nRefs #1"), commit("test: specify x\n\nRefs #1")]

    problems = check_tdd_order(commits)

    assert problems and "test:" in problems[0]


def test_test_then_feature_respects_the_rule() -> None:
    commits = [commit("test: specify x\n\nRefs #1"), commit("feat: add x\n\nRefs #1")]

    assert check_tdd_order(commits) == []


def test_documentation_and_tooling_commits_need_no_test() -> None:
    commits = [commit("docs: explain x\n\nRefs #1"), commit("ci: cache poetry\n\nRefs #2")]

    assert check_tdd_order(commits) == []


def test_an_explicit_exemption_is_accepted() -> None:
    message = "fix: correct a typo in a message\n\nRefs #4\n\nTDD-Exempt: wording only"

    assert check_tdd_order([commit(message)]) == []


# --- branches ------------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["feat/12-onnx-engine", "fix/31-icacls", "docs/7-pitch"])
def test_conventional_branch_names_pass(name: str) -> None:
    assert check_branch(name) == []


@pytest.mark.parametrize("name", ["onnx", "feat/onnx-engine", "feature/12-onnx", "feat/12_Onnx"])
def test_other_branch_names_are_refused(name: str) -> None:
    assert check_branch(name)


def test_dependabot_branches_are_exempt() -> None:
    assert check_branch("dependabot/pip/ruff-0.17.0") == []


# --- a real repository ---------------------------------------------------------------------
def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "chore: start")
    return tmp_path


def add_commit(repo: Path, message: str) -> None:
    git(repo, "commit", "-q", "--allow-empty", "-m", message)


def test_range_check_reads_the_commits_of_a_pull_request(repo: Path) -> None:
    base = git(repo, "rev-parse", "HEAD").strip()
    add_commit(repo, "test: specify x\n\nRefs #1")
    add_commit(repo, "feat: add x\n\nRefs #1")

    assert check_range(repo, f"{base}..HEAD") == []


def test_range_check_reports_each_bad_commit(repo: Path) -> None:
    base = git(repo, "rev-parse", "HEAD").strip()
    add_commit(repo, "feat: add x")

    problems = check_range(repo, f"{base}..HEAD")

    assert any("Refs #" in problem for problem in problems)
    assert any("test:" in problem for problem in problems)


def test_the_script_works_as_a_commit_msg_hook(tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "tools" / "commit_conventions.py"
    good, bad = tmp_path / "good", tmp_path / "bad"
    good.write_text(GOOD, encoding="utf-8")
    bad.write_text("wip\n", encoding="utf-8")

    ok = subprocess.run([sys.executable, str(script), str(good)], capture_output=True, text=True)
    ko = subprocess.run([sys.executable, str(script), str(bad)], capture_output=True, text=True)

    assert ok.returncode == 0
    assert ko.returncode == 1
    assert "type" in ko.stderr
