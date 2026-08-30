# SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
# SPDX-License-Identifier: Apache-2.0
"""Bridges MCP Tool calls to the Zenzic Core engine.

Uses ``zenzic.core.incremental.IncrementalAnalysisEngine`` — the same
transport-agnostic entry point the Language Server Protocol server is built
on (ADR-075) — rather than the CLI's internal orchestration functions, which
are private to ``zenzic.cli`` and carry no stability contract for external
consumers.

Per MCP-specific Invariant 1 (no VSM dumps), this module's public functions
return only the diagnostics for the file(s) actually requested, never a full
site topology or baseline dump.
"""

from __future__ import annotations

from pathlib import Path

from zenzic.core.adapters import get_adapter
from zenzic.core.codes import NON_SUPPRESSIBLE_CODES
from zenzic.core.discovery import iter_markdown_sources
from zenzic.core.exclusion import LayeredExclusionManager
from zenzic.core.incremental import IncrementalAnalysisEngine
from zenzic.core.scanner import _build_rule_engine
from zenzic.models.config import ZenzicConfig
from zenzic.models.diagnostics import ZenzicDiagnostic
from zenzic.models.vsm import VirtualBufferOverlay, build_vsm


class DocumentNotFoundError(Exception):
    """Raised when the requested path does not resolve to a tracked Markdown file."""


class SecretLeakError(Exception):
    """Raised when a Z2xx diagnostic's message appears to carry raw secret material.

    This should be structurally unreachable: ``IncrementalAnalysisEngine.
    _findings_to_diagnostics`` builds ``ZenzicDiagnostic.message`` from
    ``RuleFinding.message`` only, never from ``RuleFinding.match_text`` (where
    the Core's credential scanner puts the raw matched secret) — so the LSP
    diagnostic channel this module consumes never carries raw secret text by
    construction. This guard exists per MCP-specific Invariant 2 ("do not
    assume the CLI-path masking behaves identically here without verifying
    it") as a fail-closed check against that assumption ever silently
    breaking in a future Core refactor, rather than as an active redaction
    step (there is nothing here to redact under the current Core contract).
    """


_SECRET_LEAK_MARKERS = ("AKIA", "ghp_", "-----BEGIN")
"""Cheap, non-exhaustive heuristics for common raw-secret prefixes.

Not a substitute for the Core's own credential scanner — this only guards
the narrow claim in ``SecretLeakError``'s docstring, i.e. that this specific
message-construction path never leaks a raw match. It does not attempt to
catch every possible secret shape.
"""


def _check_no_secret_leak(diag: ZenzicDiagnostic) -> ZenzicDiagnostic:
    """Fail closed if a Z2xx diagnostic's message contains raw secret material.

    Implemented as an explicit ``if``/``raise``, deliberately not a Python
    ``assert`` statement — ``assert`` is stripped when the interpreter runs
    under ``-O``/``PYTHONOPTIMIZE=1``, which would silently disable this
    check in an optimized deployment. This check stays active regardless of
    interpreter flags.

    See :class:`SecretLeakError` for why this is a fail-closed guard rather
    than a redaction step: the upstream Core code path already guarantees
    diagnostic messages never carry raw secrets. If it ever does, this
    raises rather than letting the leak reach the MCP client silently.
    """
    if diag.code not in NON_SUPPRESSIBLE_CODES:
        return diag
    if any(marker in diag.message for marker in _SECRET_LEAK_MARKERS):
        raise SecretLeakError(
            f"Z-code {diag.code} diagnostic message appears to contain raw "
            f"secret material — refusing to return it to the MCP client."
        )
    return diag


def check_document(repo_root: Path, target: Path) -> list[ZenzicDiagnostic]:
    """Run a full Zenzic check and return diagnostics for a single document.

    Builds a fresh ``IncrementalAnalysisEngine`` scoped to *repo_root* and
    performs one full-workspace sync (required for cross-file checks such as
    dangling references and topology), then returns only the diagnostics for
    *target* — never the full per-URI mapping for the whole site (Invariant 1).

    Args:
        repo_root: Absolute path to the repository root.
        target: Absolute path to the Markdown file to check.

    Returns:
        Diagnostics for *target*, checked for secret leaks per
        :func:`_check_no_secret_leak`. Empty list if the file is clean.

    Raises:
        DocumentNotFoundError: *target* does not exist or is not a Markdown
            file discoverable under the resolved ``docs_dir``.
    """
    from zenzic.models.config import load_config_with_diagnostics

    config, _ = load_config_with_diagnostics(repo_root)
    config = config or ZenzicConfig()
    docs_root = (repo_root / config.docs_dir).resolve()
    target = target.resolve()

    exclusion_mgr = LayeredExclusionManager(config, repo_root=repo_root, docs_root=docs_root)
    if not target.is_file() or target not in set(
        iter_markdown_sources(docs_root, config, exclusion_mgr)
    ):
        raise DocumentNotFoundError(
            f"{target} is not a tracked Markdown file under {docs_root}"
        )

    md_contents: dict[Path, str] = {}
    for md_file in iter_markdown_sources(docs_root, config, exclusion_mgr):
        try:
            md_contents[md_file.resolve()] = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

    adapter = get_adapter(config.build_context, docs_root, repo_root)
    vsm = build_vsm(adapter, docs_root, md_contents, repo_root=repo_root)
    overlay = VirtualBufferOverlay(vsm)

    rule_engine = _build_rule_engine(config)
    if rule_engine is None:
        return []

    engine = IncrementalAnalysisEngine(
        config=config,
        rule_engine=rule_engine,
        adapter=adapter,
        docs_root=docs_root,
        repo_root=repo_root,
    )
    diagnostics_by_uri = engine.process_changes(vsm, overlay, changed_uris=None)

    target_uri = target.as_uri()
    return [_check_no_secret_leak(d) for d in diagnostics_by_uri.get(target_uri, [])]
