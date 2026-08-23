# Zenzic-MCP State Manifest

> Single source of truth for this repository's version, dependency baseline, and governance
> cross-reference. Distinct from `../zenzic/.claude/state/01-manifest.md`, which governs the
> Core repository only.

## 1. Version & Baseline

| Field | Value |
| :--- | :--- |
| **Repository** | `zenzic-mcp` |
| **Current Version** | `v0.1.0` (pre-release / initial scaffold) |
| **Versioning Model** | Independent of Zenzic Core. Never mirrors Core's version number. |
| **Core Dependency Constraint** | `zenzic~=0.31` (compatible-release; update deliberately, not automatically, when Core's minor version changes) |
| **Documentation Engine** | Zensical (dogfooding the Zensical adapter from day one) |

## 2. Governance Cross-Reference

- `.claude/` in this repository is `.gitignore`-excluded (Zero-Leak Governance, same rationale
  as `zenzic` Core).
- Canonical naming conventions and Tier-0 invariants live in `../zenzic/.claude/references/`
  and are referenced, not duplicated, from this repository's `CLAUDE.md`.
- This cross-repo reference assumes a single-developer workstation with both repositories
  checked out as sibling directories under the same parent folder. It is not portable to a
  second contributor or a CI runner without a separate mechanism (e.g. a versioned, public
  subset of the Core's references committed to this repo, or a documented manual sync step).

## 3. Status

- [ ] Repository created
- [ ] `pyproject.toml` scaffolded with `zenzic~=0.31` dependency
- [ ] MCP server skeleton (Resources / Tools / Prompts) implemented
- [ ] Secret redaction test (Invariant 2) in place
- [ ] Cache invalidation strategy (Invariant 3) designed and tested
- [ ] First Zensical-authored documentation page published
