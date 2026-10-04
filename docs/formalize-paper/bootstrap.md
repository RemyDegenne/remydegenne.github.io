# Starting from nothing

For a collaborator with an empty directory and no formalization experience. Do the steps in
order; each ends with a check that must pass before moving on. `<Name>` is the project name
(here `colt-2026-83`), `<Lib>` the Lean library name (here `Maiti2026Power`, "author, year,
keyword"), `<Paper>` the directory for the paper's own results (here `MXJ2026`). Files to copy
are in `templates/` next to this file; `tools.md` says where each tool comes from.

1. **Install the tools.** elan (installs Lean and lake), VS Code with the Lean 4 extension,
   git and the GitHub CLI `gh`, Python 3 with `pip install leanblueprint`, a TeX distribution
   with `xelatex` and `latexmk`. Check: `elan --version`, `leanblueprint --help`, `xelatex --version`.
2. **Create the Lean project on the Mathlib template.**
   ```
   lake new <Name> math && cd <Name> && git init
   ```
   This writes `lakefile.toml`, `lean-toolchain`, a root file and a `.gitignore`. Replace
   `lakefile.toml` by `templates/lakefile.toml` with `<Lib>` filled in: it requires LML and
   checkdecls, not Mathlib directly (Mathlib comes through LML, at the revision LML pins, so the
   two never disagree), sets the Batteries linter driver and the strict
   `[leanOptions]`, and declares the `Comparator` library used in step 6. Then
   ```
   lake update                                             # fetch dependencies
   cp .lake/packages/LeanMachineLearning/lean-toolchain .  # use LML's toolchain
   lake exe cache get                                      # Mathlib oleans, avoids hours of compiling
   lake build                                              # check: completes with no errors
   ```
   Append `templates/gitignore-additions` to `.gitignore`. Add a `LICENSE` (Apache-2.0, as
   Mathlib and LML). Every Lean file follows `templates/Example.lean`: copyright header,
   `module`, `public import …`, a module docstring, `@[expose] public section`. Create
   `<Lib>/Mathlib/`, `<Lib>/LeanMachineLearning/` and `<Lib>/<Paper>/`, put a first file in
   each, generate the root with `lake exe mk_all --lib <Lib>`; check `lake build <Lib> --wfail`.
3. **Put the paper in `source/`** (the arXiv or camera-ready TeX sources) and write
   `notes/blueprint-outline.md` before any blueprint or Lean: the results, the lemmas they need,
   what Mathlib/LML already provide, the modelling choices. This is the contract between the
   chapters written next; it also fixes the label names.
4. **Create the blueprint.** From the repository root, `leanblueprint new` asks for the
   project data and writes `blueprint/src/` (`content.tex`, `print.tex`, `web.tex`,
   `plastex.cfg`, `macros/`), a `home_page/` and `.github/workflows/blueprint.yml`. Make
   `content.tex` a list of `\input{chapters/…}`, one chapter file per part of the outline. Copy
   `templates/scripts/check-blueprint.py` to `scripts/`. Replace the generated workflow by
   `templates/workflows/blueprint.yml`, adapted: the library name in the `mk_all --check` step
   and the referee site's `root`. The referee site's action needs a `trust-extract` release for
   the Lean of `lean-toolchain` (see `tools.md`). Check:
   `python3 scripts/check-blueprint.py`, `leanblueprint pdf`, `leanblueprint web`,
   `lake exe checkdecls blueprint/lean_decls` (empty at first), and `leanblueprint serve` to
   look at the site. On GitHub, enable Pages with "GitHub Actions" as the source.
5. **Write `formalization.yaml`** from `templates/formalization.yaml`: fill `project`,
   `sources`, and the `status` section listing every headline result with its intended Lean
   name and blueprint label. Keep the schema comment in the header so the editor validates it.
6. **Set up the comparator side** once the headline statements exist (end of phase 1).
   Copy `templates/comparator/` to `comparator/` (`Comparator.lean` is the stub root and stays
   as is; fill the imports of `Solution.lean` and the table of `README.md`), write
   `comparator/targets.txt` with one headline declaration name per line (the name after the
   `<Lib>.` prefix), and list every `Challenge_<name>` in the `globs` of the `Comparator`
   library in `lakefile.toml`. Copy `templates/scripts/make-challenges.py` and
   `templates/scripts/comparator-verify.sh` to `scripts/` and adapt the library name `LIB` and the
   cache directory `~/.cache/colt-2026-83` in the first, the cache directory in the second. The
   first runs challenge-gen, which it clones and builds for the project's toolchain (see
   `tools.md`). Check: `python3 scripts/make-challenges.py`, `lake build Comparator`, then one
   `scripts/comparator-verify.sh --insecure <config>`. Add `templates/workflows/comparator.yml`
   (manual trigger, nothing to adapt).
7. **First push.** Commit, create the GitHub repository (`gh repo create`), push, and check
   that the blueprint workflow goes green: build, lint, `mk_all --check`, comparator build,
   referee site, blueprint deployment. From here on, follow the workflow in `SKILL.md`.
