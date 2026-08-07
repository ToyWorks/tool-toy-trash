#!/usr/bin/env bash
set -euo pipefail

# Minimal runner (manual use). Keeps prompts short by using file paths.
# Usage:
#   scripts/run_t3_audit.sh "product-slug"
#
# Steps 1-4 are agent work and cannot be shell-scripted; this handles the
# deterministic tail (validate -> merge -> synthesize) and scaffolds the rest.

SLUG="${1:-case}"
DATE="$(date +%F)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="./tmp/reports/t3-${DATE}-${SLUG}"

mkdir -p "$OUT_DIR"

echo "[1] Collect sources with the agent's web tools -> $OUT_DIR/01-level0-extracts.md"
echo "[2] Organize + Brand Blind (per SKILL.md)      -> $OUT_DIR/02-brand-blinded.md"
echo "[3] Run the three auditors in parallel, passing only the file path."
echo "    Write their stdout to $OUT_DIR/03-{tool,toy,trash}-auditor.json"
echo

missing=0
for role in tool toy trash; do
  if [[ ! -f "$OUT_DIR/03-$role-auditor.json" ]]; then
    echo "  waiting on: $OUT_DIR/03-$role-auditor.json"
    missing=1
  fi
done
if (( missing )); then
  echo
  echo "Re-run once the auditor reports exist."
  exit 0
fi

echo "[3.5] Validate + merge"
python3 "$SKILL_DIR/scripts/validate_auditor_json.py" merge \
  --tool  "$OUT_DIR/03-tool-auditor.json" \
  --toy   "$OUT_DIR/03-toy-auditor.json" \
  --trash "$OUT_DIR/03-trash-auditor.json" \
  --output "$OUT_DIR/auditor_reports.json"

echo
echo "[4] Run the Eagle Eye Validator if any trigger condition holds (see SKILL.md)."
echo "    Apply its diffs to the 03-*.json files, then re-run this script."
echo

echo "[5] Synthesize"
python3 "$SKILL_DIR/scripts/synthesize_results.py" \
  --input "$OUT_DIR/auditor_reports.json" \
  --output "$OUT_DIR/05-synthesis.json" \
  --text

echo
echo "[6] Write $OUT_DIR/99-audit-report.md per references/report-schema.md"
