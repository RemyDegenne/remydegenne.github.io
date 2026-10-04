# Comparator setup

Machine-checkable verification, with [leanprover/comparator](https://github.com/leanprover/comparator),
that this repository proves the headline results claimed in [`formalization.yaml`](../formalization.yaml)
without having to read or trust the Lean development in `<Lib>/`.

**Status.** <Which challenges are proved, when `scripts/comparator-verify.sh` last passed and how
(`--insecure` or sandboxed).>

Each challenge is one self-contained file whose transitive imports resolve to Mathlib and Lean
core only, the shape the [Palomar registry](https://palomar-registry.org/) enforces: no LML, no
project modules, no sibling helpers.

## The trust story

For each headline theorem `<Lib>.<name>` there is a challenge file `Challenge_<name>.lean` and a
config `<name>.json`; the list is `targets.txt`:

| paper result | challenge(s) |
|---|---|
| Theorem 1 (<what it says>) | `<name>` |

Each challenge states the theorem with `sorry`, with every definition the statement rests on
copied verbatim from its source by [challenge-gen](https://github.com/LeanTrustBuilders/challenge-gen):
the project's definitions and the LML declarations they build on. A reader checks the *statement*
(the challenge file) by hand and lets comparator check that the project proves exactly it, with
no axioms beyond `propext`, `Classical.choice` and `Quot.sound`, the proofs replayed through the
kernel. The config also lists the lemmas the definitions use, left `sorry` in the challenge and
proved by the project, and the theorems Lean makes of the proofs inside definitions.

## Regenerating and running

`scripts/make-challenges.py` regenerates every challenge and config from `targets.txt`;
`lake build Comparator` checks that they compile; `scripts/comparator-verify.sh [--insecure]`
runs comparator on every config (see the script header for the sandbox requirements).
