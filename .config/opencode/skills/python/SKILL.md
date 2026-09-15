---
name: Python
description: Python conventions and verification commands (pytest, ruff, mypy, CLI scripts, typing). Load when working in a SCOPE with .py / pyproject.toml.
---

## Commands

| What | Command |
| --- | --- |
| Single test | `pytest -q <path>/test_x.py::test_name` |
| Module tests | `pytest -q <path> -k <expr>` |
| Lint | `ruff check <path>` |
| Format | `ruff format --check <path>` |
| Types | `mypy <path>` (when configured in `pyproject.toml`/`setup.cfg`) |

Establish first how the project manages dependencies: `pyproject.toml`, `requirements*.txt`, `uv`,
`poetry`, an existing `.venv`. Do not create environments on your own — check for `.venv/bin/`; if
tests do not start, return `BLOCKED` with the reason instead of building an environment blind.

## Conventions

- Type annotations are mandatory for new and changed public functions; `Any` only with a comment
  explaining why.
- Errors: specific exceptions. Bare `except Exception:`/`except:` without discrimination is a
  defect. No `pass` in `except` without a stated reason in a comment.
- Output: `logging` through the logger already used in the project. `print` only in the CLI layer
  and only where it is the program's output contract.
- CLI scripts: `argparse` (or whatever `scripts/` already uses), `if __name__ == "__main__":`,
  non-zero exit code on failure, no file access during argument parsing.
- Paths: `pathlib`, never manual string concatenation; normalize and check existence of external
  paths before starting long work.
- Config and secrets: from environment/config, never hardcoded; a new parameter lands together with
  the code that reads it and its documentation in README/the config file.
- Dependencies: never add a package silently — surface it in `RISK:` and propose it.
- Tests: next to the code in `tests/` or `test_*.py`, no network and no real timers; time and
  external calls go through the injection/mock pattern already used in the project.

## Forbidden zones

`__pycache__/**`, `.venv*/**`, `*.egg-info/**`, `dist/**`, `build/**` (blocked at the permission
layer). Generated client stubs — only together with their generator.

## Python diff checklist (for review)

1. `except Exception`/`except:` without discrimination, `pass` in a handler.
2. A changed signature with callers and test mocks not updated.
3. `print` instead of logging, secrets written to the log.
4. Mutable default argument (`def f(x=[])`), module-level shared cache without invalidation.
5. Files/sessions opened without a context manager.
6. Config read deep inside the logic (unportable, untestable).
7. A test that passes only with network, an external file or a specific wall-clock time.
8. A new import whose package is missing from the dependencies.
