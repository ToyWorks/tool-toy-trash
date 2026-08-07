#!/usr/bin/env python3
"""
Repo-level consistency: the things that describe the skill must describe the
skill that actually exists.

The recurring failure in this repo has been metadata drifting away from
reality — a README pointing at scripts that were never committed, a rubric
guide citing a template file that does not exist, a version number nobody
bumped. Each is invisible until someone tries to use it.
"""

import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))

sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

import synthesize_results  # noqa: E402
from validate_auditor_json import ROLES  # noqa: E402


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def skill_frontmatter():
    text = read(os.path.join(SKILL_DIR, "SKILL.md"))
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "SKILL.md has no YAML frontmatter block"
    return match.group(1)


def frontmatter_value(key):
    """Minimal scalar lookup — avoids a PyYAML dependency for two fields."""
    for line in skill_frontmatter().splitlines():
        m = re.match(rf"^{re.escape(key)}:\s*(.+)$", line.strip())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    return None


class TestSkillFrontmatter(unittest.TestCase):

    def test_name_matches_the_directory(self):
        self.assertEqual(frontmatter_value("name"), os.path.basename(SKILL_DIR))

    def test_description_exists_and_is_substantive(self):
        """
        The description is what an agent matches on to decide whether to load
        the skill. A vague one means it never triggers.
        """
        text = skill_frontmatter()
        self.assertIn("description:", text)
        body = text.split("description:", 1)[1].split("\nmetadata:")[0]
        self.assertGreater(len(body.strip()), 120,
                           "description is too thin to trigger reliably")
        self.assertIn("Use when", body,
                      "description should say when to use the skill, not just what it is")

    def test_declares_no_python_dependencies(self):
        """
        Both scripts are stdlib-only so the skill installs with no Python
        environment. A reinstated dependency block should be a deliberate choice.
        """
        self.assertNotIn("dependency:", skill_frontmatter())

    def test_scripts_import_nothing_third_party(self):
        # Parse the AST rather than grepping: prose lines that begin "from a
        # source file..." inside a docstring look exactly like an import.
        import ast
        stdlib_ok = {
            "argparse", "json", "os", "re", "sys", "unittest", "copy",
            "typing", "importlib", "collections", "itertools", "math", "ast",
        }
        scripts = os.path.join(SKILL_DIR, "scripts")
        for name in sorted(os.listdir(scripts)):
            if not name.endswith(".py"):
                continue
            tree = ast.parse(read(os.path.join(scripts, name)), filename=name)
            for node in ast.walk(tree):
                roots = []
                if isinstance(node, ast.Import):
                    roots = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    roots = [node.module.split(".")[0]]
                for root in roots:
                    self.assertIn(root, stdlib_ok,
                                  f"{name} imports non-stdlib module {root!r}")


class TestVersionsAgree(unittest.TestCase):
    """One version number, stated in several places."""

    def setUp(self):
        self.version = frontmatter_value("version")

    def test_frontmatter_declares_a_version(self):
        self.assertRegex(self.version or "", r"^\d+\.\d+$")

    def test_skill_body_heading_matches_frontmatter(self):
        body = read(os.path.join(SKILL_DIR, "SKILL.md"))
        h1 = next((l for l in body.splitlines() if l.startswith("# ")), "")
        self.assertIn(f"v{self.version}", h1,
                      f"the H1 in SKILL.md ({h1!r}) should carry the frontmatter version")

    def test_synthesizer_banner_matches_frontmatter(self):
        """The text report prints a version; it should not lag the skill."""
        banner = synthesize_results.render_text({
            "scores": {"tool_raw": 0, "tool_max": 33, "tool_normalized": 0.0,
                       "toy_raw": 0, "toy_max": 33, "toy_normalized": 0.0,
                       "trash_raw": 0, "trash_max": 42, "trash_normalized": 0.0,
                       "composite": 0.0},
            "litmus_gates": {"tool": "No", "toy": "No", "trash": "No"},
            "classification": {"display_label": "Tool", "confidence": "Low",
                               "gray_zone": False, "eagle_eye_veto_activated": False},
            "final_verdict_summary": "",
        })
        self.assertIn(f"v{self.version}", banner)


class TestMarketplaceMatchesRepo(unittest.TestCase):
    """`/plugin marketplace add` reads this file; a stale path is a failed install."""

    def setUp(self):
        path = os.path.join(REPO_ROOT, ".claude-plugin", "marketplace.json")
        if not os.path.exists(path):
            self.skipTest("no .claude-plugin/marketplace.json in this repo")
        self.data = json.loads(read(path))

    def test_required_top_level_fields(self):
        for key in ("name", "owner", "plugins"):
            self.assertIn(key, self.data)
        self.assertIn("name", self.data["owner"])
        self.assertTrue(self.data["plugins"])

    def test_every_listed_skill_path_exists_and_has_a_skill_md(self):
        for plugin in self.data["plugins"]:
            for rel in plugin.get("skills", []):
                skill_path = os.path.normpath(os.path.join(REPO_ROOT, rel))
                self.assertTrue(os.path.isdir(skill_path),
                                f"{plugin['name']}: no such directory {rel}")
                self.assertTrue(os.path.isfile(os.path.join(skill_path, "SKILL.md")),
                                f"{rel} has no SKILL.md")

    def test_every_skill_in_the_repo_is_published(self):
        """A skill nobody can install is a skill nobody uses."""
        skills_dir = os.path.join(REPO_ROOT, "skills")
        on_disk = {d for d in os.listdir(skills_dir)
                   if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))}
        listed = {os.path.basename(rel.rstrip("/"))
                  for plugin in self.data["plugins"]
                  for rel in plugin.get("skills", [])}
        self.assertEqual(on_disk - listed, set(),
                         "skills present on disk but absent from marketplace.json")

    def test_readme_lists_every_skill(self):
        readme = read(os.path.join(REPO_ROOT, "README.md"))
        skills_dir = os.path.join(REPO_ROOT, "skills")
        for name in os.listdir(skills_dir):
            if os.path.isfile(os.path.join(skills_dir, name, "SKILL.md")):
                self.assertIn(name, readme, f"{name} is missing from the README table")


class TestAuditorTemplates(unittest.TestCase):
    """
    The `*-template.md` JSON blocks are what an auditor subagent copies and
    fills in. If one is malformed, or drops a rubric item, the auditor emits
    malformed or incomplete JSON — and the item it never scored is simply gone.

    The prose `*-auditor.md` guides are exempt: their JSON deliberately contains
    `{...}` illustrations and is read, not copied.
    """

    ROLE_FILES = {
        "tool": "tool-auditor-template.md",
        "toy": "toy-auditor-template.md",
        "trash": "trash-auditor-template.md",
    }

    def template(self, role):
        text = read(os.path.join(SKILL_DIR, "references", self.ROLE_FILES[role]))
        blocks = re.findall(r"```json\n(.*?)```", text, re.S)
        self.assertEqual(len(blocks), 1,
                         f"{self.ROLE_FILES[role]} should hold exactly one JSON template")
        return text, json.loads(blocks[0])

    def test_each_template_is_valid_json(self):
        for role in self.ROLE_FILES:
            with self.subTest(role=role):
                self.template(role)  # json.loads raises on failure

    def test_template_items_match_the_rubric_exactly(self):
        for role, contract in ROLES.items():
            with self.subTest(role=role):
                _, doc = self.template(role)
                ids = {i for section in doc["checklist_items"].values()
                       for i in section["items"]}
                self.assertEqual(ids, set(contract["items"]),
                                 f"{self.ROLE_FILES[role]} item IDs drifted from the rubric")

    def test_template_declares_the_fields_the_scripts_read(self):
        for role, contract in ROLES.items():
            with self.subTest(role=role):
                _, doc = self.template(role)
                self.assertIn("litmus_gate", doc,
                              "the field synthesize_results.py reads must be in the template")
                self.assertIn(doc["litmus_gate"], ("Yes", "No"))
                self.assertEqual(doc["total_score"], 0, "template should start at zero")
                self.assertEqual(doc["max_possible_score"], contract["max"])
                self.assertIn("extract_for_report", doc)
        _, trash = self.template("trash")
        self.assertEqual(trash["critical_issues"], [],
                         "the Trash template must ship the array that drives the veto")

    def test_scoring_table_rows_match_the_json_items(self):
        """Each template shows a table and a JSON block; they must agree."""
        for role, contract in ROLES.items():
            with self.subTest(role=role):
                text, _ = self.template(role)
                rows = set(re.findall(r"^\|\s*(\d\.\d)\s*\|", text, re.M))
                self.assertEqual(rows, set(contract["items"]),
                                 f"{self.ROLE_FILES[role]} table rows disagree with the rubric")

    def test_every_item_max_is_three(self):
        for role in ROLES:
            with self.subTest(role=role):
                _, doc = self.template(role)
                for section in doc["checklist_items"].values():
                    for item_id, item in section["items"].items():
                        self.assertEqual(item["max_score"], 3, f"item {item_id}")


class TestReportSchemaMatchesRubrics(unittest.TestCase):
    """
    report-schema.md hardcodes each chart dimension's maximum. Those numbers are
    a function of how many items sit in each rubric section, so they can silently
    stop being true when a rubric changes.
    """

    def setUp(self):
        self.schema = read(os.path.join(SKILL_DIR, "references", "report-schema.md"))

    def test_declared_role_maxima_match_the_rubrics(self):
        for role, contract in ROLES.items():
            total = contract["max"]
            self.assertIn(f"Always {total}", self.schema,
                          f"report-schema.md never states {role}_max = {total}")

    def test_chart_dimension_maxima_sum_to_the_role_maximum(self):
        """Every dimension list must add up to that role's total."""
        for role, expected in (("tool", 33), ("toy", 33), ("trash", 42)):
            line = next((l for l in self.schema.splitlines()
                         if l.strip().startswith(f"* **{role}**")), None)
            self.assertIsNotNone(line, f"no chart_data line for {role}")
            parts = [int(n) for n in re.findall(r"\((\d+)\)", line)]
            self.assertEqual(sum(parts), expected,
                             f"{role} chart dimensions {parts} sum to {sum(parts)}, "
                             f"expected {expected}")

    def test_schema_documents_both_label_fields(self):
        for field in ("final_label", "display_label"):
            self.assertIn(field, self.schema,
                          f"report-schema.md does not document {field}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
