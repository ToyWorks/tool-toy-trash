#!/usr/bin/env python3
"""
Check that every file the skill points at actually exists.

A dead reference is worse here than in ordinary docs: the agent is instructed to
"Read references/x.md" mid-run, and a missing file means it either stalls or
improvises the rubric. `references/trash-auditor.md` pointed at a
`trash-auditor-template.md` that was never committed.

Covers markdown links, and bare `path/file.md` / `path/file.py` mentions in
prose and code fences.

Run: python3 skills/t3-hardware-scoring/tests/check_links.py
"""

import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BARE_PATH = re.compile(r"(?:^|[\s`'\"(])((?:references|scripts|tests)/[\w./-]+\.(?:md|py|sh|json))")
SIBLING_MD = re.compile(r"`([\w-]+\.md)`")

# Files an audit *produces* at run time (01-level0-extracts.md, 02-brand-blinded.md,
# 99-audit-report.md, ...). They are named so the agent knows what to write, and
# are never committed to the skill.
RUNTIME_ARTIFACT = re.compile(r"^\d{2}(\.\d+)?-")


def markdown_files():
    for root, dirs, files in os.walk(SKILL_DIR):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(root, name)


def main() -> int:
    problems = []

    for path in sorted(markdown_files()):
        rel = os.path.relpath(path, SKILL_DIR)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        here = os.path.dirname(path)

        targets = set()

        for target in MD_LINK.findall(text):
            target = target.split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            targets.add((target, here))

        for target in BARE_PATH.findall(text):
            targets.add((target, SKILL_DIR))

        # `foo.md` written inside a references/ file means a sibling file.
        if os.path.basename(here) == "references":
            for target in SIBLING_MD.findall(text):
                targets.add((target, here))

        for target, base in sorted(targets):
            if RUNTIME_ARTIFACT.match(os.path.basename(target)):
                continue
            if not os.path.exists(os.path.join(base, target)):
                problems.append(f"{rel}: points at missing file -> {target}")

    if problems:
        print("Broken references:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    print("All skill references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
