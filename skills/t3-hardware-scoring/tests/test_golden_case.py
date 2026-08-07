#!/usr/bin/env python3
"""
End-to-end test over the golden fixture in fixtures/golden-ai-pendant/.

The fixture is a complete worked audit of a fictional product: the
Brand-Blinded source text, the three auditor reports a correct run produces,
and the classification they should synthesize to.

It exists for two jobs:

  1. **Regression test.** Steps 3.5 -> 5 are pure functions of the auditor JSON,
     so they can be pinned exactly.
  2. **Reference output.** It is the one place in the skill that shows what a
     finished, internally consistent auditor report actually looks like — the
     rubric guides only show fragments with "..." placeholders.

The strongest check here is `test_every_quote_exists_in_the_source_text`. The
skill's central claim is zero hallucination: every score traces to a verbatim
quote. That claim is mechanically checkable, and this is where it gets checked.
"""

import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from synthesize_results import synthesize_results  # noqa: E402
from validate_auditor_json import build_merged, validate  # noqa: E402

GOLDEN = os.path.join(HERE, "fixtures", "golden-ai-pendant")
ROLES = ("tool", "toy", "trash")


def load_json(name):
    with open(os.path.join(GOLDEN, name), encoding="utf-8") as f:
        return json.load(f)


def squash(text):
    """Collapse all whitespace so a quote still matches across a wrapped line."""
    return re.sub(r"\s+", " ", text).strip()


class GoldenCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.docs = {role: load_json(f"03-{role}-auditor.json") for role in ROLES}
        cls.expected = load_json("expected-synthesis.json")
        with open(os.path.join(GOLDEN, "02-brand-blinded.md"), encoding="utf-8") as f:
            cls.source = squash(f.read())

    # ── Step 3: auditor reports ──────────────────────────────────────────────

    def test_all_three_reports_are_internally_consistent(self):
        for role in ROLES:
            rep = validate(self.docs[role], role, role)
            self.assertEqual(rep.errors, [], f"{role} errors: {rep.errors}")
            self.assertEqual(rep.warnings, [], f"{role} warnings: {rep.warnings}")

    def test_every_quote_exists_in_the_source_text(self):
        """
        Zero hallucination, checked rather than asserted: every string in every
        verbatim_evidence array must appear in 02-brand-blinded.md.
        """
        checked = 0
        for role in ROLES:
            for section_name, section in self.docs[role]["checklist_items"].items():
                for item_id, item in section["items"].items():
                    for quote in item["verbatim_evidence"]:
                        checked += 1
                        self.assertIn(
                            squash(quote), self.source,
                            f"{role} item {item_id} in {section_name!r} cites a quote "
                            f"that is not in 02-brand-blinded.md: {quote!r}",
                        )
        self.assertGreater(checked, 20, "fixture should exercise a realistic quote count")

    def test_auditors_saw_only_the_brand_blinded_text(self):
        """Information Isolation: no auditor may leak an un-blinded identifier."""
        for role in ROLES:
            blob = json.dumps(self.docs[role])
            self.assertTrue(self.docs[role]["information_isolation_confirmed"])
            for leaked in ("MantaBase", "http://", "https://"):
                self.assertNotIn(leaked, blob, f"{role} report leaked {leaked!r}")

    def test_eagle_eye_triggers_are_the_five_expected_patterns(self):
        issues = " ".join(self.docs["trash"]["critical_issues"])
        for pattern in ("Core Flaw", "Privacy Tension", "Price vs. Doubt",
                        "Subscription Trap", "App Redundancy"):
            self.assertIn(pattern, issues)
        self.assertEqual(len(self.docs["trash"]["critical_issues"]),
                         self.expected["eagle_eye_trigger_count"])

    # ── Step 3.5: merge ──────────────────────────────────────────────────────

    def test_merge_matches_the_committed_auditor_reports(self):
        """The committed auditor_reports.json must be reproducible from the sources."""
        self.assertEqual(build_merged(self.docs), load_json("auditor_reports.json"))

    # ── Step 5: synthesis ────────────────────────────────────────────────────

    def test_synthesis_matches_expected(self):
        result = synthesize_results(build_merged(self.docs))

        for key, want in self.expected["scores"].items():
            self.assertEqual(result["scores"][key], want, f"scores.{key}")

        self.assertEqual(result["litmus_gates"], self.expected["litmus_gates"])

        for key, want in self.expected["classification"].items():
            self.assertEqual(result["classification"][key], want, f"classification.{key}")

    def test_verdict_names_the_veto(self):
        verdict = synthesize_results(build_merged(self.docs))["final_verdict_summary"]
        self.assertIn("Eagle Eye Veto activated", verdict)

    def test_a_polished_product_still_lands_in_trash(self):
        """
        The point of the whole architecture: strong Toy signals (machined
        aluminium, four colourways, a fidget-worthy clasp — enough to pass the
        Toy litmus gate) do not rescue a product whose core feature does not work.
        """
        result = synthesize_results(build_merged(self.docs))
        self.assertEqual(result["litmus_gates"]["toy"], "Yes")
        self.assertEqual(result["classification"]["primary"], "Trash")


if __name__ == "__main__":
    unittest.main(verbosity=2)
