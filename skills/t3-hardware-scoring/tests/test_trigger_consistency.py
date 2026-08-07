#!/usr/bin/env python3
"""
Keep the Eagle Eye trigger set consistent across every file that lists it.

Four documents and one script all enumerate the triggers, and they had drifted
apart: trash-auditor.md listed 5 patterns, eagle-eye-validator.md claimed "the 6
canonical" triggers (omitting Core Flaw, which the auditor guide *did* list),
and trash-red-flags.md defined 14. An auditor reading one file scored against a
different trigger set than the validator reviewing its work.

Duplication here is deliberate — an auditor subagent reads one rubric file and
should not have to open a second to know what fires. So the fix is not to
de-duplicate the tables, it is to pin them to one canonical source and fail the
build when a copy drifts.

Canonical source: references/trash-red-flags.md, "Canonical Trigger Index".
"""

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
REFS = os.path.join(SKILL_DIR, "references")

sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

from validate_auditor_json import (  # noqa: E402
    EAGLE_EYE_ITEMS,
    EAGLE_EYE_PATTERNS,
    trigger_pattern,
)

CANONICAL_FILE = "trash-red-flags.md"

# Every file that reproduces the trigger table, and the heading its copy lives
# under. A new file listing triggers should be added here.
COPIES = {
    "trash-auditor.md": "Eagle Eye: High-Sensitivity Trigger Checklist",
    "trash-auditor-template.md": "Eagle Eye Trigger Quick Reference",
    "eagle-eye-validator.md": "Missed Trigger Spot-check",
}

ITEM_ID = re.compile(r"^\d\.\d$")


def read(name):
    with open(os.path.join(REFS, name), encoding="utf-8") as f:
        return f.read()


def parse_trigger_rows(text):
    """
    Pull {pattern: item} out of every markdown table row shaped
    `| **Pattern** | 1.5 | ... |`.

    Keying off the bold-name + item-id shape means prose tables elsewhere in the
    file are ignored without needing to track section boundaries.
    """
    found = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip()
        if not (name.startswith("**") and name.endswith("**")):
            continue
        item = cells[1].strip()
        if not ITEM_ID.match(item):
            continue
        found.setdefault(name[2:-2].strip(), item)
    return found


def section(text, heading):
    """Return the body of the section whose heading contains `heading`."""
    lines = text.splitlines()
    start = None
    level = 0
    for i, line in enumerate(lines):
        if line.startswith("#") and heading in line:
            start = i + 1
            level = len(line) - len(line.lstrip("#"))
            break
    if start is None:
        raise AssertionError(f"heading not found: {heading!r}")
    for j in range(start, len(lines)):
        stripped = lines[j]
        if stripped.startswith("#"):
            if len(stripped) - len(stripped.lstrip("#")) <= level:
                return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


def canonical():
    body = section(read(CANONICAL_FILE), "Canonical Trigger Index")
    return parse_trigger_rows(body)


class TestCanonicalIndex(unittest.TestCase):

    def setUp(self):
        self.index = canonical()

    def test_index_is_non_trivial(self):
        self.assertGreaterEqual(len(self.index), 10,
                                "canonical index failed to parse — check the table format")

    def test_every_item_id_is_a_real_trash_rubric_item(self):
        trash_items = {"1.1", "1.2", "1.3", "1.4", "1.5", "1.6",
                       "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "4.1", "4.2"}
        for pattern, item in self.index.items():
            self.assertIn(item, trash_items, f"{pattern} points at unknown item {item}")

    def test_every_indexed_pattern_has_a_detail_row(self):
        """The index must not promise a pattern the file never specifies."""
        detail = parse_trigger_rows(read(CANONICAL_FILE))
        for pattern, item in self.index.items():
            self.assertIn(pattern, detail, f"{pattern} is indexed but has no detail row")
            self.assertEqual(detail[pattern], item,
                             f"{pattern}: index says item {item}, detail row disagrees")

    def test_stated_count_matches_the_table(self):
        """The prose says how many patterns there are; keep it honest."""
        text = read(CANONICAL_FILE)
        self.assertIn(f"{len(self.index)} patterns", text)


class TestCopiesMatchCanonical(unittest.TestCase):
    """Each reproduced table must list the same patterns against the same items."""

    def setUp(self):
        self.index = canonical()

    def test_each_copy_is_identical_to_the_index(self):
        for filename, heading in COPIES.items():
            with self.subTest(file=filename):
                copy = parse_trigger_rows(section(read(filename), heading))

                missing = sorted(set(self.index) - set(copy))
                self.assertEqual(missing, [], f"{filename} is missing: {missing}")

                extra = sorted(set(copy) - set(self.index))
                self.assertEqual(extra, [],
                                 f"{filename} lists patterns not in {CANONICAL_FILE}: {extra}")

                for pattern, item in self.index.items():
                    self.assertEqual(
                        copy[pattern], item,
                        f"{filename}: {pattern} mapped to item {copy[pattern]}, "
                        f"canonical says {item}",
                    )

    def test_no_copy_understates_the_trigger_count(self):
        """
        The specific regression: eagle-eye-validator.md said "the 6 canonical
        Eagle Eye triggers" while the auditor scored against 14.
        """
        for filename in COPIES:
            text = read(filename)
            for stale in re.findall(r"\b(\d+)\s+canonical", text):
                self.assertEqual(int(stale), len(self.index),
                                 f"{filename} claims {stale} canonical triggers, "
                                 f"but there are {len(self.index)}")


class TestCodeMatchesDocs(unittest.TestCase):
    """
    validate_auditor_json.py checks that a "Triggered:" reason names a real
    pattern on the right item. Its table has to track the canonical index.
    """

    def test_pattern_table_matches_the_canonical_index(self):
        index = canonical()
        self.assertEqual(
            EAGLE_EYE_PATTERNS, index,
            "EAGLE_EYE_PATTERNS in validate_auditor_json.py disagrees with "
            f"{CANONICAL_FILE}: "
            f"only in code {sorted(set(EAGLE_EYE_PATTERNS) - set(index))}, "
            f"only in docs {sorted(set(index) - set(EAGLE_EYE_PATTERNS))}",
        )

    def test_eagle_eye_items_match_the_canonical_index(self):
        documented = set(canonical().values())
        self.assertEqual(EAGLE_EYE_ITEMS, documented)

    def test_pattern_names_containing_periods_parse_correctly(self):
        """
        Reasons are formatted "Triggered: <Pattern>. <detail>", and three
        pattern names contain a period themselves. Splitting on the first
        period yields "Price vs", not "Price vs. Doubt".
        """
        self.assertEqual(
            trigger_pattern("Triggered: Price vs. Doubt. $329, accuracy unproven."),
            "Price vs. Doubt",
        )
        self.assertEqual(
            trigger_pattern("Triggered: Promise vs. Delivery. Buyers call it a scam."),
            "Promise vs. Delivery",
        )

    def test_every_canonical_name_round_trips(self):
        for name in EAGLE_EYE_PATTERNS:
            self.assertEqual(trigger_pattern(f"Triggered: {name}. Some detail."), name,
                             f"{name!r} does not parse back out of a reason string")

    def test_unknown_pattern_name_yields_nothing(self):
        self.assertEqual(trigger_pattern("Triggered: Vibes Are Off. Just a feeling."), "")

    def test_no_pattern_name_is_a_prefix_of_another(self):
        """
        trigger_pattern() matches longest-first so a future name cannot be
        shadowed by a shorter one. Today no name is a prefix of another, which
        is what keeps that ordering merely defensive — assert it stays that way,
        because a collision would make the parse order load-bearing and silent.
        """
        collisions = [(a, b) for a in EAGLE_EYE_PATTERNS for b in EAGLE_EYE_PATTERNS
                      if a != b and b.lower().startswith(a.lower())]
        self.assertEqual(collisions, [],
                         "one pattern name prefixes another; trigger_pattern() would "
                         "depend on match order")


class TestGoldenFixtureUsesRealPatterns(unittest.TestCase):
    """A fixture citing an invented pattern name would teach the wrong vocabulary."""

    def test_fixture_triggers_are_canonical_and_land_on_the_right_items(self):
        import json
        path = os.path.join(HERE, "fixtures", "golden-ai-pendant", "03-trash-auditor.json")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)

        index = canonical()
        seen = 0
        for sect in doc["checklist_items"].values():
            for item_id, item in sect["items"].items():
                reason = item.get("reason", "")
                if not re.match(r"\s*Triggered:", reason):
                    continue
                seen += 1
                pattern = trigger_pattern(reason)
                self.assertTrue(pattern,
                                f"item {item_id} cites no canonical pattern: {reason!r}")
                self.assertEqual(index[pattern], item_id,
                                 f"{pattern} belongs to item {index[pattern]}, "
                                 f"but the fixture triggers it on {item_id}")
        self.assertGreater(seen, 0, "fixture should exercise at least one trigger")

    def test_critical_issues_also_name_canonical_patterns(self):
        import json
        path = os.path.join(HERE, "fixtures", "golden-ai-pendant", "03-trash-auditor.json")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        for issue in doc["critical_issues"]:
            self.assertTrue(trigger_pattern(issue),
                            f"critical_issues entry names no canonical pattern: {issue!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
