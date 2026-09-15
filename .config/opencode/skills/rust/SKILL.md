---
name: Rust
description: Rust conventions and verification commands (crates, cargo, errors, unsafe, async). Load when working in a SCOPE with .rs / Cargo.toml.
---

## Commands

| What | Command |
| --- | --- |
| Single test | `cargo test -p <crate> <filter>` |
| Crate tests | `cargo test -p <crate>` |
| Lint | `cargo clippy -p <crate> --all-targets -- -D warnings` |
| Format | `cargo fmt --check` (`cargo fmt` only when explicitly requested) |
| Build | `cargo build -p <crate>` |

Scoped, not the whole workspace: a full run only when the acceptance criterion demands it. Before
running, establish the layout: root `Cargo.toml`, `crates/*`, `tools/*`, `[workspace]`.

## Conventions

- Errors: `Result<T, E>` with a typed error (usually `thiserror`) in libraries;
  `anyhow`/strings only in the binary/CLI layer. `unwrap()`/`expect()` are acceptable in tests, in
  `main`, and where the invariant is proven higher in the stack — anywhere else it is a defect.
- `panic!` only for "impossible" states, with a comment stating why it is impossible.
- `unsafe` — the smallest possible block, with a mandatory `// SAFETY:` comment saying what the
  caller guarantees. Do not introduce new `unsafe` without necessity: request approval first.
- `async`: never block the executor — offload blocking/heavy work via `spawn_blocking`; never hold
  a `MutexGuard`/`RwLockReadGuard` across an `await`; do not busy-poll where a channel/event exists.
- Dependencies: never add a crate silently — surface it in `RISK:` and propose it, the orchestrator
  decides. Never hand-edit `Cargo.lock`.
- Public API of a crate stays minimal: `pub` only what is genuinely used outside.
- Config and constants: no magic numbers in function bodies; read config/env values once at the
  boundary instead of deep inside the logic.
- Tests: unit tests in `#[cfg(test)] mod tests` alongside the code, integration tests in `tests/`.
  A new test names the behaviour, not the function (`fn rejects_empty_bbox`), one scenario per test.

## Forbidden zones

`target/**` (blocked at the permission layer), `**/generated/**`, generated
protobuf/bindings output — edit only on explicit request and together with the generator.

## Rust diff checklist (for review)

1. `unwrap`/`expect`/`panic` on the data-handling path.
2. Errors swallowed via `let _ =` or `.ok()` without checking.
3. `unsafe` without `// SAFETY:`, or a guarantee that does not hold on every entry path.
4. A blocking call inside `async`, or a guard held across `await`.
5. A changed public signature without updating callers in the same crate.
6. A new dependency without necessity; a hand-edited `Cargo.lock`.
7. Cloning large structs in a hot loop; rebuilding a `Vec` every iteration.
