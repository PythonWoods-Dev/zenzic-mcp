# MCP-Specific Invariants (`zenzic-mcp`)

> These are additive to, never a replacement for, the canonical Tier-0 invariants in
> `../zenzic/.claude/references/01-tier-0-invariants.md`. Read that file first.

## 1. No Unbounded Resource/Tool Payloads

No MCP Resource or Tool response may return an unfiltered dump of the VSM, the full baseline,
or the full finding list for a large repository. Every graph- or list-shaped response must
support at least one of: `limit`, a path/glob filter, or a specific query key (e.g. "does link
X exist" rather than "list all links").

Rationale: an LLM client's context window is a shared, expensive resource. A single unbounded
tool call on a 5,000-file project must not be able to exhaust it.

## 2. Secret Redaction Before Transmission

Any Tool or Resource whose underlying Core call can surface a `Z2xx` finding (credential
leak, forbidden scheme, path traversal) MUST route through the Core's existing secret-masking
path before serialization. This is not optional and not assumed — it must be covered by a
dedicated test that asserts a known secret pattern never appears unmasked in a Tool/Resource
response, run against the actual MCP serialization path, not just the CLI output path.

## 3. State Invalidation for the Long-Running Server

Because the MCP server holds the `IncrementalAnalysisEngine` / VSM in memory across an agent
session (to avoid the cold-start cost of rebuilding it per call), it must define and test an
explicit invalidation strategy for:
- files changed by a process other than the MCP server's own Tool calls (external edits,
  `git pull`, another editor),
- files added or removed since the server started.

A cache that silently serves stale topology is worse than no cache — it directly undermines
the "AI writes, Zenzic verifies" trust model this project is built on.

## 4. Independent Versioning

`zenzic-mcp`'s own version number is unrelated to the Zenzic Core's version number. Core
compatibility is declared as a dependency constraint (e.g. `zenzic~=0.31` in `pyproject.toml`),
never as a version-number mirror. See `.claude/state/01-manifest.md` for the current baseline.

## 5. Radical Unawareness, Preserved at the Boundary

The Zenzic Core package must never import or reference MCP/LLM-specific types or concepts.
All MCP framing (Resources, Tools, Prompts, JSON-RPC transport) lives exclusively in
`zenzic-mcp`, which depends on Core as an ordinary library consumer — the dependency direction
is one-way.
