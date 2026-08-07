#!/usr/bin/env python3
"""
T3 Audit Result Synthesis Script — v2.2
Implements normalization, Litmus Gates, Gray Zone resolution, and the Eagle Eye
Veto per the t3-classification.md specification.

Changes in v2.2 (all covered by tests/test_synthesize.py):
  * Gray Zone Litmus Gate override implemented (spec Step 3 rule 2) — previously
    documented but missing, so the spec's own worked example disagreed with the code.
  * Gray Zone with a negative composite now carries Trash as a secondary.
  * `final_label` is the clean, parseable label; `display_label` carries the
    "(Eagle Eye)" / "(Gray Zone)" annotations. Previously the suffix was baked
    into final_label, which both broke leaderboard grouping and lost the
    "(Gray Zone)" marker whenever Eagle Eye also fired.
  * Missing or malformed `litmus_gate` / `total_score` is now a hard error.
    It used to default silently to "No", flipping one of the four
    primary-classification conditions with no warning.

Stdlib only. No third-party dependencies.
"""

import argparse
import json
import sys
from typing import Dict, List, Any


# ─── Constants ───────────────────────────────────────────────────────────────

TOOL_MAX = 33
TOY_MAX = 33
TRASH_MAX = 42

MAX_BY_ROLE = {"tool": TOOL_MAX, "toy": TOY_MAX, "trash": TRASH_MAX}


class InputError(ValueError):
    """Raised when an auditor report is missing or malformed."""


# ─── Normalization ────────────────────────────────────────────────────────────

def normalize(raw: float, max_raw: float) -> float:
    """Normalize raw score to 0-100 scale."""
    if max_raw == 0:
        return 0.0
    return round((raw / max_raw) * 100, 1)


# ─── Input parsing (strict) ───────────────────────────────────────────────────

def parse_litmus(value: Any) -> bool:
    """Parse a litmus gate value. Raises InputError on anything unrecognized."""
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text.startswith("yes"):
        return True
    if text.startswith("no"):
        return False
    raise InputError(f"litmus_gate must be \"Yes\" or \"No\", got {value!r}")


def read_report(reports: Dict[str, Any], role: str) -> Dict[str, Any]:
    """Pull one auditor report out of the input, failing loudly on bad shape."""
    report = reports.get(role)
    if report is None:
        raise InputError(f"missing '{role}' auditor report")
    if not isinstance(report, dict):
        raise InputError(f"'{role}' auditor report must be an object, "
                         f"got {type(report).__name__}")
    return report


def read_score(report: Dict[str, Any], role: str) -> int:
    """Read and range-check total_score."""
    if "total_score" not in report:
        raise InputError(f"'{role}' report is missing total_score")
    raw = report["total_score"]
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise InputError(f"'{role}' total_score must be an integer, got {raw!r}")
    max_raw = MAX_BY_ROLE[role]
    if not 0 <= raw <= max_raw:
        raise InputError(f"'{role}' total_score {raw} is outside the valid "
                         f"range 0-{max_raw}")
    return raw


def read_gate(report: Dict[str, Any], role: str) -> bool:
    """
    Read the top-level litmus_gate.

    Absent is an error, not a default. The gate is one of only four conditions
    that decide the primary classification, so silently reading a missing gate
    as "No" changes verdicts without leaving a trace.
    """
    if "litmus_gate" not in report:
        raise InputError(
            f"'{role}' report is missing the top-level litmus_gate field. "
            f"Add \"litmus_gate\": \"Yes\" or \"No\" (see {role}-auditor-template.md). "
            f"Run scripts/validate_auditor_json.py to check the auditor output."
        )
    try:
        return parse_litmus(report["litmus_gate"])
    except InputError as e:
        raise InputError(f"'{role}' report: {e}") from None


def _clean_issues(raw: Any) -> List[str]:
    return [str(i) for i in raw if str(i).strip()]


def read_critical_issues(trash: Dict[str, Any]) -> List[str]:
    """
    Read the Eagle Eye triggers, accepting the top-level or nested location.

    An absent *or empty* top-level array falls through to
    extract_for_report.critical_issues. This drives a safety veto, so where the
    two locations disagree, err toward firing it rather than toward dropping it.
    validate_auditor_json.py flags the disagreement itself.
    """
    top = trash.get("critical_issues")
    if top is not None and not isinstance(top, list):
        raise InputError(f"'trash' critical_issues must be a list, "
                         f"got {type(top).__name__}")

    issues = _clean_issues(top or [])
    if issues:
        return issues

    extract = trash.get("extract_for_report")
    if isinstance(extract, dict):
        nested = extract.get("critical_issues")
        if isinstance(nested, list):
            return _clean_issues(nested)
    return []


# ─── Classification ───────────────────────────────────────────────────────────

def check_primary_conditions(norm_tool: float, norm_toy: float, norm_trash: float,
                             litmus_tool: bool, litmus_toy: bool,
                             litmus_trash: bool) -> Dict[str, int]:
    """
    Count how many primary-classification conditions each category meets.
    Per t3-classification.md Step 1: 2+ conditions makes a category Primary.
    """
    tool_count = 0
    if norm_tool >= 75:              tool_count += 1
    if norm_tool > norm_toy + 20:    tool_count += 1
    if norm_tool > norm_trash + 20:  tool_count += 1
    if litmus_tool:                  tool_count += 1

    toy_count = 0
    if norm_toy >= 75:               toy_count += 1
    if norm_toy > norm_tool + 20:    toy_count += 1
    if norm_toy > norm_trash + 20:   toy_count += 1
    if litmus_toy:                   toy_count += 1

    trash_count = 0
    if norm_trash >= 60:             trash_count += 1  # lower threshold per spec
    if norm_trash > norm_tool + 20:  trash_count += 1
    if norm_trash > norm_toy + 20:   trash_count += 1
    if litmus_trash:                 trash_count += 1

    return {"tool": tool_count, "toy": toy_count, "trash": trash_count}


def resolve_gray_zone(norm_tool: float, norm_toy: float, composite: float,
                      litmus_tool: bool, litmus_toy: bool,
                      litmus_trash: bool) -> str:
    """
    Gray Zone resolution per t3-classification.md Step 3, in spec order.

    Rule 2 (Litmus Gate override) outranks rule 1 (composite tiebreaker): when
    exactly one category passes its gate, that category is the only one with any
    positive evidence signal, so it wins regardless of the composite.
    """
    gates = {"Tool": litmus_tool, "Toy": litmus_toy, "Trash": litmus_trash}
    passing = [name for name, passed in gates.items() if passed]
    if len(passing) == 1:
        return passing[0]

    # Rule 1: composite tiebreaker.
    if composite < 0:
        return "Trash"
    # composite > 0, or == 0: higher of Tool/Toy, Tool wins ties.
    return "Tool" if norm_tool >= norm_toy else "Toy"


def determine_secondary(primary: str, norm_tool: float, norm_toy: float,
                        norm_trash: float, gray_zone: bool,
                        composite: float) -> List[str]:
    """Determine secondary classification per t3-classification.md Step 2."""
    secondary: List[str] = []
    if primary == "Tool":
        if norm_toy >= 60:   secondary.append("Toy")
        if norm_trash >= 50: secondary.append("Trash")
    elif primary == "Toy":
        if norm_tool >= 60:  secondary.append("Tool")
        if norm_trash >= 50: secondary.append("Trash")
    elif primary == "Trash":
        if norm_tool >= 50:  secondary.append("Tool")
        if norm_toy >= 50:   secondary.append("Toy")

    # Gray Zone rule: a negative composite means Trash outweighs the winner even
    # when NormTrash sits under the usual 50 threshold, so it is always named.
    if gray_zone and composite < 0 and primary != "Trash" and "Trash" not in secondary:
        secondary.append("Trash")

    return secondary


def classify(norm_tool: float, norm_toy: float, norm_trash: float,
             litmus_tool: bool, litmus_toy: bool, litmus_trash: bool,
             eagle_eye_triggers: List[str]) -> Dict[str, Any]:
    """
    Full classification logic per t3-classification.md.
    The Eagle Eye Veto forces Trash into the label when critical issues exist.
    """
    composite = max(norm_tool, norm_toy) - norm_trash
    counts = check_primary_conditions(norm_tool, norm_toy, norm_trash,
                                      litmus_tool, litmus_toy, litmus_trash)

    # ── Primary ────────────────────────────────────────────────────────────
    gray_zone = max(counts.values()) < 2

    if gray_zone:
        primary = resolve_gray_zone(norm_tool, norm_toy, composite,
                                    litmus_tool, litmus_toy, litmus_trash)
    else:
        # Most conditions wins; ties break on normalized score.
        norms = {"Tool": norm_tool, "Toy": norm_toy, "Trash": norm_trash}
        primary = sorted(
            [(name, counts[name.lower()], norms[name]) for name in ("Tool", "Toy", "Trash")],
            key=lambda x: (-x[1], -x[2]),
        )[0][0]

    # ── Secondary ──────────────────────────────────────────────────────────
    secondary = determine_secondary(primary, norm_tool, norm_toy, norm_trash,
                                    gray_zone, composite)

    # ── Eagle Eye Veto ─────────────────────────────────────────────────────
    eagle_eye_activated = len(eagle_eye_triggers) > 0
    if eagle_eye_activated and primary != "Trash" and "Trash" not in secondary:
        secondary.append("Trash")

    # ── Confidence ────────────────────────────────────────────────────────
    if eagle_eye_activated:
        confidence = "Review Required"
    elif gray_zone:
        confidence = "Low"
    elif max(counts.values()) >= 3:
        confidence = "High"
    else:
        confidence = "Medium"

    # ── Labels ────────────────────────────────────────────────────────────
    # final_label stays clean so leaderboards can group on it; display_label
    # carries the annotations for humans.
    final_label = " + ".join([primary] + secondary)
    annotations = []
    if eagle_eye_activated:
        annotations.append("Eagle Eye")
    if gray_zone:
        annotations.append("Gray Zone")
    display_label = final_label + (f" ({', '.join(annotations)})" if annotations else "")

    return {
        "primary": primary,
        "secondary": secondary,
        "final_label": final_label,
        "display_label": display_label,
        "eagle_eye_veto_activated": eagle_eye_activated,
        "eagle_eye_triggers": eagle_eye_triggers,
        "confidence": confidence,
        "composite_score": round(composite, 1),
        "condition_counts": counts,
        "gray_zone": gray_zone,
    }


# ─── Synthesis ────────────────────────────────────────────────────────────────

def synthesize_results(auditor_reports: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize three Auditor reports into a final T3 audit result.

    Expected input keys: "tool", "toy", "trash". Each report needs total_score
    (int) and litmus_gate ("Yes"/"No"); the trash report also needs
    critical_issues (list). Raises InputError on anything missing or malformed.
    """
    tool = read_report(auditor_reports, "tool")
    toy = read_report(auditor_reports, "toy")
    trash = read_report(auditor_reports, "trash")

    tool_raw = read_score(tool, "tool")
    toy_raw = read_score(toy, "toy")
    trash_raw = read_score(trash, "trash")

    norm_tool = normalize(tool_raw, TOOL_MAX)
    norm_toy = normalize(toy_raw, TOY_MAX)
    norm_trash = normalize(trash_raw, TRASH_MAX)

    litmus_tool = read_gate(tool, "tool")
    litmus_toy = read_gate(toy, "toy")
    litmus_trash = read_gate(trash, "trash")

    eagle_eye_triggers = read_critical_issues(trash)

    classification = classify(
        norm_tool, norm_toy, norm_trash,
        litmus_tool, litmus_toy, litmus_trash,
        eagle_eye_triggers,
    )

    scores = {
        "tool_raw": tool_raw,   "tool_max": TOOL_MAX,   "tool_normalized": norm_tool,
        "toy_raw": toy_raw,     "toy_max": TOY_MAX,     "toy_normalized": norm_toy,
        "trash_raw": trash_raw, "trash_max": TRASH_MAX, "trash_normalized": norm_trash,
        "composite": classification["composite_score"],
    }

    return {
        "scores": scores,
        "litmus_gates": {
            "tool": "Yes" if litmus_tool else "No",
            "toy": "Yes" if litmus_toy else "No",
            "trash": "Yes" if litmus_trash else "No",
        },
        "classification": classification,
        "final_verdict_summary": _build_verdict(classification, scores, auditor_reports),
        "auditor_reports": auditor_reports,
    }


def _extract_reason(report: Dict[str, Any]) -> str:
    extract = report.get("extract_for_report")
    if not isinstance(extract, dict):
        return ""
    return str(extract.get("litmus_test_reason", "")).strip()


def _build_verdict(classification: Dict, scores: Dict, reports: Dict) -> str:
    primary = classification["primary"]
    comp = scores["composite"]

    verdict = (f"Classification: {classification['display_label']}. "
               f"Composite score {comp:+.1f}. ")

    if primary == "Tool":
        verdict += (f"Product delivers quantifiable utility "
                    f"(Tool normalized {scores['tool_normalized']:.0f}/100). ")
        reason = _extract_reason(reports.get("tool", {}))
    elif primary == "Toy":
        verdict += (f"Product delivers emotional/aesthetic value "
                    f"(Toy normalized {scores['toy_normalized']:.0f}/100). ")
        reason = _extract_reason(reports.get("toy", {}))
    else:
        verdict += (f"Product creates more problems than it solves "
                    f"(Trash normalized {scores['trash_normalized']:.0f}/100). ")
        reason = _extract_reason(reports.get("trash", {}))

    if reason:
        verdict += f"{reason.rstrip('.')}. "

    if classification["gray_zone"]:
        verdict += ("Gray Zone: no category met 2+ primary conditions, so this "
                    "classification is provisional. ")

    if classification["eagle_eye_veto_activated"]:
        issues = classification["eagle_eye_triggers"]
        verdict += f"⚠️ Eagle Eye Veto activated — critical issues: {'; '.join(issues[:2])}."

    return verdict.strip()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def render_text(result: Dict[str, Any]) -> str:
    s = result["scores"]
    c = result["classification"]
    g = result["litmus_gates"]
    lines = [
        "=" * 60,
        "T3 AUDIT SYNTHESIS  —  v2.2",
        "=" * 60,
        "",
        f"🟢 Tool  : {s['tool_raw']:>2}/{s['tool_max']}  →  {s['tool_normalized']:.1f}/100",
        f"🟡 Toy   : {s['toy_raw']:>2}/{s['toy_max']}  →  {s['toy_normalized']:.1f}/100",
        f"🔴 Trash : {s['trash_raw']:>2}/{s['trash_max']} →  {s['trash_normalized']:.1f}/100",
        "",
        f"Composite : {s['composite']:+.1f}",
        f"Litmus    : Tool={g['tool']}  Toy={g['toy']}  Trash={g['trash']}",
        "",
        "─" * 60,
        f"Classification : {c['display_label']}",
        f"Confidence     : {c['confidence']}",
    ]
    if c["gray_zone"]:
        lines.append("Gray Zone      : no category met 2+ primary conditions")
    if c["eagle_eye_veto_activated"]:
        lines.append("")
        lines.append("🚨 Eagle Eye Veto ACTIVE:")
        lines.extend(f"   • {t}" for t in c["eagle_eye_triggers"])
    lines.extend(["", result["final_verdict_summary"]])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize T3 audit results from three Auditor reports (v2.2)"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Path to JSON file containing tool/toy/trash auditor reports")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--text", action="store_true", help="Human-readable text summary")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            auditor_reports = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(auditor_reports, dict):
        print("Error: input must be a JSON object with tool/toy/trash keys", file=sys.stderr)
        sys.exit(1)

    try:
        result = synthesize_results(auditor_reports)
    except InputError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.text:
        print(render_text(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nSaved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
