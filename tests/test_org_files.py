"""Tests for the files GitHub applies to every repository of the organization."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
FIRST_PARTY = re.compile(r"^(actions|github)/[\w.-]+@(v\d+|[0-9a-f]{40})$")
_FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.MULTILINE | re.DOTALL)
_HEADING = re.compile(r"^(#{1,6}) ", re.MULTILINE)


def load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def triggers(workflow: dict[Any, Any]) -> Any:
    return workflow.get("on", workflow.get(True))


def steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for job in workflow["jobs"].values() for step in job.get("steps", [])]


def all_workflows() -> list[Path]:
    return sorted([*WORKFLOWS.glob("*.yml"), *(ROOT / "workflow-templates").glob("*.yml")])


# --- community health files -----------------------------------------------------------------
def test_default_community_files_exist() -> None:
    for name in (
        "CONTRIBUTING.md",
        "CONTRIBUTING.fr.md",
        "SECURITY.md",
        "pull_request_template.md",
        "profile/README.md",
    ):
        assert (ROOT / name).is_file(), name


def test_issue_forms_are_valid() -> None:
    forms = sorted((ROOT / "ISSUE_TEMPLATE").glob("*.yml"))

    assert {form.name for form in forms} >= {
        "bug.yml",
        "feature.yml",
        "experiment.yml",
        "config.yml",
    }
    for form in forms:
        data = load(form)
        if form.name != "config.yml":
            assert data["name"] and data["description"] and data["body"], form.name


def test_the_profile_lists_only_public_projects() -> None:
    profile = (ROOT / "profile" / "README.md").read_text(encoding="utf-8")

    for private in ("edge-smith", "waymark", "willproof-runtime"):
        assert private not in profile


# --- workflows ----------------------------------------------------------------------------
@pytest.mark.parametrize("path", all_workflows(), ids=lambda p: p.name)
def test_workflows_are_read_only_and_first_party(path: Path) -> None:
    workflow = load(path)

    assert workflow["permissions"] == {"contents": "read"}
    for step in steps(workflow):
        if "uses" in step:
            assert FIRST_PARTY.match(step["uses"]), step["uses"]
        if str(step.get("uses", "")).startswith("actions/checkout"):
            assert step["with"]["persist-credentials"] is False


@pytest.mark.parametrize("name", ["commit-conventions.yml", "gitleaks.yml"])
def test_shared_workflows_are_reusable(name: str) -> None:
    assert "workflow_call" in triggers(load(WORKFLOWS / name))


def test_workflow_templates_have_their_properties_file() -> None:
    for template in (ROOT / "workflow-templates").glob("*.yml"):
        properties = template.with_suffix(".properties.json")
        data = json.loads(properties.read_text(encoding="utf-8"))
        assert data["name"] and data["description"]


# --- documentation in two languages -------------------------------------------------------
PAIRS = [("README.md", "README.fr.md"), ("CONTRIBUTING.md", "CONTRIBUTING.fr.md")]


def structure(text: str) -> tuple[list[int], list[str]]:
    code = [
        "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("#"))
        for _, body in _FENCE.findall(text)
    ]
    return [len(h) for h in _HEADING.findall(_FENCE.sub("", text))], code


@pytest.mark.parametrize(("english", "french"), PAIRS)
def test_both_languages_have_the_same_structure(english: str, french: str) -> None:
    en = (ROOT / english).read_text(encoding="utf-8")
    fr = (ROOT / french).read_text(encoding="utf-8")

    assert structure(en) == structure(fr)
