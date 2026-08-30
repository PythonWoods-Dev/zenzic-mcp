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
lint:
    {{ runner }} ruff check .
    {{ runner }} mypy src

# Full local gate: everything CI runs, in one command.
verify: lint test-cov
