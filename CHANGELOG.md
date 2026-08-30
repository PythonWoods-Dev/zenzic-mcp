<!-- SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Changelog

All notable changes to `zenzic-mcp` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/), independently from Zenzic Core —
see `.claude/state/01-manifest.md` for the versioning model.

---

## [Unreleased]

### Added

- **Repository Bootstrap**: initial `pyproject.toml` (`v0.1.0`), with `zenzic~=0.31` as a
  Track-2 project dependency (resolved locally via `[tool.uv.sources]` to the sibling `../zenzic`
  checkout until v0.31.0 ships to PyPI).
- **MCP Server Skeleton**: stdio transport, built on the official `mcp` SDK's low-level
  `Server`/request-handler API (not FastMCP) — a deliberate choice: explicit payload
  construction is easier to audit against this project's MCP-specific invariants than
  decorator-generated schema/response shaping would be.
- **First Tool: `check_document(repo_root, path)`**: a thin wrapper over
  `zenzic.core.incremental.IncrementalAnalysisEngine` — the same transport-agnostic Core entry
  point the Language Server Protocol server uses — rather than the CLI's private orchestration
  functions, which carry no external stability contract. Returns findings for the requested file
  only, never a full site dump (MCP-specific Invariant 1). Verified to match
  `zenzic check all <file>` exactly on three cases (clean file, content-defect fixture,
  security-breach fixture).
- **Secret Redaction Test (Invariant 2)**: `tests/test_secret_redaction.py` plants a known fake
  secret, drives the real MCP wire protocol end-to-end, and asserts the raw secret is absent from
  the full serialized `tools/call` response payload — not just from one field.

### Fixed

- **Missing `LICENSE` File**: `pyproject.toml` already declared `license = "Apache-2.0"`, but no `LICENSE` file existed in the repository, unlike the sibling `zenzic`/`zenzic-action`/`zenzic-vscode` repos. Added the standard Apache-2.0 text with matching copyright line.
- **`check_document`'s Tool Handler Only Caught `DocumentNotFoundError` — Any Other Exception Propagated Unhandled Past the MCP Wire Boundary**:
  - Confirmed live with a real, natural failure mode (not a synthetic one): a project declaring `engine = "zensical"` in `.zenzic.toml` with neither `zensical.toml` nor `mkdocs.yml` present raises a real `zenzic.core.exceptions.ZenzicConfigError` from `check_document()`. Traced the real MCP SDK behavior for this case, which the original finding had left undetermined: the server process itself does not crash, but the exception leaks past the tool handler as a raw client-side `MCPError` instead of a controlled `CallToolResult(is_error=True)`. Added a catch-all `except Exception` around the `check_document()` call, matching the existing `DocumentNotFoundError` branch's shape. TDD-first: `tests/test_exception_handling.py`, confirmed genuinely red (the uncaught `ZenzicConfigError` surfaced as an `MCPError` on the client side) before the fix, green after.

### Known Limitations

- **Cache Invalidation (Invariant 3) Not Yet Designed**: `check_document` is currently fully
  stateless — it builds a fresh `IncrementalAnalysisEngine` per call. The in-memory, cross-call
  caching Invariant 3 describes is future work, deferred until a second Tool's requirements make
  the right caching strategy clearer rather than guessing at it now with only one consumer.
- **CLI/LSP Topology Divergence Inherited from Core**: `check_document` is built on
  `IncrementalAnalysisEngine`, which does not share a topology-detection algorithm with the
  CLI's `check_all` (`Z402` nav-based vs. `Z410`/`Z411` graph-based — see the Core repository's
  `CHANGELOG.md` and ADR vault). `check_document` results reflect the LSP-side algorithm; a
  future Tool that needs `check_all`-equivalent topology output should verify this divergence is
  resolved or accounted for first.
