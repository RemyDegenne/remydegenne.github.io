# Tools, where to find them, and gotchas

## Tools

- **Lean 4 and elan** (`lean-toolchain` pins the version): https://github.com/leanprover/lean4,
  https://github.com/leanprover/elan.
- **Mathlib**: https://github.com/leanprover-community/mathlib4 — also provides `lake exe mk_all`,
  `lake exe cache get`, `#min_imports` and the style linters; the linter driver `runLinter` is
  Batteries', https://github.com/leanprover-community/batteries.
- **LML** (Lean Machine Learning): https://github.com/LeanMachineLearning/LML — the
  algorithm–environment framework (`Algorithm`, `Environment`, `IsAlgEnvSeq`, `IdentAlg`,
  stopped histories, divergence decompositions) and its `ForMathlib/` lemmas.
- **The referee site**: https://github.com/LeanTrustBuilders/referee-site — the project's
  claims, what their statements rest on, and a private review of each declaration, published
  under `home_page/referee` by the GitHub action `LeanTrustBuilders/referee-site@main` (see its
  README, "In CI"). Part of the LeanTrustBuilders suite (https://github.com/LeanTrustBuilders):
  the action extracts the project's dataset with the newest `trust-extract` release for its
  toolchain (https://github.com/LeanTrustBuilders/extractor), which must exist for the Lean of
  `lean-toolchain`: `gh release list -R LeanTrustBuilders/extractor`. Locally,
  `pip install git+https://github.com/LeanTrustBuilders/referee-site` gives `trust-site build`.
- **challenge-gen**: https://github.com/LeanTrustBuilders/challenge-gen — the comparator
  challenges, run by `scripts/make-challenges.py`. It writes each headline statement with `sorry`
  as a standalone module, everything the statement rests on copied verbatim from its source, and
  beside it comparator's config listing the theorems to check. With `--import Mathlib` the file
  imports Mathlib alone and copies what it needs of the project and of LML, the shape Palomar asks
  for. No binary release: the script clones and builds it into `~/.cache/<Name>/challenge-gen`,
  at the tag `v<toolchain>` of the project's `lean-toolchain`, which must exist
  (`gh release list -R LeanTrustBuilders/challenge-gen`; there is none before 4.35.0-rc3).
- **leanblueprint**: https://github.com/PatrickMassot/leanblueprint — `pip install leanblueprint`;
  needs a TeX distribution with `xelatex` and `latexmk`, and plasTeX for the web build.
- **checkdecls**: https://github.com/PatrickMassot/checkdecls — lake dependency behind
  `lake exe checkdecls blueprint/lean_decls`.
- **comparator**: https://github.com/leanprover/comparator, with
  https://github.com/leanprover/lean4export (both cloned and built automatically by
  `scripts/comparator-verify.sh` into `~/.cache/<Name>/comparator-tools`) and the landrun
  sandbox https://github.com/Zouuup/landrun (required unless `--insecure`).
- **formalization.yaml**: https://github.com/mathlib-initiative/formalization.yaml — schema and
  field documentation; the file's header links the schema for editor validation.
- **Palomar registry**: https://palomar-registry.org/ — the registry whose mechanical verification
  dictates the challenge shape (Mathlib-only imports, everything else inlined).
- **CI actions** (`.github/workflows/`): `leanprover/lean-action` (build),
  `leanprover-community/docgen-action` (blueprint website), `LeanTrustBuilders/referee-site`
  (referee site), `leanprover-community/mathlib-update-action` (dependency bumps).

## Learning Lean and Mathlib

Mathematics in Lean https://leanprover-community.github.io/mathematics_in_lean/, the Mathlib API
docs https://leanprover-community.github.io/mathlib4_docs/, Loogle https://loogle.lean-lang.org
for searching lemmas by shape, and the Zulip chat https://leanprover.zulipchat.com for
questions. In the editor, use VS Code with the Lean 4 extension.

## Gotchas collected on this project

- Under the module system a proof nested in an `instance` becomes module-private and breaks
  comparator; keep instances used by headline definitions free of nested proofs. challenge-gen
  lists in `theorem_names` the lemmas left `sorry` that the definitions use.
- Section instance variables are auto-included: lemmas that do not need them get
  `omit [inst] in`. Section `variable (h : …)` needs `include h`.
- `ℕ∞` and `WithTop ℕ` carry different `MeasurableSpace` instances; `(n : WithTop ℕ)`
  elaborates to `Nat.cast`, `IsStoppingTime` produces `WithTop.some`. They are defeq: bridge
  with `exact`/`change`, never `rw`; pass `(i := n)` to lemmas quantified over the index.
- A failing field in a structure literal (`MeasurableEquiv … where`) silently turns the def
  into `sorry`; later `rfl` failures are the symptom.
- Blueprint LaTeX: brace subscripts of macros under unicode-math (`_{\R}`), wrap math in
  headings with `\texorpdfstring`, no `enumitem` (plasTeX), `\^{}` inside `\texttt`.
- `leanblueprint web` reuses the bibliography of the PDF build: always build the PDF first.
- Comparator compares every constant in the closure of a headline statement structurally, by
  name, and the challenge is a single module while the project is many. Lean abstracts each
  non-trivial nested proof of a definition into `decl._proof_i` and each `match` into
  `decl.match_i`, deduplicating identical ones *per module*, so their names differ between the
  project and the challenge (`optZ.match_1` vs `Learning.MDP.env.match_1`, `maxReturn._proof_1`
  vs `statesKernel._proof_3`) and the comparison fails with "Const does not match". In the
  closure of the headline statements: no `by` proofs or lemma applications with non-atomic
  arguments inside definitions (name the lemma and apply it to variables; instances are
  `⟨lemma⟩`; kernels are `⟨f, measurable_f⟩`, not `Kernel.ofFunOfCountable`), no pattern
  matching (`Nat.rec` with a step function, equations by `rfl`), no `(0 : Fin (n + 1))`
  (a `NeZero` proof; use `⟨0, Nat.zero_lt_succ n⟩`) and no real numeral `≥ 2` (a
  `Nat.AtLeastTwo` proof; write `((3 : ℕ) : ℝ)`). Diagnose with a scratch file that `#print`s
  the constant (`pp.explicit`, `pp.proofs`) in `import <Lib>...` and in
  `import Challenge_<name>` and diff the two. Theorem statements are not abstracted, so they
  may use numerals freely. challenge-gen detects such a case: it writes no config for the
  target and names the auxiliary theorem the challenge would take for the project's, and
  `make-challenges.py` stops. It does the same for a statement reaching a private declaration, or
  a definition the project makes with `irreducible_def`: their names hold their module's, so
  comparator can never match them. (entropy-mdp, 2026-09-16)
