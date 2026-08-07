#!/usr/bin/env python3
"""
Tests for scripts/synthesize_results.py — the Final Judge math.

These lock down the decision rules in references/t3-classification.md. Every
case names the spec section it comes from, so when a rule changes the test that
must change is obvious.

Run: python3 -m unittest discover -s tests -v     (from the skill directory)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from synthesize_results import (  # noqa: E402
    InputError,
    classify,
    normalize,
    synthesize_results,
)


def report(total, gate, issues=None):
    """Build a minimal auditor report."""
    r = {"total_score": total, "litmus_gate": gate, "extract_for_report": {}}
    if issues is not None:
        r["critical_issues"] = issues
    return r


def reports(tool, tool_gate, toy, toy_gate, trash, trash_gate, issues=None):
    return {
        "tool": report(tool, tool_gate),
        "toy": report(toy, toy_gate),
        "trash": report(trash, trash_gate, issues if issues is not None else []),
    }


class TestNormalization(unittest.TestCase):
    """t3-classification.md — Score Normalization Protocol."""

    def test_maxima(self):
        self.assertEqual(normalize(33, 33), 100.0)
        self.assertEqual(normalize(42, 42), 100.0)

    def test_zero(self):
        self.assertEqual(normalize(0, 33), 0.0)

    def test_rounds_to_one_decimal(self):
        # 26/33 = 78.787...  ->  78.8
        self.assertEqual(normalize(26, 33), 78.8)
        # 21/42 = 50.0 exactly
        self.assertEqual(normalize(21, 42), 50.0)

    def test_different_maxima_are_comparable(self):
        """The whole point of normalizing: 33-scale and 42-scale become one scale."""
        self.assertEqual(normalize(33, 33), normalize(42, 42))


class TestPrimaryClassification(unittest.TestCase):
    """t3-classification.md Step 1 — 2+ conditions makes a category Primary."""

    def test_strong_tool(self):
        result = synthesize_results(reports(27, "Yes", 10, "No", 8, "No"))
        c = result["classification"]
        self.assertEqual(c["primary"], "Tool")
        self.assertEqual(c["secondary"], [])
        self.assertEqual(c["final_label"], "Tool")
        self.assertEqual(c["confidence"], "High")
        self.assertFalse(c["gray_zone"])
        self.assertFalse(c["eagle_eye_veto_activated"])

    def test_strong_toy(self):
        result = synthesize_results(reports(9, "No", 28, "Yes", 7, "No"))
        c = result["classification"]
        self.assertEqual(c["primary"], "Toy")
        self.assertEqual(c["confidence"], "High")

    def test_trash_uses_the_lower_60_threshold(self):
        """Trash becomes Primary at 60 normalized, not 75 — inverted severity."""
        # 26/42 = 61.9 normalized: clears 60 but would miss a 75 threshold.
        result = synthesize_results(reports(8, "No", 8, "No", 26, "Yes"))
        self.assertEqual(result["scores"]["trash_normalized"], 61.9)
        self.assertEqual(result["classification"]["primary"], "Trash")

    def test_medium_confidence_at_exactly_two_conditions(self):
        # Tool 25/33 = 75.8, Toy 20/33 = 60.6, Trash 25/42 = 59.5.
        # Tool clears the >=75 bar and the gate, but neither 20-point gap
        # (75.8 < 80.6 and 75.8 < 79.5) — exactly two conditions.
        result = synthesize_results(reports(25, "Yes", 20, "No", 25, "No"))
        c = result["classification"]
        self.assertEqual(c["condition_counts"]["tool"], 2)
        self.assertEqual(c["primary"], "Tool")
        self.assertEqual(c["confidence"], "Medium")


class TestSecondaryClassification(unittest.TestCase):
    """t3-classification.md Step 2."""

    def test_tool_primary_picks_up_toy_secondary_at_60(self):
        # Toy 20/33 = 60.6 >= 60
        result = synthesize_results(reports(30, "Yes", 20, "No", 5, "No"))
        c = result["classification"]
        self.assertEqual(c["primary"], "Tool")
        self.assertIn("Toy", c["secondary"])

    def test_tool_primary_picks_up_trash_secondary_at_50(self):
        # Trash 21/42 = 50.0, exactly on the threshold.
        result = synthesize_results(reports(26, "Yes", 12, "No", 21, "Yes"))
        c = result["classification"]
        self.assertEqual(c["primary"], "Tool")
        self.assertEqual(c["secondary"], ["Trash"])
        self.assertEqual(c["final_label"], "Tool + Trash")

    def test_trash_secondary_just_below_threshold_is_excluded(self):
        # Trash 20/42 = 47.6 < 50
        result = synthesize_results(reports(26, "Yes", 12, "No", 20, "No"))
        self.assertEqual(result["classification"]["secondary"], [])


class TestSpecWorkedExamples(unittest.TestCase):
    """
    The two fully worked examples printed in t3-classification.md.

    Both of these disagreed with the shipped code before v2.2 — which is exactly
    why they are pinned here.
    """

    def test_eagle_eye_example(self):
        """t3-classification.md 'Strict Output Template' — Tool 26 / Toy 12 / Trash 21."""
        result = synthesize_results(reports(
            26, "Yes", 12, "No", 21, "Yes",
            issues=["Triggered Privacy Tension: Claims local but requires cloud sync."],
        ))
        s, c = result["scores"], result["classification"]

        self.assertEqual(s["tool_normalized"], 78.8)
        self.assertEqual(s["toy_normalized"], 36.4)
        self.assertEqual(s["trash_normalized"], 50.0)
        self.assertEqual(s["composite"], 28.8)

        self.assertEqual(c["primary"], "Tool")
        self.assertEqual(c["secondary"], ["Trash"])
        # The doc prints the label without an annotation; annotations live in
        # display_label so leaderboards can still group on final_label.
        self.assertEqual(c["final_label"], "Tool + Trash")
        self.assertEqual(c["display_label"], "Tool + Trash (Eagle Eye)")
        self.assertTrue(c["eagle_eye_veto_activated"])
        self.assertEqual(c["confidence"], "Review Required")

    def test_gray_zone_example(self):
        """
        t3-classification.md 'Gray Zone example' — Tool 12 / Toy 12 / Trash 20,
        Toy gate Yes. The doc's expected answer is 'Toy + Trash (Gray Zone)'.

        Composite alone would say Trash; the Litmus Gate override (Step 3 rule 2)
        is what makes Toy primary. That override was documented but never
        implemented, so this case used to return 'Trash (Gray Zone)'.
        """
        result = synthesize_results(reports(12, "No", 12, "Yes", 20, "No"))
        s, c = result["scores"], result["classification"]

        self.assertEqual(s["tool_normalized"], 36.4)
        self.assertEqual(s["toy_normalized"], 36.4)
        self.assertEqual(s["trash_normalized"], 47.6)
        self.assertEqual(s["composite"], -11.2)

        self.assertTrue(c["gray_zone"])
        self.assertEqual(c["primary"], "Toy")
        self.assertEqual(c["secondary"], ["Trash"])
        self.assertEqual(c["display_label"], "Toy + Trash (Gray Zone)")
        self.assertEqual(c["confidence"], "Low")


class TestGrayZone(unittest.TestCase):
    """t3-classification.md Step 3 — resolution rules, in order."""

    def test_gray_zone_when_nothing_reaches_two_conditions(self):
        result = synthesize_results(reports(12, "No", 12, "No", 20, "No"))
        self.assertTrue(result["classification"]["gray_zone"])
        self.assertEqual(result["classification"]["confidence"], "Low")

    def test_litmus_override_beats_the_composite_tiebreaker(self):
        """Rule 2 outranks rule 1: one passing gate wins even on a negative composite."""
        result = synthesize_results(reports(12, "Yes", 12, "No", 20, "No"))
        self.assertEqual(result["classification"]["primary"], "Tool")

    def test_no_override_when_two_gates_pass(self):
        """The override is for exactly one passing gate; otherwise fall to composite."""
        result = synthesize_results(reports(12, "Yes", 12, "Yes", 20, "No"))
        c = result["classification"]
        self.assertTrue(c["gray_zone"])
        self.assertEqual(c["primary"], "Trash")  # composite is negative

    def test_composite_tiebreaker_positive(self):
        result = synthesize_results(reports(14, "No", 12, "No", 10, "No"))
        c = result["classification"]
        self.assertTrue(c["gray_zone"])
        self.assertEqual(c["primary"], "Tool")

    def test_composite_exactly_zero_prefers_tool(self):
        # Tool 11/33 = 33.3, Trash 14/42 = 33.3, composite 0.0
        result = synthesize_results(reports(11, "No", 11, "No", 14, "No"))
        c = result["classification"]
        self.assertEqual(result["scores"]["composite"], 0.0)
        self.assertEqual(c["primary"], "Tool")

    def test_negative_composite_names_trash_even_below_the_50_threshold(self):
        """Gray Zone rule: a negative composite always names Trash as secondary."""
        result = synthesize_results(reports(12, "Yes", 12, "No", 20, "No"))
        c = result["classification"]
        self.assertTrue(c["gray_zone"])
        self.assertEqual(result["scores"]["trash_normalized"], 47.6)  # under 50
        self.assertEqual(result["scores"]["composite"], -11.2)
        self.assertEqual(c["primary"], "Tool")
        self.assertIn("Trash", c["secondary"])

    def test_trash_secondary_is_not_forced_when_the_composite_is_positive(self):
        """The Gray Zone rule keys off a negative composite, not the zone itself."""
        result = synthesize_results(reports(14, "Yes", 12, "No", 10, "No"))
        c = result["classification"]
        self.assertTrue(c["gray_zone"])
        self.assertGreater(result["scores"]["composite"], 0)
        self.assertEqual(c["secondary"], [])


class TestEagleEyeVeto(unittest.TestCase):
    """t3-classification.md — Eagle Eye Veto System."""

    def test_veto_forces_trash_into_an_otherwise_clean_tool(self):
        clean = synthesize_results(reports(30, "Yes", 5, "No", 4, "No"))
        self.assertEqual(clean["classification"]["final_label"], "Tool")

        vetoed = synthesize_results(reports(
            30, "Yes", 5, "No", 4, "No",
            issues=["Triggered: Privacy Tension. Claims local, uses cloud."],
        ))
        c = vetoed["classification"]
        self.assertEqual(c["final_label"], "Tool + Trash")
        self.assertEqual(c["confidence"], "Review Required")

    def test_veto_does_not_duplicate_an_existing_trash_secondary(self):
        result = synthesize_results(reports(
            26, "Yes", 12, "No", 21, "Yes", issues=["Triggered: Core Flaw."],
        ))
        self.assertEqual(result["classification"]["secondary"].count("Trash"), 1)

    def test_veto_is_a_noop_when_trash_is_already_primary(self):
        result = synthesize_results(reports(
            8, "No", 8, "No", 30, "Yes", issues=["Triggered: App Redundancy."],
        ))
        c = result["classification"]
        self.assertEqual(c["primary"], "Trash")
        self.assertEqual(c["secondary"], [])
        self.assertEqual(c["final_label"], "Trash")

    def test_veto_overrides_high_confidence(self):
        """Even a 4-condition Tool drops to Review Required under a veto."""
        result = synthesize_results(reports(
            33, "Yes", 3, "No", 2, "No", issues=["Triggered: Core Flaw."],
        ))
        self.assertEqual(result["classification"]["condition_counts"]["tool"], 4)
        self.assertEqual(result["classification"]["confidence"], "Review Required")

    def test_triggers_read_from_the_nested_extract_location(self):
        """Auditors put critical_issues at top level or under extract_for_report."""
        data = reports(30, "Yes", 5, "No", 4, "No")
        del data["trash"]["critical_issues"]
        data["trash"]["extract_for_report"] = {"critical_issues": ["Triggered: Core Flaw."]}
        self.assertTrue(synthesize_results(data)["classification"]["eagle_eye_veto_activated"])

    def test_empty_top_level_does_not_mask_a_populated_nested_list(self):
        """
        This is a safety veto: where the two locations disagree, fire it. An
        empty top-level array used to shadow a populated nested one, silently
        turning a vetoed product back into a clean Tool.
        """
        data = reports(30, "Yes", 5, "No", 4, "No", issues=[])
        data["trash"]["extract_for_report"] = {"critical_issues": ["Triggered: Core Flaw."]}
        c = synthesize_results(data)["classification"]
        self.assertTrue(c["eagle_eye_veto_activated"])
        self.assertEqual(c["final_label"], "Tool + Trash")

    def test_top_level_wins_when_both_are_populated(self):
        data = reports(30, "Yes", 5, "No", 4, "No", issues=["Triggered: App Redundancy."])
        data["trash"]["extract_for_report"] = {
            "critical_issues": ["Triggered: Core Flaw.", "Triggered: Snake Oil."]
        }
        self.assertEqual(
            synthesize_results(data)["classification"]["eagle_eye_triggers"],
            ["Triggered: App Redundancy."],
        )

    def test_both_empty_means_no_veto(self):
        data = reports(30, "Yes", 5, "No", 4, "No", issues=[])
        data["trash"]["extract_for_report"] = {"critical_issues": []}
        self.assertFalse(synthesize_results(data)["classification"]["eagle_eye_veto_activated"])

    def test_empty_string_triggers_do_not_fire_the_veto(self):
        result = synthesize_results(reports(30, "Yes", 5, "No", 4, "No", issues=["", "   "]))
        self.assertFalse(result["classification"]["eagle_eye_veto_activated"])

    def test_both_annotations_survive_together(self):
        """Gray Zone used to be swallowed whenever Eagle Eye also fired."""
        result = synthesize_results(reports(
            12, "No", 12, "Yes", 20, "No", issues=["Triggered: Core Flaw."],
        ))
        c = result["classification"]
        self.assertTrue(c["gray_zone"])
        self.assertTrue(c["eagle_eye_veto_activated"])
        self.assertIn("Eagle Eye", c["display_label"])
        self.assertIn("Gray Zone", c["display_label"])


class TestLabels(unittest.TestCase):
    """final_label stays machine-parseable; display_label carries annotations."""

    def test_final_label_never_carries_annotations(self):
        for data in (
            reports(12, "No", 12, "No", 20, "No"),                              # gray zone
            reports(30, "Yes", 5, "No", 4, "No", issues=["Triggered: X."]),     # eagle eye
        ):
            label = synthesize_results(data)["classification"]["final_label"]
            self.assertNotIn("(", label, f"final_label must stay parseable: {label!r}")

    def test_final_label_is_the_label_parts_joined(self):
        c = synthesize_results(reports(26, "Yes", 12, "No", 21, "Yes"))["classification"]
        self.assertEqual(c["final_label"], " + ".join([c["primary"]] + c["secondary"]))


class TestStrictInputHandling(unittest.TestCase):
    """
    Malformed input must fail loudly.

    The pre-v2.2 script silently defaulted a missing litmus_gate to "No" — and
    the gate is one of only four primary-classification conditions, so a
    subagent that omitted the field quietly changed the verdict.
    """

    def test_missing_litmus_gate_raises(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        del data["tool"]["litmus_gate"]
        with self.assertRaises(InputError) as ctx:
            synthesize_results(data)
        self.assertIn("litmus_gate", str(ctx.exception))

    def test_missing_litmus_gate_would_have_changed_the_verdict(self):
        """
        Proof the old silent default was not harmless.

        Tool 25/33, Toy 20/33, Trash 25/42. With the gate, Tool has the two
        conditions it needs to be Primary outright. Read as "No" — which is what
        an omitted field used to produce — Tool drops to one condition, the whole
        audit falls into the Gray Zone, and confidence goes from Medium to Low.
        """
        with_gate = synthesize_results(reports(25, "Yes", 20, "No", 25, "No"))["classification"]
        as_defaulted = synthesize_results(reports(25, "No", 20, "No", 25, "No"))["classification"]

        self.assertEqual(with_gate["confidence"], "Medium")
        self.assertEqual(as_defaulted["confidence"], "Low")
        self.assertFalse(with_gate["gray_zone"])
        self.assertTrue(as_defaulted["gray_zone"])

    def test_unparseable_litmus_gate_raises(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        data["toy"]["litmus_gate"] = "maybe"
        with self.assertRaises(InputError):
            synthesize_results(data)

    def test_boolean_litmus_gate_is_accepted(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        data["tool"]["litmus_gate"] = True
        self.assertEqual(synthesize_results(data)["litmus_gates"]["tool"], "Yes")

    def test_missing_auditor_raises(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        del data["toy"]
        with self.assertRaises(InputError) as ctx:
            synthesize_results(data)
        self.assertIn("toy", str(ctx.exception))

    def test_missing_total_score_raises(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        del data["trash"]["total_score"]
        with self.assertRaises(InputError):
            synthesize_results(data)

    def test_out_of_range_score_raises(self):
        """A Trash total of 40 is legal; the same 40 on the 33-point Tool scale is not."""
        synthesize_results(reports(20, "No", 20, "No", 40, "No"))  # fine
        with self.assertRaises(InputError) as ctx:
            synthesize_results(reports(40, "No", 20, "No", 20, "No"))
        self.assertIn("0-33", str(ctx.exception))

    def test_negative_score_raises(self):
        with self.assertRaises(InputError):
            synthesize_results(reports(-1, "No", 20, "No", 20, "No"))

    def test_non_integer_score_raises(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        data["tool"]["total_score"] = "26"
        with self.assertRaises(InputError):
            synthesize_results(data)

    def test_non_list_critical_issues_raises(self):
        data = reports(26, "Yes", 12, "No", 21, "Yes")
        data["trash"]["critical_issues"] = "Triggered: Core Flaw."
        with self.assertRaises(InputError):
            synthesize_results(data)


class TestBoundaries(unittest.TestCase):
    """Every threshold in the spec, checked on both sides."""

    def test_all_zero(self):
        result = synthesize_results(reports(0, "No", 0, "No", 0, "No"))
        c = result["classification"]
        self.assertEqual(result["scores"]["composite"], 0.0)
        self.assertTrue(c["gray_zone"])
        self.assertEqual(c["primary"], "Tool")

    def test_all_maximum(self):
        result = synthesize_results(reports(33, "Yes", 33, "Yes", 42, "Yes"))
        s = result["scores"]
        self.assertEqual(s["composite"], 0.0)
        self.assertEqual(s["tool_normalized"], 100.0)
        self.assertEqual(s["trash_normalized"], 100.0)

    def test_20_point_gap_is_exclusive(self):
        """'Tool > Toy + 20' is strictly greater, so an exact 20-point gap fails."""
        # Tool 33 = 100.0, Toy 26.4/33... use raw values that land exactly 20 apart:
        # Tool 33/33 = 100.0, Toy 26/33 = 78.8 -> gap 21.2 (passes)
        # Tool 33/33 = 100.0, Toy 27/33 = 81.8 -> gap 18.2 (fails)
        gap_over = classify(100.0, 78.8, 0.0, False, False, False, [])
        gap_under = classify(100.0, 81.8, 0.0, False, False, False, [])
        self.assertEqual(gap_over["condition_counts"]["tool"], 3)
        self.assertEqual(gap_under["condition_counts"]["tool"], 2)

    def test_75_threshold_is_inclusive(self):
        self.assertEqual(classify(75.0, 0, 0, False, False, False, [])["condition_counts"]["tool"], 3)
        self.assertEqual(classify(74.9, 0, 0, False, False, False, [])["condition_counts"]["tool"], 2)

    def test_60_trash_threshold_is_inclusive(self):
        self.assertEqual(classify(0, 0, 60.0, False, False, False, [])["condition_counts"]["trash"], 3)
        self.assertEqual(classify(0, 0, 59.9, False, False, False, [])["condition_counts"]["trash"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
