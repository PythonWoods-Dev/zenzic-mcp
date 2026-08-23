# Zenzic-MCP Priority Table

> This roadmap is independent of `zenzic` Core's own priority table
> (`../zenzic/.claude/state/03-priority-table.md`). `zenzic-mcp` does not occupy a Core version
> slot (e.g. it is not "v0.32.0") — it has its own `v0.1.0 → v0.2.0 → ...` sequence, with a
> stated minimum Core version as a dependency constraint, not a shared milestone number.

| Stato | Priorità | Feature | Note |
| :--- | :--- | :--- | :--- |
| `[ ]` | P0 | Repository scaffold & `.claude/` bootstrap | This document |
| `[ ]` | P0 | MCP server skeleton (stdio transport, tool registration) | |
| `[ ]` | P0 | `check_document(path)` tool — thin wrapper over Core's `check` | Granular, not a full-repo dump |
| `[ ]` | P0 | Secret redaction test on the MCP serialization path | Invariant 2 |
| `[ ]` | P1 | `vsm://topology` resource with mandatory filter/limit params | Invariant 1 |
| `[ ]` | P1 | State invalidation for externally-modified files | Invariant 3 |
| `[ ]` | P1 | `fix_document(path)` tool (Atomic Mutator wrapper) | Mutation — confirm before executing, not silent |
| `[ ]` | P2 | `explain_finding(code)` prompt template | |
| `[ ]` | P2 | First Zensical-authored docs page (dogfooding proof) | |
| `[ ]` | P3 | Publish to MCP community registry | After a stable internal release cycle |
