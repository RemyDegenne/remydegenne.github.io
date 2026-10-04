/-
Copyright (c) 2026 Rémy Degenne. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Rémy Degenne
-/

/-! # Comparator library root

Stub root module of the `Comparator` lake library. The library's actual content — the
`Challenge_*` statements and the `Solution` module — is listed through `globs` in `lakefile.toml`,
deliberately NOT imported here: tools that import every library root of the workspace
(`checkdecls`) must not load the challenges, which redeclare project and LML names.
See `comparator/README.md`. -/
