<!-- SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# zenzic-mcp

Model Context Protocol server exposing the [Zenzic](https://github.com/PythonWoods-Dev/zenzic)
Deterministic Document Integrity Engine to LLM agents (Claude, Cursor, Cline, and other MCP
clients).

## Status

Early bootstrap. A minimal server skeleton and a single Tool (`check_document`) are implemented;
see `.claude/state/01-manifest.md` and `.claude/state/02-priority-table.md` for current scope
and roadmap.

## Relationship to Zenzic Core

`zenzic-mcp` is a separate, independently-versioned repository that imports `zenzic` as a
library dependency rather than shelling out to its CLI. See `.claude/CLAUDE.md` for the full
governance model.
