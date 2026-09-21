<!--
SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
SPDX-License-Identifier: Apache-2.0
-->

# Security Policy

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

If you discover a security vulnerability in `zenzic-mcp` — including anything that lets a
caller read outside the repository it was pointed at, or that returns credential material
to the client — report it privately via one of these channels:

- **GitHub Security Advisories** (preferred): [github.com/PythonWoods-Dev/zenzic-mcp/security/advisories](https://github.com/PythonWoods-Dev/zenzic-mcp/security/advisories)
- **Email**: `dev@pythonwoods.dev` — subject line: `[SECURITY] zenzic-mcp — <brief description>`

Please include a clear description, steps to reproduce, potential impact, and a suggested
fix if you have one. Never include a real credential in a report — describe its shape
instead, or use an obviously synthetic value.

We will acknowledge your report within **72 hours** and aim to release a fix within
**14 days** of confirming the issue.

## Scope

`zenzic-mcp` is a Model Context Protocol server that speaks **stdio** and exposes a single
tool, `check_document`, which takes two caller-supplied paths (`repo_root` and `path`) and
returns the Zenzic engine's findings for one file. Its trust boundary is therefore the
MCP client, and the following areas are in scope for a security report:

| Area | Description |
| :--- | :---------- |
| **Path escape via tool arguments** | A `repo_root`/`path` pair that causes a read outside the repository the caller named |
| **Credential echo** | A response that returns matched secret *material* rather than the fact and location of a finding — the engine detects credentials, and this server must not carry them back to the client |
| **Scope escape** | A response that returns full site topology or baseline data for a single-file request, contrary to the tool's stated contract |
| **Denial of service** | A crafted document or configuration that causes unbounded time or memory in the analysis path |
| **Dependency CVE** | A known CVE in a runtime dependency, including the `zenzic` engine itself |
| **Code execution** | A crafted Markdown or configuration file that causes arbitrary code execution during a check |

Out of scope: documentation content errors, false positives or negatives in a finding's
*severity*, and anything that affects only local development sessions rather than the
published package.

## Security design notes

This server **imports the `zenzic` engine as a library** rather than invoking its binary,
so it inherits the engine's own posture: no subprocess calls in the analysis path, and all
parsing done in pure Python over plain data. Configuration files (`.zenzic.toml`) are read
as TOML; no code in them is evaluated.

Two consequences are worth stating explicitly because they are properties of this server
rather than of the engine:

- **The caller chooses the paths.** Both `repo_root` and `path` come from the MCP client.
  Any containment guarantee is therefore a property of this server's argument handling,
  not something the engine can provide on its behalf.
- **The transport is stdio, not a network socket.** There is no listening port and no
  authentication layer; the security boundary is whatever the host granted the MCP client.
  A vulnerability report should say which client and which transport it assumed.

## Supported versions

`zenzic-mcp` is **pre-release** and has had no tagged release. There is no supported
version to backport to: security fixes land on the default branch, and the first tagged
release will carry them. This table will be replaced with a real support matrix at that
point.

| Version | Support status |
| :------ | :------------- |
| unreleased (default branch) | ✅ Security fixes land here |

## Disclosure policy

We follow a **coordinated disclosure** model. Please allow up to 14 days for a fix before
any public disclosure. Confirmed reporters will be credited in `CHANGELOG.md` unless they
prefer to remain anonymous.
