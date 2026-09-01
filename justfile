# SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
# SPDX-License-Identifier: Apache-2.0
#
# ZRT-010 — Sovereign Parity: local and CI run identical invocations.
# Mirrors the ../zenzic and ../zenzic-action justfiles' recipe naming
# convention (test / test-cov / verify), scaled down to this repo's
# bootstrap-stage size.

set shell := ["bash", "-c"]

runner := "uv run"

# Fast inner loop: no coverage.
test *args:
    {{ runner }} pytest {{ args }}

# Audit run: coverage enforced (fail_under=75 via pyproject.toml).
test-cov *args:
    {{ runner }} pytest --cov=src/zenzic_mcp --cov-report=term-missing {{ args }}

# Static checks: lint + type-check.
# `[tool.uv.sources]` in pyproject.toml points the zenzic constraint at the
# sibling checkout, so this yields an editable Core install for local work.
# The hook install is part of setup rather than a step to remember: this
# repository was once found with no hooks installed at all, the precondition
# Rule 31 blocks on. Running setup makes that self-healing.
#
# Bootstrap a fresh clone: install dependencies and git hooks.
setup:
    uv sync --all-groups
    uvx pre-commit install -t pre-commit -t pre-push
    @echo "Setup complete. Run 'just verify' to check everything passes."

lint:
    {{ runner }} ruff check .
    {{ runner }} ruff format --check .
    {{ runner }} mypy src
    {{ runner }} reuse lint

# Full local gate: everything CI runs, in one command.
verify: _check-hooks lint test-cov

# Blocking gate, not a warning. A pre-commit hook that is merely declared in
# .pre-commit-config.yaml runs nothing: the hook has to be installed into
# .git/hooks for the commit-time gate to exist at all. Three of the four
# ecosystem repositories were found with no hook installed, so every commit
# in them bypassed markdownlint, REUSE and the formatter silently.
#
# A missing pre-commit hook cannot block its own commit -- there is nothing
# installed to run -- so this check fails `just verify` instead, which is the
# pre-push path and what CI runs. Exit 1, never a warning: the previous
# version of this recipe printed the same diagnosis and let the work proceed.
# Blocking gate, not a warning. A pre-commit hook that is merely declared in
# .pre-commit-config.yaml runs nothing: the hook has to be installed into
# .git/hooks for the commit-time gate to exist at all. Three of the four
# ecosystem repositories were found with no hook installed, so every commit
# in them bypassed markdownlint, REUSE and the formatter silently.
#
# A missing pre-commit hook cannot block its own commit -- there is nothing
# installed to run -- so this check fails `just verify` instead, which is the
# pre-push path and what CI runs. Exit 1, never a warning: the previous
# version of this recipe printed the same diagnosis and let the work proceed.
_check-hooks:
    #!/usr/bin/env bash
    set -euo pipefail
    # CI checks out a bare working tree and never commits from it, so git hooks
    # are meaningless there -- and requiring them would fail every run for a
    # condition no CI job can or should fix. The gate exists for the machine
    # where commits are actually authored.
    if [ -n "${CI:-}" ]; then
        echo "CI environment: git-hook check skipped (hooks gate local commits only)"
        exit 0
    fi
    _missing=0
    for _h in pre-commit pre-push; do
        if [ ! -f ".git/hooks/${_h}" ] || ! grep -qi "pre-commit" ".git/hooks/${_h}"; then
            echo -e "\033[31mBLOCKED: the ${_h} hook is not installed (or is not pre-commit's).\033[0m"
            echo "  Without it the ${_h} gate does not run, and defects reach the remote."
            echo "  Fix: uvx pre-commit install -t ${_h}"
            _missing=1
        fi
    done
    if [ "${_missing}" -ne 0 ]; then
        echo ""
        echo "Refusing to continue with an uninstalled git hook. See Rule 31."
        exit 1
    fi
    echo "git hooks installed (pre-commit, pre-push)"
