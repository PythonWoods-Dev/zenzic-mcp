# SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
# SPDX-License-Identifier: Apache-2.0
"""Minimal MCP server exposing the Zenzic Core engine over stdio.

Built on the official `mcp` SDK's low-level ``Server``/request-handler API
(not FastMCP), so every Tool's schema and response payload is constructed
explicitly — required for auditing MCP-specific Invariant 1 (bounded
payloads) and Invariant 2 (secret redaction) line by line, rather than
relying on decorator-generated behavior.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.runner import ServerRequestContext
from mcp.server.stdio import stdio_server

from zenzic_mcp.analysis import DocumentNotFoundError, check_document

server: Server = Server("zenzic-mcp")


_CHECK_DOCUMENT_TOOL = types.Tool(
    name="check_document",
    title="Check Document",
    description=(
        "Run a full Zenzic quality/security check on a single Markdown document "
        "and return its findings. Scoped to the requested file only — never "
        "returns the full site topology or baseline (MCP Invariant 1)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "repo_root": {
                "type": "string",
                "description": "Absolute path to the repository root containing .zenzic.toml.",
            },
            "path": {
                "type": "string",
                "description": "Absolute or repo_root-relative path to the Markdown file to check.",
            },
        },
        "required": ["repo_root", "path"],
    },
)


async def _handle_list_tools(
    _ctx: ServerRequestContext, _params: types.PaginatedRequestParams
) -> types.ListToolsResult:
    return types.ListToolsResult(tools=[_CHECK_DOCUMENT_TOOL])


async def _handle_call_tool(
    _ctx: ServerRequestContext, params: types.CallToolRequestParams
) -> types.CallToolResult:
    if params.name != "check_document":
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Unknown tool: {params.name}")],
            is_error=True,
        )

    arguments = params.arguments or {}
    try:
        repo_root = Path(str(arguments["repo_root"])).resolve()
        raw_path = str(arguments["path"])
    except KeyError as exc:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Missing required argument: {exc}")],
            is_error=True,
        )

    target = Path(raw_path)
    if not target.is_absolute():
        target = repo_root / target

    try:
        diagnostics = check_document(repo_root, target)
    except DocumentNotFoundError as exc:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=str(exc))],
            is_error=True,
        )

    if not diagnostics:
        summary = "No findings."
    else:
        lines = [
            f"{d.range.start.line + 1}:{d.range.start.character + 1}  [{d.code}]  {d.message}"
            for d in diagnostics
        ]
        summary = "\n".join(lines)

    return types.CallToolResult(content=[types.TextContent(type="text", text=summary)])


server.add_request_handler("tools/list", types.PaginatedRequestParams, _handle_list_tools)
server.add_request_handler("tools/call", types.CallToolRequestParams, _handle_call_tool)


async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(notification_options=NotificationOptions()),
        )


def main() -> None:
    """Entry point for the ``zenzic-mcp`` console script."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
