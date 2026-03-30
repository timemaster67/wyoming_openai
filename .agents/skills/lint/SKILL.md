---
name: lint
description: Run all linters (ruff, pyright) and fix issues in a loop until the codebase is clean.
disable-model-invocation: true
---

## Current State
- Branch: !`git branch --show-current`
- Dirty files: !`git diff --name-only`

Run **all** project linters and resolve every issue. Loop until the codebase passes cleanly.

### Linter pipeline

Run the linters in this order each iteration:

1. **Ruff auto-fix** — `ruff check . --fix` (safe, auto-fixable issues)
2. **Ruff check** — `ruff check .` (remaining issues that need manual fixes)
3. **Pyright** — `pyright` (type-checking)

### Resolution loop

```
while linters report errors:
    1. Run ruff check . --fix  (let ruff auto-fix what it can)
    2. Run ruff check .
       - If errors remain, read the offending files and fix them
    3. Run pyright
       - If errors remain, read the offending files and fix them
    4. If no errors in steps 2 and 3, break
```

### Rules

- **Max 5 iterations.** If issues persist after 5 loops, stop and report the remaining errors to the user.
- **Ruff first, pyright second.** Ruff fixes (especially import sorting) can eliminate pyright false positives, so always run ruff before pyright.
- **Use `ruff check . --fix` before manual fixes.** Never manually fix what ruff can auto-fix.
- **Minimal changes.** Only touch lines the linters flag. Do not refactor, add docstrings, or "improve" surrounding code.
- **Preserve behavior.** Fixes must not change runtime behavior. If a fix requires a judgment call (e.g., an `Any` type that needs a real annotation), prefer the narrowest correct type.
- **Report clearly.** After each iteration, briefly state which linter you ran and how many errors remain. When done, summarize what was fixed.
- If `$ARGUMENTS` contains a file path or glob, pass it to both linters to scope the run (e.g., `ruff check $ARGUMENTS` and `pyright $ARGUMENTS`).
