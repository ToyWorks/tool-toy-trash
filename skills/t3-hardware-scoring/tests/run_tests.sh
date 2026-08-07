#!/usr/bin/env bash
# Run the T3 skill test suite. Stdlib Python only — no install step.
#
#   skills/t3-hardware-scoring/tests/run_tests.sh
#
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SKILL_DIR"

echo "== unit + golden-case tests =="
python3 -m unittest discover -s tests -v

echo
echo "== CLI smoke test: validate -> merge -> synthesize =="
FIXTURE="tests/fixtures/golden-ai-pendant"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for role in tool toy trash; do
  python3 scripts/validate_auditor_json.py validate --role "$role" \
    "$FIXTURE/03-$role-auditor.json"
done

python3 scripts/validate_auditor_json.py merge \
  --tool  "$FIXTURE/03-tool-auditor.json" \
  --toy   "$FIXTURE/03-toy-auditor.json" \
  --trash "$FIXTURE/03-trash-auditor.json" \
  --output "$TMP/auditor_reports.json"

# The committed fixture must stay reproducible from its three source reports.
if ! diff -q "$TMP/auditor_reports.json" "$FIXTURE/auditor_reports.json" >/dev/null; then
  echo "FAIL: merge output drifted from $FIXTURE/auditor_reports.json" >&2
  diff -u "$FIXTURE/auditor_reports.json" "$TMP/auditor_reports.json" >&2 || true
  exit 1
fi

python3 scripts/synthesize_results.py --input "$TMP/auditor_reports.json" --text

echo
echo "== a broken report must be rejected =="
python3 - "$FIXTURE/03-trash-auditor.json" "$TMP/broken.json" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))
doc["total_score"] += 1           # totals no longer match the items
json.dump(doc, open(sys.argv[2], "w", encoding="utf-8"))
PY

if python3 scripts/validate_auditor_json.py validate --role trash "$TMP/broken.json"; then
  echo "FAIL: validator accepted a report whose total does not match its items" >&2
  exit 1
fi
echo "  ok     validator rejected the tampered report as expected"

echo
echo "All checks passed."
