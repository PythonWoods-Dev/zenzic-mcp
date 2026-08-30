# SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
# SPDX-License-Identifier: Apache-2.0
"""check_document's tool handler must not let an unexpected exception escape
the MCP wire boundary unhandled.

Only DocumentNotFoundError was ever caught around the check_document() call
in server.py -- any other exception (an adapter crash, a config error, a
rule-engine bug) propagated fully unhandled out of the tool handler. This is
a real, live-reproducible gap, not hypothetical: a project declaring
`engine = "zensical"` in .zenzic.toml with neither zensical.toml nor
mkdocs.yml present raises a real zenzic.core.exceptions.ZenzicConfigError
from check_document() -- confirmed directly before writing this test, not
assumed.
"""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.server import NotificationOptions
from mcp.shared.memory import create_client_server_memory_streams

from zenzic_mcp.server import server


async def _call_check_document(repo_root: Path, rel_path: str) -> tuple[str, bool]:
    """Drive the real MCP wire protocol; return (payload, connection_survived)."""
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
                return result.model_dump_json(), not server_task.done()
        finally:
            server_task.cancel()


def test_adapter_config_error_returns_clean_error_result(tmp_path: Path) -> None:
    """A real ZenzicConfigError (not DocumentNotFoundError) from check_document
    must surface as a clean CallToolResult(is_error=True), not an unhandled
    exception that kills the server task or the client connection."""
    (tmp_path / ".zenzic.toml").write_text(
        textwrap.dedent("""\
            [build_context]
            engine = "zensical"
        """),
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n", encoding="utf-8")

    payload, server_survived = asyncio.run(_call_check_document(tmp_path, "docs/index.md"))

    assert server_survived, "server task died handling an unexpected exception"
    assert '"isError":true' in payload or '"is_error":true' in payload, (
        f"Expected a clean is_error result, got:\n{payload}"
    )
