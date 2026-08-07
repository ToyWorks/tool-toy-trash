#!/usr/bin/env python3
"""
Tests for scripts/validate_auditor_json.py.

Each test starts from the golden fixture (a known-good auditor report), breaks
exactly one thing, and asserts the validator notices. That shape matters: it
proves the check fires for the reason we think it does, rather than because the
fixture was broken in five ways at once.
"""

import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from validate_auditor_json import build_merged, validate  # noqa: E402

GOLDEN = os.path.join(HERE, "fixtures", "golden-ai-pendant")


def load(role):
    with open(os.path.join(GOLDEN, f"03-{role}-auditor.json"), encoding="utf-8") as f:
        return json.load(f)


def errors_for(doc, role):
    return validate(doc, role, "test").errors


def find_item(doc, item_id):
    """Return the item dict for `item_id` regardless of which section holds it."""
    for section in doc["checklist_items"].values():
        if item_id in section["items"]:
            return section["items"][item_id]
    raise KeyError(item_id)


class TestGoldenFixturesAreClean(unittest.TestCase):
    """If the fixtures themselves drift, every other test here becomes meaningless."""

    def test_all_three_pass_without_errors_or_warnings(self):
        for role in ("tool", "toy", "trash"):
            rep = validate(load(role), role, role)
            self.assertEqual(rep.errors, [], f"{role}: {rep.errors}")
            self.assertEqual(rep.warnings, [], f"{role}: {rep.warnings}")


class TestArithmetic(unittest.TestCase):
    """
    The failure SKILL.md Step 3.5 warns about in prose: a total that does not
    match the items it claims to sum.
    """

    def test_total_score_mismatch_is_caught(self):
        doc = load("trash")
        doc["total_score"] = 29  # items still sum to 30
        errs = errors_for(doc, "trash")
        self.assertTrue(any("sum to 30" in e for e in errs), errs)

    def test_section_subtotal_mismatch_is_caught(self):
        doc = load("tool")
        list(doc["checklist_items"].values())[0]["total"] = 99
        self.assertTrue(any("declared total 99" in e for e in errors_for(doc, "tool")))

    def test_total_above_the_role_maximum_is_caught(self):
        doc = load("tool")
        find_item(doc, "1.3")["score"] = 3
        find_item(doc, "1.3")["verbatim_evidence"] = ["x"]
        doc["total_score"] = 99
        self.assertTrue(errors_for(doc, "tool"))

    def test_score_outside_the_0_3_scale_is_caught(self):
        doc = load("tool")
        find_item(doc, "1.1")["score"] = 5
        self.assertTrue(any("outside the 0-3 scale" in e for e in errors_for(doc, "tool")))

    def test_wrong_max_possible_score_for_role_is_caught(self):
        doc = load("tool")
        doc["max_possible_score"] = 42  # that is the Trash maximum
        self.assertTrue(any("max_possible_score" in e for e in errors_for(doc, "tool")))


class TestRubricCoverage(unittest.TestCase):
    """Trash scores 14 items, Tool and Toy score 11. A dropped item is silent data loss."""

    def test_missing_item_is_caught(self):
        doc = load("trash")
        del doc["checklist_items"]["4. Replaceability"]["items"]["4.2"]
        self.assertTrue(any("missing scored items: 4.2" in e for e in errors_for(doc, "trash")))

    def test_trash_json_validated_as_tool_is_caught(self):
        """The 14-item Trash rubric has IDs the 11-item Tool rubric does not."""
        errs = errors_for(load("trash"), "tool")
        self.assertTrue(any("unexpected item IDs" in e for e in errs), errs)

    def test_auditor_field_mismatch_is_caught(self):
        doc = load("tool")
        doc["auditor"] = "Trash"
        self.assertTrue(any("auditor field says" in e for e in errors_for(doc, "tool")))


class TestEvidenceFirst(unittest.TestCase):
    """
    "Evidence FIRST, then score — no score without a verbatim quote" (SKILL.md).
    This is the rule that keeps the whole audit anchored to the source text.
    """

    def test_score_without_evidence_is_caught(self):
        doc = load("tool")
        find_item(doc, "1.1")["verbatim_evidence"] = []
        errs = errors_for(doc, "tool")
        self.assertTrue(any("no verbatim_evidence" in e for e in errs), errs)

    def test_blank_quotes_do_not_count_as_evidence(self):
        doc = load("tool")
        find_item(doc, "1.1")["verbatim_evidence"] = ["", "   "]
        self.assertTrue(any("no verbatim_evidence" in e for e in errors_for(doc, "tool")))

    def test_template_placeholder_left_in_is_caught(self):
        doc = load("tool")
        find_item(doc, "1.1")["verbatim_evidence"] = ["<exact quote>"]
        self.assertTrue(any("placeholder" in e for e in errors_for(doc, "tool")))

    def test_missing_evidence_key_is_caught(self):
        doc = load("tool")
        del find_item(doc, "1.3")["verbatim_evidence"]
        self.assertTrue(any("verbatim_evidence is required" in e for e in errors_for(doc, "tool")))

    def test_score_without_a_reason_is_caught(self):
        doc = load("tool")
        find_item(doc, "1.1")["reason"] = ""
        self.assertTrue(any("requires a non-empty reason" in e for e in errors_for(doc, "tool")))

    def test_quote_cap_is_a_warning_not_an_error(self):
        """Token guardrails should nudge, not block a finished audit."""
        doc = load("tool")
        find_item(doc, "1.1")["verbatim_evidence"] = ["a", "b", "c", "d"]
        rep = validate(doc, "tool", "test")
        self.assertEqual(rep.errors, [])
        self.assertTrue(any("exceeds the cap" in w for w in rep.warnings))


class TestLitmusGate(unittest.TestCase):
    """
    The three *-auditor.md rubric guides show a JSON body with no top-level
    litmus_gate, while synthesize_results.py reads exactly that field. An auditor
    that follows the rubric guide verbatim produces a report whose gate silently
    reads "No".
    """

    def test_missing_top_level_gate_is_an_error(self):
        doc = load("tool")
        del doc["litmus_gate"]
        errs = errors_for(doc, "tool")
        self.assertTrue(any("litmus_gate is missing" in e for e in errs), errs)

    def test_gate_contradicting_the_nested_answer_is_caught(self):
        doc = load("trash")
        doc["litmus_gate"] = "No"  # litmus_test_result.answer is still "Yes"
        self.assertTrue(any("litmus_test_result.answer" in e for e in errors_for(doc, "trash")))

    def test_gate_contradicting_the_report_extract_is_caught(self):
        doc = load("trash")
        doc["extract_for_report"]["litmus_test_answer"] = "No"
        errs = errors_for(doc, "trash")
        self.assertTrue(any("extract_for_report" in e for e in errs), errs)

    def test_unparseable_gate_value_is_caught(self):
        doc = load("tool")
        doc["litmus_gate"] = "probably"
        self.assertTrue(any("must be" in e for e in errors_for(doc, "tool")))


class TestEagleEyeBookkeeping(unittest.TestCase):
    """
    A trigger has to reach critical_issues to have any effect — that array is
    the sole input to the Eagle Eye Veto. A trigger scored but never recorded is
    a silently discarded veto.
    """

    def test_trigger_missing_from_critical_issues_is_caught(self):
        doc = load("trash")
        # Drop from BOTH copies, so this can only be caught by the
        # trigger-count check and not incidentally by the top-vs-nested check.
        doc["critical_issues"].pop()
        doc["extract_for_report"]["critical_issues"].pop()
        errs = errors_for(doc, "trash")
        self.assertTrue(any("4 entries but" in e and "Triggered:" in e for e in errs), errs)

    def test_pattern_scored_on_the_wrong_item_is_caught(self):
        """
        App Redundancy belongs to 4.1. Firing it on 4.2 would still be a 3 with
        a "Triggered:" reason, so only a name-to-item check catches it.
        """
        doc = load("trash")
        item = find_item(doc, "4.2")
        item["score"] = 3
        item["reason"] = "Triggered: App Redundancy. Free app does it better."
        item["verbatim_evidence"] = ["a free smartphone app does the same"]
        doc["critical_issues"].append("Triggered: App Redundancy. Duplicate.")
        doc["extract_for_report"]["critical_issues"].append("App Redundancy: duplicate.")
        errs = errors_for(doc, "trash")
        self.assertTrue(any("belongs to item 4.1, not 4.2" in e for e in errs), errs)

    def test_invented_pattern_name_is_flagged(self):
        doc = load("trash")
        find_item(doc, "1.5")["reason"] = "Triggered: Bad Vibes. Feels wrong."
        rep = validate(doc, "trash", "test")
        self.assertTrue(any("canonical Eagle Eye pattern" in w for w in rep.warnings),
                        rep.warnings)

    def test_all_triggers_dropped_is_caught(self):
        doc = load("trash")
        doc["critical_issues"] = []
        errs = errors_for(doc, "trash")
        self.assertTrue(any("the veto would not fire" in e for e in errs), errs)

    def test_trigger_reason_not_scored_3_is_caught(self):
        doc = load("trash")
        find_item(doc, "1.5")["score"] = 2
        errs = errors_for(doc, "trash")
        self.assertTrue(any("forces 3" in e for e in errs), errs)

    def test_missing_critical_issues_key_is_caught(self):
        doc = load("trash")
        del doc["critical_issues"]
        self.assertTrue(any("critical_issues is required" in e for e in errors_for(doc, "trash")))

    def test_clean_trash_report_with_no_triggers_is_valid(self):
        """A product can legitimately trigger nothing — [] must pass."""
        doc = load("trash")
        for section in doc["checklist_items"].values():
            for item in section["items"].values():
                item["score"] = 0
                item["verbatim_evidence"] = []
                item["reason"] = "No evidence of this failure mode."
            section["total"] = 0
        doc["total_score"] = 0
        doc["critical_issues"] = []
        doc["extract_for_report"]["critical_issues"] = []
        doc["litmus_gate"] = "No"
        doc["litmus_test_result"]["answer"] = "No"
        doc["extract_for_report"]["litmus_test_answer"] = "No"
        self.assertEqual(errors_for(doc, "trash"), [])

    def test_top_level_and_nested_critical_issues_must_agree(self):
        """
        The synthesizer falls back to the nested copy when the top-level array
        is empty, so a disagreement decides whether the veto fires.
        """
        doc = load("trash")
        doc["extract_for_report"]["critical_issues"] = doc["critical_issues"][:2]
        errs = errors_for(doc, "trash")
        self.assertTrue(any("extract_for_report.critical_issues has 2" in e for e in errs), errs)


class TestDuplicateItems(unittest.TestCase):
    """An ID in two sections would collapse silently, hiding one set of evidence."""

    def test_duplicate_item_id_across_sections_is_caught(self):
        doc = load("trash")
        doc["checklist_items"]["2. Problem Creation"]["items"]["1.1"] = {
            "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "dupe",
        }
        errs = errors_for(doc, "trash")
        self.assertTrue(any("more than one section" in e for e in errs), errs)


class TestMerge(unittest.TestCase):
    """merge replaces the hand-copied auditor_reports.json of SKILL.md Step 3.5."""

    def setUp(self):
        self.docs = {role: load(role) for role in ("tool", "toy", "trash")}

    def test_merged_shape_matches_what_the_synthesizer_reads(self):
        merged = build_merged(self.docs)
        self.assertEqual(set(merged), {"tool", "toy", "trash"})
        for role in ("tool", "toy", "trash"):
            self.assertIn("total_score", merged[role])
            self.assertIn("litmus_gate", merged[role])
            self.assertIn("extract_for_report", merged[role])
        self.assertIn("critical_issues", merged["trash"])

    def test_values_are_copied_from_source_never_retyped(self):
        merged = build_merged(self.docs)
        self.assertEqual(merged["trash"]["total_score"], self.docs["trash"]["total_score"])
        self.assertEqual(merged["trash"]["critical_issues"],
                         self.docs["trash"]["critical_issues"])
        self.assertEqual(merged["tool"]["litmus_gate"], "No")
        self.assertEqual(merged["trash"]["litmus_gate"], "Yes")

    def test_merge_is_deterministic(self):
        self.assertEqual(build_merged(self.docs),
                         build_merged(copy.deepcopy(self.docs)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
