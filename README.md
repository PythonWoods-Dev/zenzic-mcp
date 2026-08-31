<!-- SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

<p align="center">
  <a href="https://github.com/PythonWoods-Dev/zenzic-mcp">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="./assets/zenzic-wordmark-mcp-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="./assets/zenzic-wordmark-mcp.svg">
      <img alt="Zenzic / mcp" src="./assets/zenzic-wordmark-mcp-dark.svg" width="350">
    </picture>
  </a>
</p>

<h1 align="center">Zenzic: Documentation Integrity for MCP Clients</h1>

<p align="center">
  <strong>Formatters handle syntax. Prose linters handle grammar. Zenzic protects the graph—and optionally enforces lightweight editorial policy without a separate tool.</strong><br>
  <em>A Model Context Protocol server exposing the Zenzic engine to LLM agents over stdio.</em>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/license-Apache--2.0-0d9488?style=flat-square" alt="License">
  </a>
  <img src="https://img.shields.io/badge/status-pre--release-f59e0b?style=flat-square" alt="Status: pre-release">
  <img src="https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square" alt="Python 3.10+">
</p>

---

## ⚠️ Status: Pre-Release

**This project is in development and has had no release.** The version is `0.1.0`, no tag has
been published, and the tool surface below is deliberately small — one Tool. Treat the
interface as unstable: names, arguments, and response shapes may change without a deprecation
period until a `1.0.0` exists.

Everything documented on this page is implemented and callable today. Nothing here describes
planned work.

---

## What This Is

[Zenzic](https://github.com/PythonWoods/zenzic) analyses Markdown documentation as a graph:
it resolves every link, anchor, and asset reference across a whole docs tree without building
the site, and scans source for leaked credentials. `zenzic-mcp` puts that engine behind a
[Model Context Protocol](https://modelcontextprotocol.io/) server so an LLM agent can ask it
about a document directly, instead of shelling out to a CLI and parsing terminal output.

It imports `zenzic` as a library dependency rather than invoking its binary, so an agent gets
the analyser's own structured diagnostics.

---

## Tools

### `check_document`

Runs a full Zenzic quality and security check on **one** Markdown document and returns its
findings.

| Argument | Type | Required | Meaning |
| :--- | :--- | :---: | :--- |
| `repo_root` | string | yes | Absolute path to the repository root containing `.zenzic.toml`. |
| `path` | string | yes | The Markdown file to check — absolute, or relative to `repo_root`. |

Returns one line per finding, `line:column  [CODE]  message`, or `No findings.` when the
document is clean. Unknown tools, missing arguments, a path that is not a tracked Markdown
file, and unexpected engine failures all return a normal error result rather than propagating
past the protocol boundary.

Two behaviours are worth knowing because they are deliberate:

- **Whole-repository analysis, single-document response.** The server performs a full workspace
  sync before answering, because cross-file findings — dangling references, orphan pages,
  topology — cannot be computed from one file in isolation. It then returns diagnostics for the
  requested file only, never the full per-URI map of the site.
- **No cached state between calls.** Zenzic Core keeps a process-lifetime adapter cache; this
  server clears it on every call. A long-running server would otherwise keep answering from an
  adapter built against a `mkdocs.yml` or `.zenzic.toml` that has since changed.

That is the entire tool surface. There are no resources or prompts.

---

## Install & Run

Requires Python 3.10+.

```bash
uv tool install zenzic-mcp     # not yet published to PyPI — see Status above
```

Until a release exists, install from a checkout:

```bash
git clone https://github.com/PythonWoods-Dev/zenzic-mcp
cd zenzic-mcp
uv sync
```

The server speaks MCP over stdio and is started by your client, not by hand. Register it with
any MCP-capable client — the command is `zenzic-mcp` (console script), or
`uv run zenzic-mcp` from a checkout:

```json
{
  "mcpServers": {
    "zenzic": {
      "command": "zenzic-mcp"
    }
  }
}
```

Consult your client's own documentation for where that configuration lives.

---

## Relationship to Zenzic

Zenzic separates one analysis engine from the surfaces that apply it. The engine and the
documentation defining its rules live together in [`zenzic`](https://github.com/PythonWoods/zenzic);
enforcement reaches you through whichever surface fits the moment:

| Surface | Where it applies the rules |
| :--- | :--- |
| [`zenzic`](https://github.com/PythonWoods/zenzic) | The CLI, and the engine every surface below shares. |
| [`zenzic-action`](https://github.com/PythonWoods/zenzic-action) | In CI, as a merge gate on the pull request. |
| [`zenzic-vscode`](https://github.com/PythonWoods/zenzic-vscode) | In the editor, at the keystroke. |
| **`zenzic-mcp`** | To LLM agents, over the Model Context Protocol. |

Each is a thin client over the same engine, so a finding means the same thing wherever you
meet it. `zenzic-mcp` is versioned independently of Core; it declares `zenzic~=0.31` as a
dependency.

---

## License

Apache-2.0 — see [LICENSE](./LICENSE).
