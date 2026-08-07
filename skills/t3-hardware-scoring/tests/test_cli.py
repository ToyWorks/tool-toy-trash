#!/usr/bin/env python3
"""
CLI behaviour: exit codes, stdout/stderr split, and file output.

The skill drives these scripts as shell commands, so the exit code *is* the
signal. A validator that prints "ERROR" and exits 0 gets ignored by every
`&&` chain and every agent checking whether a step succeeded — which is how
the old silent litmus_gate default stayed invisible.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL_DIR, "scripts")
GOLDEN = os.path.join(HERE, "fixtures", "golden-ai-pendant")

SYNTH = os.path.join(SCRIPTS, "synthesize_results.py")
VALIDATE = os.path.join(SCRIPTS, "validate_auditor_json.py")


def run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


class CLITestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def path(self, name):
        return os.path.join(self.tmp, name)

    def write(self, name, payload):
        p = self.path(name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        return p

    def load_fixture(self, role):
        with open(os.path.join(GOLDEN, f"03-{role}-auditor.json"), encoding="utf-8") as f:
            return json.load(f)


class TestSynthesizeCLI(CLITestCase):

    def reports(self, **overrides):
        data = {
            "tool": {"total_score": 26, "litmus_gate": "Yes", "extract_for_report": {}},
            "toy": {"total_score": 12, "litmus_gate": "No", "extract_for_report": {}},
            "trash": {"total_score": 21, "litmus_gate": "Yes",
                      "critical_issues": [], "extract_for_report": {}},
        }
        data.update(overrides)
        return data

    def test_valid_input_exits_zero_and_emits_json(self):
        p = self.write("ok.json", self.reports())
        r = run(SYNTH, "--input", p)
        self.assertEqual(r.returncode, 0, r.stderr)
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["classification"]["final_label"], "Tool + Trash")

    def test_text_mode_exits_zero(self):
        p = self.write("ok.json", self.reports())
        r = run(SYNTH, "--input", p, "--text")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("T3 AUDIT SYNTHESIS", r.stdout)

    def test_missing_litmus_gate_exits_nonzero(self):
        data = self.reports()
        del data["tool"]["litmus_gate"]
        p = self.write("bad.json", data)
        r = run(SYNTH, "--input", p)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("litmus_gate", r.stderr)
        self.assertEqual(r.stdout.strip(), "",
                         "a failed run must not emit a result on stdout")

    def test_out_of_range_score_exits_nonzero(self):
        data = self.reports()
        data["tool"]["total_score"] = 99
        p = self.write("bad.json", data)
        self.assertNotEqual(run(SYNTH, "--input", p).returncode, 0)

    def test_missing_file_exits_nonzero(self):
        r = run(SYNTH, "--input", self.path("nope.json"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not found", r.stderr)

    def test_malformed_json_exits_nonzero(self):
        p = self.path("broken.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write("{not json")
        r = run(SYNTH, "--input", p)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("invalid JSON", r.stderr)

    def test_json_array_input_is_rejected(self):
        p = self.path("arr.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)
        self.assertNotEqual(run(SYNTH, "--input", p).returncode, 0)

    def test_output_flag_writes_a_parseable_file(self):
        p = self.write("ok.json", self.reports())
        out = self.path("result.json")
        r = run(SYNTH, "--input", p, "--text", "--output", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, encoding="utf-8") as f:
            saved = json.load(f)
        self.assertIn("classification", saved)
        self.assertIn("display_label", saved["classification"])


class TestValidateCLI(CLITestCase):

    def test_clean_report_exits_zero(self):
        for role in ("tool", "toy", "trash"):
            src = os.path.join(GOLDEN, f"03-{role}-auditor.json")
            r = run(VALIDATE, "validate", "--role", role, src)
            self.assertEqual(r.returncode, 0, f"{role}: {r.stdout}{r.stderr}")

    def test_bad_arithmetic_exits_nonzero(self):
        doc = self.load_fixture("trash")
        doc["total_score"] += 1
        p = self.write("bad.json", doc)
        r = run(VALIDATE, "validate", "--role", "trash", p)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ERROR", r.stdout)

    def test_wrong_role_exits_nonzero(self):
        p = os.path.join(GOLDEN, "03-trash-auditor.json")
        self.assertNotEqual(run(VALIDATE, "validate", "--role", "tool", p).returncode, 0)

    def test_unknown_role_is_a_usage_error(self):
        p = os.path.join(GOLDEN, "03-tool-auditor.json")
        self.assertNotEqual(run(VALIDATE, "validate", "--role", "banana", p).returncode, 0)

    def test_missing_file_exits_two(self):
        r = run(VALIDATE, "validate", "--role", "tool", self.path("nope.json"))
        self.assertEqual(r.returncode, 2, "unreadable input should be distinguishable")

    def test_strict_promotes_warnings_to_failure(self):
        doc = self.load_fixture("tool")
        # Four quotes on a score-2 item: a warning, not an error.
        for section in doc["checklist_items"].values():
            for item in section["items"].values():
                if item["score"] == 2:
                    item["verbatim_evidence"] = ["a", "b", "c", "d"]
                    break
            else:
                continue
            break
        p = self.write("warny.json", doc)
        self.assertEqual(run(VALIDATE, "validate", "--role", "tool", p).returncode, 0)
        self.assertNotEqual(
            run(VALIDATE, "validate", "--role", "tool", p, "--strict").returncode, 0)

    def test_merge_writes_only_after_all_three_validate(self):
        doc = self.load_fixture("trash")
        doc["total_score"] += 1
        bad = self.write("bad-trash.json", doc)
        out = self.path("merged.json")

        r = run(VALIDATE, "merge",
                "--tool", os.path.join(GOLDEN, "03-tool-auditor.json"),
                "--toy", os.path.join(GOLDEN, "03-toy-auditor.json"),
                "--trash", bad, "--output", out)

        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Refusing to merge", r.stderr)
        self.assertFalse(os.path.exists(out),
                         "a refused merge must not leave a partial output file")

    def test_merge_to_stdout_is_valid_json(self):
        r = run(VALIDATE, "merge",
                "--tool", os.path.join(GOLDEN, "03-tool-auditor.json"),
                "--toy", os.path.join(GOLDEN, "03-toy-auditor.json"),
                "--trash", os.path.join(GOLDEN, "03-trash-auditor.json"))
        self.assertEqual(r.returncode, 0, r.stderr)
        merged = json.loads(r.stdout)
        self.assertEqual(set(merged), {"tool", "toy", "trash"})

    def test_merge_output_feeds_the_synthesizer_directly(self):
        """The two scripts have to compose — that is the whole Step 3.5 -> 5 path."""
        out = self.path("merged.json")
        r = run(VALIDATE, "merge",
                "--tool", os.path.join(GOLDEN, "03-tool-auditor.json"),
                "--toy", os.path.join(GOLDEN, "03-toy-auditor.json"),
                "--trash", os.path.join(GOLDEN, "03-trash-auditor.json"),
                "--output", out)
        self.assertEqual(r.returncode, 0, r.stderr)

        r2 = run(SYNTH, "--input", out)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(
            json.loads(r2.stdout)["classification"]["display_label"],
            "Trash (Eagle Eye)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
