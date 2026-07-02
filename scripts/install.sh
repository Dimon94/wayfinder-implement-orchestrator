#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="wayfinder-implement-orchestrator"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
SKIP_DEPS=0

usage() {
  cat <<EOF
Usage: ./scripts/install.sh [--skip-deps-check]

Installs $SKILL_NAME to:
  \${CODEX_HOME:-~/.codex}/skills/$SKILL_NAME
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-deps-check) SKIP_DEPS=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
  shift
done

SOURCE="$ROOT/skills/$SKILL_NAME"
DEST="$CODEX_HOME_DIR/skills/$SKILL_NAME"

[ -f "$SOURCE/SKILL.md" ] || {
  echo "Cannot find bundled skill at $SOURCE" >&2
  exit 1
}

if command -v python3 >/dev/null 2>&1; then
  python3 "$ROOT/scripts/validate.py"
fi

if [ "$SKIP_DEPS" -eq 0 ]; then
  missing=()
  for dep in ask-matt wayfinder to-prd to-issues implement code-review writing-great-skills; do
    [ -f "$CODEX_HOME_DIR/skills/$dep/SKILL.md" ] || missing+=("$dep")
  done

  if [ "${#missing[@]}" -gt 0 ]; then
    echo "Missing Matt Pocock skill dependencies in $CODEX_HOME_DIR/skills:" >&2
    printf '  - %s\n' "${missing[@]}" >&2
    echo "Install mattpocock-skills first, or rerun with --skip-deps-check." >&2
    exit 1
  fi
fi

rm -rf "$DEST"
mkdir -p "$(dirname "$DEST")"
cp -R "$SOURCE" "$DEST"

echo "Installed $SKILL_NAME to $DEST"
