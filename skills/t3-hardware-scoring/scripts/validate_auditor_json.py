#!/usr/bin/env python3
"""
T3 Auditor JSON Validator & Merger — v2.2

Replaces the hand-written "Step 3.5 auto-rebuild" instructions with a
deterministic check. An LLM subagent can produce a JSON that *looks* right and
still be arithmetically wrong; this catches that before it reaches the Final
Judge, where a single wrong total silently changes the classification.

Two modes:

  validate   Check one auditor JSON against its rubric contract.
             $ validate_auditor_json.py validate --role trash 03-trash-auditor.json

  merge      Validate all three, then build auditor_reports.json from them.
             $ validate_auditor_json.py merge \\
                 --tool 03-tool-auditor.json \\
                 --toy 03-toy-auditor.json \\
                 --trash 03-trash-auditor.json \\
                 --output auditor_reports.json

Exit codes: 0 = clean, 1 = errors found, 2 = bad usage / unreadable input.
Warnings never fail the run; pass --strict to promote them to errors.

Stdlib only. No third-party dependencies.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple

# ─── Rubric contracts ─────────────────────────────────────────────────────────
# The item IDs each role must score, and the section each belongs to. These are
# the single source of truth for "did the auditor fill in everything?".

TOOL_ITEMS = ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "4.1", "4.2"]
TOY_ITEMS = ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "4.1", "4.2"]
TRASH_ITEMS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6",
               "2.1", "2.2", "2.3",
               "3.1", "3.2", "3.3",
               "4.1", "4.2"]

ROLES: Dict[str, Dict[str, Any]] = {
    "tool":  {"items": TOOL_ITEMS,  "max": 33, "auditor": "Tool"},
    "toy":   {"items": TOY_ITEMS,   "max": 33, "auditor": "Toy"},
    "trash": {"items": TRASH_ITEMS, "max": 42, "auditor": "Trash"},
}

# The canonical Eagle Eye trigger set, mirrored from the "Canonical Trigger
# Index" table in references/trash-red-flags.md. tests/test_trigger_consistency.py
# fails if this map and that table disagree.
EAGLE_EYE_PATTERNS = {
    "Core Flaw": "1.2",
    "Snake Oil": "1.2",
    "False Pain Point": "1.2",
    "Privacy Tension": "1.5",
    "Inconsistent Claims": "1.5",
    'Broken "Never" Promise': "1.5",
    "Architectural Implausibility": "1.5",
    "Severe Side Effects": "2.1",
    "Workflow Sabotage": "2.1",
    "Price vs. Doubt": "3.2",
    "Promise vs. Delivery": "3.2",
    "Subscription Trap / Brick": "3.3",
    "App Redundancy": "4.1",
    "Delusional Raison d'être": "4.2",
}

# Items where an Eagle Eye pattern can fire.
EAGLE_EYE_ITEMS = set(EAGLE_EYE_PATTERNS.values())

TRIGGER_PREFIX = re.compile(r"^\s*Triggered:", re.IGNORECASE)


def trigger_pattern(reason: str) -> str:
    """
    Extract the canonical pattern name from a `"Triggered: <Pattern>. ..."` reason.

    Splitting on the first period does not work — several pattern names contain
    one ("Price vs. Doubt"). Match against the known names instead, longest
    first so "Price vs. Doubt" is not shadowed by a shorter prefix.
    """
    body = TRIGGER_PREFIX.sub("", reason).strip()
    for name in sorted(EAGLE_EYE_PATTERNS, key=len, reverse=True):
        if body.lower().startswith(name.lower()):
            return name
    return ""

# Per SKILL.md Step 3, verbatim_evidence is capped by score to control tokens.
MAX_QUOTES_BY_SCORE = {0: 0, 1: 1, 2: 2, 3: 2}

REASON_SOFT_LIMIT = 60  # docs say "~50 characters"; warn past 60


class Report:
    """Collects errors and warnings for one file."""

    def __init__(self, label: str):
        self.label = label
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self, strict: bool = False) -> str:
        lines = []
        for e in self.errors:
            lines.append(f"  ERROR  [{self.label}] {e}")
        for w in self.warnings:
            tag = "ERROR" if strict else "warn "
            lines.append(f"  {tag}  [{self.label}] {w}")
        if not lines:
            lines.append(f"  ok     [{self.label}] all checks passed")
        return "\n".join(lines)


# ─── Field access helpers ─────────────────────────────────────────────────────

def _iter_items(doc: Dict[str, Any]) -> Tuple[Dict[str, Tuple[str, Dict[str, Any]]], List[str]]:
    """
    Flatten checklist_items -> ({item_id: (section_name, item_dict)}, duplicates).

    The schema nests items under free-text section names ("1. Pain Point
    Identification and Resolution"), which auditors reword. Key off the item ID
    instead so a reworded section header is a warning, not a hard failure.

    An ID appearing in two sections is reported rather than silently collapsed:
    only one copy would reach the total, so the arithmetic check would pass
    against the wrong evidence.
    """
    flat: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    duplicates: List[str] = []
    sections = doc.get("checklist_items")
    if not isinstance(sections, dict):
        return flat, duplicates
    for section_name, section in sections.items():
        if not isinstance(section, dict):
            continue
        items = section.get("items")
        if not isinstance(items, dict):
            continue
        for item_id, item in items.items():
            if not isinstance(item, dict):
                continue
            key = str(item_id).strip()
            if key in flat:
                duplicates.append(key)
                continue
            flat[key] = (section_name, item)
    return flat, duplicates


def _parse_gate(value: Any) -> str:
    """Normalize a litmus gate value to 'Yes' / 'No' / '' (unparseable)."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    text = str(value).strip().lower()
    if text.startswith("yes"):
        return "Yes"
    if text.startswith("no"):
        return "No"
    return ""


# ─── Validation ───────────────────────────────────────────────────────────────

def validate(doc: Dict[str, Any], role: str, label: str) -> Report:
    """Check one auditor JSON against the rubric contract for `role`."""
    contract = ROLES[role]
    rep = Report(label)

    expected_ids = contract["items"]
    max_score = contract["max"]

    # ── Structure ────────────────────────────────────────────────────────────
    flat, duplicates = _iter_items(doc)
    if not flat:
        rep.error("checklist_items is missing, empty, or not the expected "
                  "{section: {items: {id: {...}}}} shape")
        return rep

    if duplicates:
        rep.error(f"item ID(s) appear in more than one section: "
                  f"{', '.join(sorted(set(duplicates)))}")

    missing = [i for i in expected_ids if i not in flat]
    if missing:
        rep.error(f"missing scored items: {', '.join(missing)} "
                  f"({len(expected_ids)} required for the {role} rubric)")

    unexpected = [i for i in flat if i not in expected_ids]
    if unexpected:
        rep.error(f"unexpected item IDs not in the {role} rubric: {', '.join(sorted(unexpected))}")

    # ── Per-item checks ──────────────────────────────────────────────────────
    running_total = 0
    triggered_items: List[str] = []

    for item_id in expected_ids:
        if item_id not in flat:
            continue
        _, item = flat[item_id]
        score = item.get("score")

        if not isinstance(score, int) or isinstance(score, bool):
            rep.error(f"item {item_id}: score must be an integer, got {score!r}")
            continue
        if not 0 <= score <= 3:
            rep.error(f"item {item_id}: score {score} outside the 0-3 scale")
            continue
        running_total += score

        declared_max = item.get("max_score")
        if declared_max is not None and declared_max != 3:
            rep.error(f"item {item_id}: max_score must be 3, got {declared_max!r}")

        # Evidence-first: every rubric says a score with no quote must be 0.
        evidence = item.get("verbatim_evidence")
        if evidence is None:
            rep.error(f"item {item_id}: verbatim_evidence is required (use [] for score 0)")
            evidence = []
        elif not isinstance(evidence, list):
            rep.error(f"item {item_id}: verbatim_evidence must be a list, got {type(evidence).__name__}")
            evidence = []

        quotes = [q for q in evidence if isinstance(q, str) and q.strip()]

        if score > 0 and not quotes:
            rep.error(f"item {item_id}: score {score} with no verbatim_evidence "
                      "(evidence-first rule: no quote -> score 0)")
        if score == 0 and quotes:
            rep.warn(f"item {item_id}: score 0 should carry an empty verbatim_evidence list")

        cap = MAX_QUOTES_BY_SCORE[score]
        if len(quotes) > cap:
            rep.warn(f"item {item_id}: {len(quotes)} quotes exceeds the cap of "
                     f"{cap} for score {score} (SKILL.md token guardrail)")

        # Placeholder text left in from the template.
        if any(q.strip() in {"...", "<exact quote>"} for q in quotes):
            rep.error(f"item {item_id}: verbatim_evidence still contains template placeholder text")

        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            if score > 0:
                rep.error(f"item {item_id}: score {score} requires a non-empty reason")
        elif len(reason) > REASON_SOFT_LIMIT:
            rep.warn(f"item {item_id}: reason is {len(reason)} chars (docs ask for ~50)")

        # Eagle Eye bookkeeping (trash only).
        if role == "trash" and isinstance(reason, str) and TRIGGER_PREFIX.match(reason):
            triggered_items.append(item_id)
            if score != 3:
                rep.error(f"item {item_id}: reason declares an Eagle Eye trigger "
                          f"but score is {score} (a trigger forces 3)")

            pattern = trigger_pattern(reason)
            if not pattern:
                rep.warn(f"item {item_id}: reason does not name a canonical Eagle Eye "
                         "pattern — use \"Triggered: <Pattern>.\" exactly as spelled "
                         "in trash-red-flags.md")
            elif EAGLE_EYE_PATTERNS[pattern] != item_id:
                rep.error(f"item {item_id}: pattern {pattern!r} belongs to item "
                          f"{EAGLE_EYE_PATTERNS[pattern]}, not {item_id}")
            elif item_id not in EAGLE_EYE_ITEMS:
                rep.warn(f"item {item_id}: Eagle Eye trigger on an item with no "
                         "documented pattern in trash-red-flags.md")

    # ── Section subtotals ────────────────────────────────────────────────────
    sections = doc.get("checklist_items", {})
    if isinstance(sections, dict):
        for section_name, section in sections.items():
            if not isinstance(section, dict):
                continue
            declared = section.get("total")
            items = section.get("items")
            if declared is None or not isinstance(items, dict):
                continue
            actual = sum(i.get("score", 0) for i in items.values()
                         if isinstance(i, dict) and isinstance(i.get("score"), int))
            if declared != actual:
                rep.error(f"section {section_name!r}: declared total {declared} "
                          f"but items sum to {actual}")

    # ── Totals ───────────────────────────────────────────────────────────────
    declared_total = doc.get("total_score")
    if declared_total is None:
        rep.error("total_score is missing")
    elif not isinstance(declared_total, int) or isinstance(declared_total, bool):
        rep.error(f"total_score must be an integer, got {declared_total!r}")
    elif not missing and declared_total != running_total:
        rep.error(f"total_score is {declared_total} but the {len(expected_ids)} "
                  f"item scores sum to {running_total}")
    elif declared_total > max_score:
        rep.error(f"total_score {declared_total} exceeds the {role} maximum of {max_score}")

    declared_max = doc.get("max_possible_score")
    if declared_max is not None and declared_max != max_score:
        rep.error(f"max_possible_score is {declared_max}, expected {max_score} for {role}")

    # ── Litmus gate ──────────────────────────────────────────────────────────
    # synthesize_results.py reads the TOP-LEVEL litmus_gate. If it is absent the
    # gate silently reads "No", which is one of only four primary-classification
    # conditions -- a silent miss changes the verdict. Hard error.
    if "litmus_gate" not in doc:
        rep.error("top-level litmus_gate is missing — synthesize_results.py reads "
                  "this field and would silently treat the gate as \"No\"")
    else:
        gate = _parse_gate(doc["litmus_gate"])
        if not gate:
            rep.error(f"litmus_gate must be \"Yes\" or \"No\", got {doc['litmus_gate']!r}")
        else:
            # Cross-check the two places the same answer is repeated.
            nested = doc.get("litmus_test_result", {})
            if isinstance(nested, dict) and "answer" in nested:
                nested_gate = _parse_gate(nested["answer"])
                if nested_gate and nested_gate != gate:
                    rep.error(f"litmus_gate is {gate!r} but litmus_test_result.answer "
                              f"is {nested_gate!r}")
            extract = doc.get("extract_for_report", {})
            if isinstance(extract, dict) and "litmus_test_answer" in extract:
                extract_gate = _parse_gate(extract["litmus_test_answer"])
                if extract_gate and extract_gate != gate:
                    rep.error(f"litmus_gate is {gate!r} but "
                              f"extract_for_report.litmus_test_answer is {extract_gate!r}")

    # ── extract_for_report ───────────────────────────────────────────────────
    extract = doc.get("extract_for_report")
    if not isinstance(extract, dict):
        rep.error("extract_for_report is required — 99-audit-report.md is built from it")
        extract = {}

    # ── Trash-only: critical_issues must match the triggers actually scored ──
    if role == "trash":
        issues = doc.get("critical_issues")
        if issues is None:
            rep.error("critical_issues is required on the Trash report "
                      "(use [] when nothing triggered) — it drives the Eagle Eye Veto")
        elif not isinstance(issues, list):
            rep.error(f"critical_issues must be a list, got {type(issues).__name__}")
        else:
            if len(issues) != len(triggered_items):
                rep.error(f"critical_issues has {len(issues)} entries but "
                          f"{len(triggered_items)} item(s) carry a \"Triggered:\" reason "
                          f"({', '.join(triggered_items) or 'none'})")
            if triggered_items and not issues:
                rep.error("Eagle Eye triggers were scored but critical_issues is empty — "
                          "the veto would not fire")

            # The same list is repeated under extract_for_report. The synthesizer
            # falls back to that copy when the top-level one is empty, so a
            # disagreement between them changes whether the veto fires.
            nested = extract.get("critical_issues") if isinstance(extract, dict) else None
            if isinstance(nested, list) and len(nested) != len(issues):
                rep.error(f"critical_issues has {len(issues)} entries but "
                          f"extract_for_report.critical_issues has {len(nested)}")

    # ── Declared identity ────────────────────────────────────────────────────
    auditor = doc.get("auditor")
    if auditor is not None and str(auditor).strip().lower() != role:
        rep.error(f"auditor field says {auditor!r} but this was validated as {role!r}")

    if doc.get("information_isolation_confirmed") is not True:
        rep.warn("information_isolation_confirmed is not true — "
                 "the auditor did not confirm it worked from Brand-Blinded text only")

    return rep


# ─── Merge ────────────────────────────────────────────────────────────────────

def build_merged(docs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build auditor_reports.json from the three validated auditor documents.

    This is the mechanical version of SKILL.md Step 3.5 — every value is copied
    from a source file, never retyped from a summary.
    """
    merged: Dict[str, Any] = {}
    for role in ("tool", "toy", "trash"):
        doc = docs[role]
        entry = {
            "total_score": doc.get("total_score"),
            "litmus_gate": _parse_gate(doc.get("litmus_gate")) or "No",
            "extract_for_report": doc.get("extract_for_report", {}),
        }
        if role == "trash":
            entry["critical_issues"] = doc.get("critical_issues", [])
        merged[role] = entry
    return merged


# ─── CLI ──────────────────────────────────────────────────────────────────────

def load(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(doc, dict):
        print(f"Error: {path} must contain a JSON object", file=sys.stderr)
        sys.exit(2)
    return doc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Validate one auditor JSON")
    p_val.add_argument("path")
    p_val.add_argument("--role", required=True, choices=sorted(ROLES))
    p_val.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    p_mrg = sub.add_parser("merge", help="Validate all three and build auditor_reports.json")
    p_mrg.add_argument("--tool", required=True)
    p_mrg.add_argument("--toy", required=True)
    p_mrg.add_argument("--trash", required=True)
    p_mrg.add_argument("--output", "-o", help="Write merged JSON here (default: stdout)")
    p_mrg.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    if args.command == "validate":
        rep = validate(load(args.path), args.role, args.path)
        print(rep.render(args.strict))
        failed = rep.errors or (args.strict and rep.warnings)
        sys.exit(1 if failed else 0)

    # merge
    paths = {"tool": args.tool, "toy": args.toy, "trash": args.trash}
    docs = {role: load(path) for role, path in paths.items()}

    reports = [validate(docs[role], role, paths[role]) for role in ("tool", "toy", "trash")]
    for rep in reports:
        print(rep.render(args.strict), file=sys.stderr)

    failed = any(r.errors for r in reports) or (args.strict and any(r.warnings for r in reports))
    if failed:
        print("\nRefusing to merge: fix the errors above and re-run the affected auditor.",
              file=sys.stderr)
        sys.exit(1)

    merged = build_merged(docs)
    payload = json.dumps(merged, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload + "\n")
        print(f"\nMerged 3 auditor reports -> {args.output}", file=sys.stderr)
    else:
        print(payload)


if __name__ == "__main__":
    main()
