# SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
# SPDX-License-Identifier: Apache-2.0
"""MCP-specific Invariant 2: no raw secret ever reaches a Tool response.

Plants a known, deliberately fake AWS access key in a fixture document, then
drives the *actual* MCP wire protocol (client `tools/call` -> server -> the
full serialized JSON payload the client receives) and asserts the raw secret
string does not appear anywhere in that payload -- not just in the
``message`` field of an individual diagnostic, which earlier inspection
showed is where the Core's ``IncrementalAnalysisEngine`` already keeps raw
secret material out by construction (it builds diagnostic messages from
``RuleFinding.message``, never ``RuleFinding.match_text``, where the raw
match lives). This test verifies that guarantee holds at the wire boundary,
rather than assuming it from reading the Core source.
"""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.server import NotificationOptions
from mcp.shared.memory import create_client_server_memory_streams

from zenzic_mcp.server import server

RAW_SECRET = "AKIAIOSFODNN7EXAMPLE1234"  # noqa: S105 -- known-fake AWS key literal for the test


@pytest.fixture
def secret_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """A minimal Zenzic project whose docs contain a real, detectable secret."""
    (tmp_path / ".zenzic.toml").write_text(
        textwrap.dedent("""\
            docs_dir = "docs"

            [build_context]
            engine = "standalone"
        """),
        encoding="utf-8",
    )
    doc = tmp_path / "docs" / "index.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(
        textwrap.dedent(f"""\
            # Cloud Setup

            This page documents cloud provider configuration steps for the
            deployment pipeline, including credential rotation guidance for
            reviewers who need enough context to act on this finding.

            access_key: {RAW_SECRET}
        """),
        encoding="utf-8",
    )
    return tmp_path, doc


async def _call_check_document(repo_root: Path, rel_path: str) -> str:
    """Drive the real MCP wire protocol and return the full serialized payload."""
    async with create_client_server_memory_streams() as (client_streams, server_streams):
        client_read, client_write = client_streams
        server_read, server_write = server_streams

        async def run_server() -> None:
            await server.run(
                server_read,
                server_write,
                server.create_initialization_options(notification_options=NotificationOptions()),
            )

        server_task = asyncio.create_task(run_server())
        try:
            async with ClientSession(client_read, client_write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "check_document",
                    {"repo_root": str(repo_root), "path": rel_path},
                )
                return result.model_dump_json()
        finally:
            server_task.cancel()


def test_check_document_never_leaks_raw_secret(
    secret_fixture: tuple[Path, Path],
) -> None:
    """The full wire payload from tools/call must never contain the raw secret."""
    repo_root, doc = secret_fixture

    payload = asyncio.run(_call_check_document(repo_root, "docs/index.md"))

    assert RAW_SECRET not in payload, (
        f"Raw secret leaked into the MCP tool response payload:\n{payload}"
    )
    # Sanity check the test actually exercised the credential-detection path --
    # a payload with no Z201 finding at all would make the assertion above
    # vacuously true without proving anything.
    assert "Z201" in payload, (
        f"Expected a Z201 finding to be present (proving the secret was "
        f"detected and then kept out of the payload, not just absent because "
        f"detection didn't run):\n{payload}"
    )


def test_check_document_clean_file_has_no_findings(tmp_path: Path) -> None:
    """Regression guard: a file with no secrets and no other issues is clean."""
    (tmp_path / ".zenzic.toml").write_text(
        textwrap.dedent("""\
            docs_dir = "docs"

            [build_context]
            engine = "standalone"
        """),
        encoding="utf-8",
    )
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    # Z411 DEAD_END_NODE requires an internal outgoing link (an external URL
    # does not count), so this fixture links to a real second page to stay
    # genuinely clean rather than just short-content-free.
    (docs_dir / "index.md").write_text(
        textwrap.dedent("""\
            # Clean Page

            This page contains only benign prose with no credentials and no
            forbidden schemes. It links to the [guide](guide.md) page. That
            link keeps this page from being a structural dead end. The page
            also stays well above the minimum word count threshold on its
            own, without needing any single overly long sentence to do it.
        """),
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text(
        textwrap.dedent("""\
            # Guide

            A short companion page that the index links to. It exists so the
            index page has a real internal outgoing link. This keeps the
            topology check from flagging a dead end for this regression test.
        """),
        encoding="utf-8",
    )

    payload = asyncio.run(_call_check_document(tmp_path, "docs/index.md"))
    assert "No findings." in payload
