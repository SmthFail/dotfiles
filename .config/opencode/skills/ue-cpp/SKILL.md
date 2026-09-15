---
name: Unreal C++
description: Unreal Engine C++ conventions and verification commands (modules, UCLASS/UPROPERTY, GC, logs, UBT). Load when working in a SCOPE with .h/.cpp under an Unreal project.
---

## Commands

| What | Command |
| --- | --- |
| Editor build | build via `UnrealBuildTool`/`Makefile` at the project root (take it from the map) — heavy, goes to the user for approval |
| Fast syntax check | compile the single module with the same `Makefile`/UBT using `-Target=...` |
| Runtime logs | read `Saved/Logs/**` (reading allowed, writing blocked) |
| Config | `Config/*.ini`, `DefaultEngine.ini`, `DefaultGame.ini` |

UE builds are long and resource-hungry: run one only when the acceptance criterion requires it, and
say so in `CHECK:`. If the whole project is being built to validate one line, that is a defect in
the task statement — report it instead of silently waiting.

## Structure and build

- Code lives in `Source/<Module>/`, public headers in `Public/`, internal ones in `Private/`. A new
  `#include` from another module is valid only if that module is already declared in
  `<Module>.Build.cs` dependencies; otherwise it is a dependency addition and must be declared in
  `RISK:`.
- `*.Build.cs`, `*.uproject`, `Plugins/*/*.uplugin` are build/descriptor files: change them only on
  real necessity and always list them in `CHANGED:` as a separate line with the reason.
- The version reference is `*.uproject` (`EngineAssociation`); check the API of that version rather
  than remembering another one.

## Conventions

- Type prefixes: `U` (from `UObject`), `A` (from `AActor`), `F` (plain structs), `E` (enums),
  boolean fields prefixed with `b`.
- Everything the editor/GC/Blueprint must see: `UCLASS`/`USTRUCT`/`UENUM` + `GENERATED_BODY()`,
  serialized fields get `UPROPERTY()`, Blueprint-exposed functions get `UFUNCTION()`. A field that
  must survive GC or re-save without `UPROPERTY()` is a guaranteed data loss.
- UObject pointers use `TObjectPtr<>` (or the project's `UPTR(...)` macro if adopted), never raw
  `Foo*`. Never `new`/`delete` a UObject — only `NewObject<>`/`CreateDefaultSubobject<>`.
- Logging: `UE_LOG` with a category already used in the module. No `printf`/`std::cout`.
- Invariants: `check()` where a failure is a program bug, `ensure()` where it must be survived and
  continued.
- `Tick` is the last place for work. Heavy operations (IO, allocations, traversals, texture loads)
  move out of `Tick` into events, timers or async loading.
- Streaming/textures/materials: any change to memory budget, pools, caches or LOD must be verifiable
  from logs — name in `CHECK:` which counter is expected to move.
- Profile-critical changes land as a pair "change + how to measure it" without touching adjacent
  logic, otherwise the effect cannot be attributed.

## Forbidden zones

`Binaries/**`, `Intermediate/**`, `Saved/**`, `DerivedDataCache/**`, `Build/**` (blocked at the
permission layer; `Saved/Logs/**` is readable). `.uasset`/`.umap` are not edited as text.
`Content/**` only on explicit request.

## UE C++ diff checklist (for review)

1. A new field without `UPROPERTY()` that is persisted or GC-reachable.
2. Raw `UObject*` instead of `TObjectPtr`, `new`/`delete` on UObjects, raw `delete` on arrays.
3. `StaticLoadObject`/`LoadObject` in a hot path or in `Tick` — guaranteed hitches.
4. Heavy work in `Tick`, synchronous loading inside a frame, traversal of the whole scene in a loop.
5. `check` where `ensure` belongs, i.e. on externally supplied data (config, network, file).
6. An `#include` from another module without declaring the dependency in `Build.cs` — breaks other
   targets.
7. Changes to `Config/*.ini` that affect memory/streaming budget with no way to measure the effect.
8. Edits to `Build.cs`/`uproject`/`uplugin` not declared in `CHANGED:`.
9. Mismatch between `EngineAssociation` version and the API being used.
