# WillProof Labs: shared organization files

*[Version française](README.fr.md)*

This special repository holds what every WillProof Labs repository shares. GitHub reads it
automatically; it must stay **public** for that, and it contains nothing sensitive.

## What GitHub does with it

| Here | Effect on every repository of the organization |
|---|---|
| `profile/README.md` | the organization's home page on GitHub |
| `CONTRIBUTING.md`, `SECURITY.md`, `pull_request_template.md`, `ISSUE_TEMPLATE/` | used by default by any repository that has no file of its own (private ones included) |
| `workflow-templates/` | offered in the *Actions > New workflow* tab |
| `.github/workflows/commit-conventions.yml`, `gitleaks.yml` | reusable workflows that each repository calls in one line |

A repository that needs different rules simply adds its own file, which takes precedence.

## Tools

The tools use the Python standard library only.

| Tool | Purpose |
|---|---|
| `tools/commit_conventions.py` | checks commit messages, branch names and the test-first order; used by CI and as a local `commit-msg` hook (projects copy this single file) |
| `tools/setup_repository.py` | applies the merge policy (rebase only), the shared labels of `labels.toml` and, for products, the `willproof-product` topic |
| `tools/bootstrap_project.py` | creates a board, its milestones and issues from a backlog file; idempotent |

Every tool prints its plan and changes nothing without `--apply`. `gh` must be logged in,
with the `project` scope for the boards:

```bash
gh auth login
gh auth refresh -s project
```

## Starting a new product

1. Create the repository from the template **willproof-template-python** (*Use this
   template*), private until a first version works.
2. Rename the template's package (see its README), then commit.
3. Apply the standard settings and labels:

```bash
python -m tools.setup_repository --repo willproof-labs/my-product --product
python -m tools.setup_repository --repo willproof-labs/my-product --product --apply
```

4. Create the product's board from its backlog seed, then delete the seed file in a
   commit that references the bootstrap issue: from then on, issues are the backlog.

```bash
python -m tools.bootstrap_project --repo willproof-labs/my-product --title my-product --backlog ../my-product/.github/project/backlog.toml --apply
```

## The lab board

Each product has its own board. The **WillProof Lab** board only holds what links
projects or concerns the lab itself: dependencies, cross-project experiments, shared
decisions. Its seed is `project/lab-backlog.toml`:

```bash
python -m tools.bootstrap_project --repo willproof-labs/willproof --title "WillProof Lab" --backlog project/lab-backlog.toml --apply
```

## Going public

When a product becomes public:

- [ ] add the `LICENSE` file (GitHub offers the templates: *Add file > Create new file*,
  name it `LICENSE`)
- [ ] protect `main`: pull requests only, checks required (free for public repositories)
- [ ] uncomment the badges block of its README
- [ ] add it to the *Projects* list of `profile/README.md`, in both languages

## Development

```bash
poetry install
poetry run pytest
```
