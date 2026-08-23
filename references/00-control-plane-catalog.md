# Zenzic-MCP Control Plane Catalog

> Naming conventions and directory semantics are inherited wholesale from
> `../zenzic/.claude/references/00-control-plane-catalog.md` (§1) — the canonical SSoT.
> This file only lists the files specific to `zenzic-mcp` itself; it does not restate
> conventions already defined there.

## Files in this repository's `.claude/`

| Path | Purpose |
| :--- | :--- |
| `.claude/CLAUDE.md` | Team Manager persona for `zenzic-mcp`, cross-referencing Core governance |
| `.claude/references/00-control-plane-catalog.md` | This file |
| `.claude/references/00-mcp-specific-invariants.md` | Additive Tier-0 invariants specific to the MCP server |
| `.claude/state/01-manifest.md` | Version baseline (independent from Core), dependency constraint |
| `.claude/state/02-priority-table.md` | Independent roadmap, not tied to Core version slots |
| `.claude/agents/` | Empty — populate on demand, modeled on `../zenzic/.claude/agents/` |
| `.claude/commands/` | Empty — populate on demand |
| `.claude/directives/` | Execution directive history for this repository, same `vX.Y.Z/` convention as Core |

## Dogfooding Note

Documentation for this project is authored under Zensical rather than MkDocs, deliberately —
this gives the Zensical adapter a live, real-world consumer alongside the existing MkDocs-based
`zenzic` Core documentation.
