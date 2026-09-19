# SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
# SPDX-License-Identifier: Apache-2.0
"""check_document() must never serve a stale adapter across calls.

zenzic Core's get_adapter() (zenzic.core.adapters._factory) caches adapter
instances for the process lifetime, keyed by (engine, docs_root, repo_root)
-- deliberately, to avoid redundant construction "when called from multiple
modules in the same CLI session" (its own docstring). That rationale does
not hold for zenzic-mcp: check_document() is the only caller in the process,
and already rebuilds config/md_contents/vsm/engine from scratch on every
call -- it has no legitimate reuse to protect. Since check_document() never
called clear_adapter_cache(), the long-running MCP server process (same
long-lived shape as the LSP) could keep serving an adapter built from a
now-stale mkdocs.yml/.zenzic.toml for its entire lifetime, contradicting the
server's own CHANGELOG claim of being "fully stateless."

Reproduced directly (V031_ECOSYSTEM_CACHE_AUDIT_AND_CLAUDE_CENTRALIZATION,
Phase 1): two get_adapter() calls in the same process, same cache key, with
mkdocs.yml's use_directory_urls flipped in between, returned the identical
cached adapter object with the stale value -- confirmed empirically, not
theorized.
"""

from __future__ import annotations

from pathlib import Path

from zenzic.core.adapters import get_adapter
from zenzic.models.config import load_config_with_diagnostics

from zenzic_mcp.analysis import check_document


def _current_use_directory_urls(repo_root: Path) -> bool:
    """Ask get_adapter() directly, exactly as check_document() does internally,
    to observe whatever adapter instance is currently cached for this repo."""
    config, _ = load_config_with_diagnostics(repo_root)
    docs_root = (repo_root / config.docs_dir).resolve()
    adapter = get_adapter(config.build_context, docs_root, repo_root)
    return bool(adapter.use_directory_urls)


def test_check_document_does_not_serve_a_stale_adapter_across_calls(tmp_path: Path) -> None:
    """A real mkdocs.yml edit between two check_document() calls in the same
    process must be reflected on the second call, not silently ignored."""
    (tmp_path / ".zenzic.toml").write_text('[build_context]\nengine = "mkdocs"\n', encoding="utf-8")
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Test\nuse_directory_urls: true\n", encoding="utf-8"
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    target = docs / "index.md"
    target.write_text("# Home\n", encoding="utf-8")

    check_document(tmp_path, target)
    assert _current_use_directory_urls(tmp_path) is True

    # Real mid-session edit -- engine/docs_root/repo_root (the cache key)
    # unchanged, so a naive process-lifetime cache would miss this.
    (tmp_path / "mkdocs.yml").write_text(
        "site_name: Test\nuse_directory_urls: false\n", encoding="utf-8"
    )

    check_document(tmp_path, target)
    assert _current_use_directory_urls(tmp_path) is False, (
        "check_document() served a stale cached adapter after a real "
        "mkdocs.yml edit -- the second call's adapter must reflect the "
        "current use_directory_urls, not the value from the first call."
    )
