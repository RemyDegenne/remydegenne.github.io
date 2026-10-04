#!/usr/bin/env bash
# Verify the headline results of formalization.yaml with leanprover/comparator.
#
# For each config in comparator/*.json this builds the (trusted, self-contained) challenge module
# and the solution module (the project itself), exports both with lean4export, and checks that the
# solution proves *exactly* the challenged statements, using no axioms beyond propext,
# Classical.choice and Quot.sound, with the proofs replayed through the Lean kernel.
# See comparator/README.md for what this does and does not establish.
#
# Usage:
#   scripts/comparator-verify.sh [--insecure] [CONFIG_NAME ...]
#
#   CONFIG_NAME   basename without .json (e.g. aRTS_LLN); default: every comparator/*.json.
#   --insecure    use comparator's fake-landrun shim instead of a real landrun sandbox. The
#                 verdicts are then only meaningful if you already trust this repository's build
#                 not to attack your system — fine for CI freshness checks of your own repo,
#                 NOT fine for judging someone else's.
#
# Requirements: the project toolchain (elan), git, and — unless --insecure — landrun
# (https://github.com/Zouuup/landrun, built from the main branch) in PATH. comparator and
# lean4export are cloned and built automatically into $COMPARATOR_TOOLS_DIR
# (default: ~/.cache/colt-2026-83/comparator-tools).
#
# For the strongest guarantee comparator's README additionally recommends wrapping the whole run
# in systemd-run; see comparator/README.md.

set -euo pipefail

# The comparator revision this repository's setup was last verified against.
COMPARATOR_REPO=https://github.com/leanprover/comparator
COMPARATOR_REV=e45f3b841ab6cb0e6d6a12e300bbfd84b265561c

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="${COMPARATOR_TOOLS_DIR:-$HOME/.cache/colt-2026-83/comparator-tools}"

insecure=0
configs=()
for arg in "$@"; do
  case "$arg" in
    --insecure) insecure=1 ;;
    -h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) configs+=("$arg") ;;
  esac
done
if [ "${#configs[@]}" -eq 0 ]; then
  for f in "$REPO_ROOT"/comparator/*.json; do
    configs+=("$(basename "$f" .json)")
  done
fi

# ── comparator + lean4export ────────────────────────────────────────────────────────────────────
mkdir -p "$TOOLS_DIR"
if [ ! -d "$TOOLS_DIR/comparator" ]; then
  git clone "$COMPARATOR_REPO" "$TOOLS_DIR/comparator"
fi
git -C "$TOOLS_DIR/comparator" fetch --quiet origin "$COMPARATOR_REV" 2>/dev/null || true
git -C "$TOOLS_DIR/comparator" checkout --quiet "$COMPARATOR_REV"

# comparator's kernel and lean4export must match the project's toolchain, so build them with it.
project_toolchain="$(cat "$REPO_ROOT/lean-toolchain")"
if [ "$(cat "$TOOLS_DIR/comparator/lean-toolchain")" != "$project_toolchain" ]; then
  echo "note: building comparator with the project toolchain $project_toolchain" >&2
  echo "$project_toolchain" > "$TOOLS_DIR/comparator/lean-toolchain"
fi
(cd "$TOOLS_DIR/comparator" && lake build lean4export comparator)

COMPARATOR_BIN="$TOOLS_DIR/comparator/.lake/build/bin/comparator"
export COMPARATOR_LEAN4EXPORT="$TOOLS_DIR/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export"

# ── landrun ─────────────────────────────────────────────────────────────────────────────────────
if [ "$insecure" -eq 1 ]; then
  export COMPARATOR_LANDRUN="$TOOLS_DIR/comparator/scripts/fake-landrun.sh"
  echo "WARNING: --insecure: no sandboxing; the verdicts assume this repository is not malicious." >&2
elif ! command -v landrun > /dev/null; then
  echo "error: landrun not found in PATH. Install it from https://github.com/Zouuup/landrun" >&2
  echo "(main branch), or pass --insecure if you already trust this repository's build." >&2
  exit 1
fi

# ── run every config ────────────────────────────────────────────────────────────────────────────
cd "$REPO_ROOT"
failed=()
for name in "${configs[@]}"; do
  config="comparator/$name.json"
  if [ ! -f "$config" ]; then
    echo "error: no such config: $config" >&2
    exit 1
  fi
  echo "── comparator: $config"
  if lake env "$COMPARATOR_BIN" "$config"; then
    echo "── PASS: $name"
  else
    echo "── FAIL: $name"
    failed+=("$name")
  fi
done

echo
if [ "${#failed[@]}" -eq 0 ]; then
  echo "All ${#configs[@]} comparator configs verified."
else
  echo "FAILED: ${failed[*]}"
  exit 1
fi
