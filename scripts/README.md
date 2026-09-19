<!--
SPDX-FileCopyrightText: 2026 PythonWoods <dev@pythonwoods.dev>
SPDX-License-Identifier: Apache-2.0
-->

# `scripts/` — CI tooling

| Script | Invocation | What it does | What verifies its output |
| :--- | :--- | :--- | :--- |
| `ci_secret_scan.py` | **Automatic** — `.github/workflows/secret-scan.yml`, on every push to `main` and every pull request against it | Runs `zenzic guard scan` over every git-tracked file (`git ls-files`) and fails closed on any finding outside the (currently empty) fixture allowlist. | Its own `_self_test()` runs before any verdict, so a broken instrument cannot report clean, and it prints the file count — "passed" and "looked at nothing" must not be the same string. |

This table has a column most such tables omit: **what verifies the output**. A
script that runs is not the same as a script whose result is checked, and the
distinction is what separates a gate from a habit.
