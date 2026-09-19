<!-- SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- markdownlint-disable MD041 -->

## Description
<!-- Describe the architectural intent of the changes and provide context. -->
Fixes #

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature breaking backward compatibility)
- [ ] Documentation update
- [ ] Refactoring / Tech Debt removal
- [ ] CI/CD workflow improvement

## Governance & Compliance Checklist

- [ ] **DCO & Signatures:** All commits are signed with DCO (`git commit -s`) and GPG/SSH (`git commit -S`).
- [ ] **Issue-First:** This PR addresses an explicitly approved Issue.
- [ ] **Changelog:** I have updated `CHANGELOG.md` under the `## [Unreleased]` section.
- [ ] **Commit Standards:** Commit messages strictly follow the Conventional Commits specification.
- [ ] **Absolute Ownership:** I have verified and can architecturally justify every single line of code. No unreviewed AI-generated code is included.

## Quality Gates

- [ ] **Local Pipeline:** `just verify` (lint + test-cov) passes without errors.
- [ ] **Coverage:** New code paths carry tests; the coverage gate is not lowered to accommodate them.
- [ ] **Engine Pinning:** The `zenzic` constraint and `[tool.uv.sources]` are unchanged, or the change is justified in the description.
- [ ] **Protocol Surface:** Any change to a tool's name, arguments or return shape is called out explicitly — MCP clients bind to those.
