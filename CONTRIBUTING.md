<!-- SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Contributing to `zenzic-mcp`

This repository holds the Model Context Protocol server that exposes the Zenzic
engine to an MCP client. It is the youngest repository in the ecosystem and the
only one that has not shipped a release.

It is **not** held to a lower standard for that. The rules that govern the core
govern this repository too; where something here is genuinely different, this page
says so and says what would change it.

## Prerequisites

| Tool | Why |
| :--- | :--- |
| Python ≥ 3.10 | The engine's floor |
| [`uv`](https://docs.astral.sh/uv/) | Dependency resolution and the virtualenv |
| [`just`](https://just.systems/) | Every task in this repository is a recipe |

```bash
just setup      # create the environment and install the project
just verify     # the full gate — run this before pushing
```

## The Zenzic core dependency

`pyproject.toml` declares `zenzic~=0.31` and, for development, resolves it from a
sibling checkout:

```toml
[tool.uv.sources]
zenzic = { path = "../zenzic", editable = true }
```

So a local `just verify` tests against whatever is in `../zenzic`, not against a
published wheel. That is deliberate while this server is developed alongside the
engine, and it is the reason the declared pin can name a version that is not yet
on PyPI.

**What this repository does not have yet, and why.** Its siblings carry a
`pin-core` recipe that rewrites the declared pin and an `audit-release` recipe that
fails when the pin, the package metadata and the release document disagree. Neither
exists here, because there is no release to keep them consistent with. **The
condition that changes it**: the first time a version of this server is published,
the pin becomes a promise to a user rather than a note to a developer, and it needs
both recipes plus a check that the three agree.

## Commit requirements

Both of these are enforced by CI on every pull request, not merely requested:

1. **Sign-off.** Every commit carries a `Signed-off-by:` trailer — `git commit -s`.
   This is the Developer Certificate of Origin; a pull request with an unsigned-off
   commit fails the `Check DCO` job.
2. **Conventional pull-request titles.** The title is linted by the same
   `Lint PR Title` job the other repositories use — `feat:`, `fix:`, `chore:`,
   `docs:`, `test:`, `ci:`, `refactor:`.

Commits should also be **signed** (`git commit -S`) rather than merely signed off.
The sibling repositories enforce this with a repository ruleset; this one does not
have a ruleset yet, which is a gap rather than a difference — see below.

## Known gaps, stated rather than left to be discovered

| Gap | Status |
| :--- | :--- |
| No repository ruleset, `main` unprotected | **Open.** Every sibling requires signed commits, linear history and a pull request on its default branch. This repository requires none of them, so a direct push to `main` would succeed. Tracked for correction. |
| No `RELEASE.md` | **Deliberate.** Nothing has been released. It becomes required at the first published version. |
| No secret-scanning workflow | **Open.** Three of four repositories run one. |

## Before you push

`just verify` is the gate, and `git push` runs it through a pre-push hook, so a
failing tree cannot leave the machine. It runs the linter, the type checker, the
test suite and the REUSE licence check.

If a check fails and you believe the check is wrong, say so in the pull request
rather than working around it. A gate that is bypassed once is a gate nobody trusts
afterwards.
