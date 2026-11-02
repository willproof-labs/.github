# Contributing to WillProof Labs

*[Version française](CONTRIBUTING.fr.md)*

Thank you for your interest. These rules apply to every repository of the organization,
unless a project's own `CONTRIBUTING.md` says otherwise. They are meant to stay light:
each one exists because it protects something that matters.

## Before you start

- **Every change starts from an issue.** Open one (bug, feature or experiment form), or
  pick one from the project's board, and say you are on it.
- **Reuse before building.** Check which existing tool already does part of the job;
  the issue forms ask for it.
- **Never share anything identifying or secret**: machine names, user names, personal
  paths, keys, real personal data.

## Commits and branches

Branches are named after the issue: `type/<issue number>-short-description`.

```text
feat/12-onnx-engine
fix/31-icacls-parsing
docs/7-readme-pitch
```

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) and
reference their issue:

```text
feat(engines): add the ONNX Runtime engine

Why the change is needed, in a few lines if it is not obvious.

Refs #12
```

| Type | For |
|---|---|
| `test` | a test, usually written before the code it specifies |
| `feat` | a new capability |
| `fix` | a bug fix |
| `refactor` | a change that alters neither behaviour nor tests |
| `docs` | documentation only |
| `ci`, `build`, `chore` | pipelines, packaging, maintenance |
| `perf` | a measured performance improvement |

`feat!:` (with `!`) marks a breaking change. The first line has 72 characters at most.

## Test-driven development

We write the failing test first, commit it (`test:`), then make it pass (`feat:` or
`fix:`). In a pull request, a `feat` or `fix` commit must come after at least one `test`
commit. When a test really makes no sense (a typo in a message, for instance), add a
trailer that says why:

```text
fix: correct a typo in an error message

Refs #44

TDD-Exempt: wording only, no behaviour to specify
```

The CI checks commit messages, branch names and this order on every pull request. To
check messages before they are even created, install the hook shipped with each project
(see its `DEVELOPMENT` documentation).

## Pull requests

- One pull request per issue; its description says `Closes #<issue>`.
- Pull requests are merged with **rebase**: each commit reaches `main` as it is, so the
  test-first history stays readable. Squash and merge commits are disabled.
- `main` only changes through pull requests whose checks are green.

## Definition of Done

A change is done when:

1. its tests were written first, and every test passes;
2. lint, formatting and type checks pass;
3. documentation is up to date **in English and in French**;
4. nothing identifying or secret is committed;
5. the pull request is reviewed and merged.

## Documentation in two languages

Code, comments and commit messages are in English. Documentation exists in English and
in French, changed together in the same pull request: a language barrier should never
keep a good developer out.

## Working with AI assistants

AI assistants are welcome, used openly:

- declare their use in the pull request (which assistant, for what);
- commits written with an assistant carry a `Co-Authored-By` trailer naming it;
- a person always reviews and merges; assistants never push to `main`;
- assistants get the narrowest access possible (one repository, pull requests only);
- you remain responsible for what you submit: understand it before you open the pull
  request.

## Security

Never report a vulnerability in a public issue: see [SECURITY.md](SECURITY.md).
