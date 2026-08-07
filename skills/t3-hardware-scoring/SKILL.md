---
name: t3-hardware-scoring
description: >-
  Classify a hardware product as Tool, Toy, or Trash using the MantaBase T3 audit:
  Brand Blinding, three independent auditors scoring fixed rubrics from verbatim
  evidence, an Eagle Eye validation pass, and a Final Judge that applies a safety
  veto. Use when the user shares a product link, gadget, or crowdfunding page and
  asks whether it is worth it, whether it is any good, whether the claims hold up,
  or asks for a T3 audit, hardware evaluation, or product scoring.
metadata:
  version: "2.2"
---

# MantaBase T3 Hardware Audit System — v2.2

## Objectives
- Collect product information → Brand Blind → Triple-Auditor independent scoring → Eagle Eye Validation → Final Judge synthesis
- Output: objective Tool / Toy / Trash classification with Eagle Eye safety veto
- Core principles: evidence-first, parallel audits, zero hallucination, transparent math

## Architecture Overview

```
Main Agent                             Subagents
───────────────────────────────────    ──────────────────────────────
Step 1: Data Collection (web tools)
Step 2: Organize + Brand Blind
  ↓ write 02-brand-blinded.md
                                       Step 3: ×3 parallel (Tool/Toy/Trash)
                                         · read file paths, print JSON to stdout
                                         · main agent writes 03-*.json files
  ↓ receive JSON, write files
  ↓ Step 3.5: validate + merge (script)
                                       Step 4: ×1 Eagle Eye Validator (conditional)
                                         · AI subagent, not a Python script
                                         · outputs adjustments[] diff
  ↓ apply diffs, re-merge
Step 5: synthesize_results.py
Step 6: 99-audit-report.md
```

**Key v2.2 changes:**
- Step 1 uses the agent's own web tools; the bundled crawler is gone
- Step 3.5 is now a script (`validate_auditor_json.py`), not prose instructions
- Every auditor report is validated before it can reach the Final Judge
- Missing `litmus_gate` / bad totals are hard errors instead of silent defaults
- `final_label` stays parseable; `display_label` carries the annotations
- The skill ships a golden worked example and a test suite (`tests/`)

**No Python dependencies.** Both scripts are stdlib-only.

---

## Data Collection Strategy (Step 1-2)

Use whatever web capability the host agent has — `WebFetch` / `WebSearch`,
a browser tool, or an Exa/Firecrawl MCP if one is connected. Fetch the product
page directly and search for independent coverage. Do not shell out to a
bundled crawler: the host's fetcher already handles redirects, JS-rendered
pages, and rate limits far better than a bare `requests.get`, and it reads the
page into context in one step.

If no web capability is available, ask the user to paste the product page text
and any reviews, then continue from Step 2 unchanged. Everything downstream
operates on `02-brand-blinded.md`, not on how the text was obtained.

### Sources to gather (in order)
1. Official product page (specs, pricing, marketing claims — quote these verbatim)
2. Third-party hands-on reviews
3. Community discussion (Reddit, forums) for real-user pain points
4. Investigation/news coverage (privacy issues, lawsuits, controversies)

Collect at least **3 independent sources**. Save raw extracts to
`01-level0-extracts.md` with source tags `[S1]`, `[S2]`, etc.

### Minimum data threshold
Proceed only when you have:
- [ ] At least one official source with **tech specs + price**
- [ ] At least one **third-party review** with hands-on findings
- [ ] Marketing claims verbatim (needed for the Eagle Eye Honest check)

### Pre-launch data flag
If the product meets ALL of the following, append `(Pre-launch)` to the case_id and skip Step 4:
- Zero independent hands-on reviews
- ≥3 critical specs undisclosed (battery, weight, connectivity, regulatory)
- Pre-order only / not shipping

---

## Procedure

### Step 1: Collect Raw Data
- Fetch the official product URL with the agent's web tools
- Search for independent reviews and community threads
- Save raw extracts to `01-level0-extracts.md` with source tags

### Step 2: Organize + Brand Blind (combined step)
- Read [references/organize-guide.md](references/organize-guide.md)
- Read [references/brand-blinding-guide.md](references/brand-blinding-guide.md)
- Merge all sources into one structured document
- Apply Brand Blinding inline (replace brand names with [BRAND], [PRODUCT], [FEATURE])
- **Preserve ALL adjectives and marketing claims verbatim** — needed by downstream auditors
- Brand-blinded text should be **≤ 1200 words** — deduplicate aggressively but keep all unique claims
- Save to `02-brand-blinded.md`

A complete example of a finished Brand-Blinded document is at
[tests/fixtures/golden-ai-pendant/02-brand-blinded.md](tests/fixtures/golden-ai-pendant/02-brand-blinded.md).

### Step 3: Triple Auditor Scoring (independent, parallel)

Each Auditor sees **only the Brand-Blinded text** from Step 2.

**Subagent execution rules (mandatory):**
- Pass the **file path** to `02-brand-blinded.md` — do NOT embed full text in the prompt
- Each subagent reads the file, reads their rubric file, and **prints JSON to stdout**
- **Main agent writes files** — subagents never call `write` (prevents timeout file loss)
- `verbatim_evidence` limits:
  - score 0–1: max **1** quote (or `[]` for score 0)
  - score 2–3: max **2** quotes
- Recommended timeouts: Tool=150s, Toy=150s, Trash=180s

#### 🟢 Tool Auditor
- Reads [references/tool-auditor.md](references/tool-auditor.md)
- Template: [references/tool-auditor-template.md](references/tool-auditor-template.md)
- Score 11 items (0-3 scale), max 33 points
- Output `litmus_gate: "Yes"/"No"` at top level

#### 🟡 Toy Auditor
- Reads [references/toy-auditor.md](references/toy-auditor.md)
- Template: [references/toy-auditor-template.md](references/toy-auditor-template.md)
- Score 11 items (0-3 scale), max 33 points
- Output `litmus_gate: "Yes"/"No"` at top level

#### 🔴 Trash Auditor
- Reads [references/trash-auditor.md](references/trash-auditor.md)
- Template: [references/trash-auditor-template.md](references/trash-auditor-template.md)
- Reads [references/trash-red-flags.md](references/trash-red-flags.md) (**required** for Eagle Eye)
- Score 14 items (0-3 scale), max 42 points
- Eagle Eye triggers → auto-set score to 3 for flagged items
- Output `litmus_gate: "Yes"/"No"` and `critical_issues: [...]` at top level

**Key principles:**
- Each auditor works from Brand-Blinded text only
- No cross-talk between auditors during scoring
- Evidence FIRST, then score — no score without a verbatim quote
- If a feature isn't in the text, it scores 0

Worked examples of all three finished reports are in
[tests/fixtures/golden-ai-pendant/](tests/fixtures/golden-ai-pendant/).

### Step 3.5: Validate and merge (mandatory)

```bash
python3 scripts/validate_auditor_json.py merge \
  --tool  03-tool-auditor.json \
  --toy   03-toy-auditor.json \
  --trash 03-trash-auditor.json \
  --output auditor_reports.json
```

This validates all three reports and refuses to merge if any check fails:

- every rubric item present (11 / 11 / 14) and scored within 0–3
- `total_score` equals the sum of its items; section subtotals match
- evidence-first: no score above 0 without a verbatim quote
- top-level `litmus_gate` present and consistent with the nested answer
- one `critical_issues` entry per `"Triggered:"` item

**🚨 Never hand-write `auditor_reports.json` from memory or a summary.** Every
value must be copied from a `03-*.json` file. That is what this command does —
if it reports an error, re-run the affected auditor rather than editing scores.

Individual reports can be checked as they arrive:

```bash
python3 scripts/validate_auditor_json.py validate --role trash 03-trash-auditor.json
```

### Step 4: Eagle Eye Validator (conditional, AI-driven)

Read [references/eagle-eye-validator.md](references/eagle-eye-validator.md)

**Trigger conditions** — run Step 4 if ANY is true:
- Trash report `critical_issues` is non-empty
- Any auditor has any item scored **3**
- Composite score is in the Gray Zone (-10 to +10)

Otherwise: skip directly to Step 5.

**Execution:**
- Spawn **1 subagent** (timeout: 120s)
- Subagent reads `02-brand-blinded.md` + only the flagged items from `03-*.json`
- Performs three checks:
  1. **Eagle Eye trigger validity** — do both conflicting quotes exist verbatim?
  2. **Architectural Plausibility** — are on-device/local claims technically feasible for the form factor?
  3. **Score=3 evidence check** — does the evidence actually support the 3-level rubric?
- Outputs an `adjustments[]` diff (not a full re-score)
- Main agent applies the diffs **to the `03-*.json` files**, then re-runs the
  Step 3.5 merge so the totals stay derived rather than patched

### Step 5: Final Judge Synthesis

```bash
python3 scripts/synthesize_results.py --input auditor_reports.json --text
```

Run the script — do not do this arithmetic by hand. The rules interact (four
primary conditions, two secondary tiers, a Gray Zone gate override, and the
veto), and both worked examples in
[references/t3-classification.md](references/t3-classification.md) previously
disagreed with the code. The script is the reference implementation; the tests
pin it to the spec.

Steps applied, per [references/t3-classification.md](references/t3-classification.md):
1. Normalize: Tool=(raw/33)×100, Toy=(raw/33)×100, Trash=(raw/42)×100
2. Composite = max(NormTool, NormToy) − NormTrash
3. Primary: the category meeting 2+ of its 4 conditions
4. Secondary: threshold tiers, plus the Gray Zone negative-composite rule
5. Eagle Eye Veto: `critical_issues` non-empty → Trash forced into the label,
   confidence forced to `Review Required`

### Step 6: Generate Audit Report

**Output file**: `99-audit-report.md`
**Directory**: `tmp/reports/t3-{YYYY-MM-DD}-{slug}/`

Follow the YAML schema in [references/report-schema.md](references/report-schema.md).
Use `final_label` for the YAML metadata and `display_label` in the prose.

---

## Output Format for Messaging Surfaces (WhatsApp / Telegram)

When delivering results in a chat interface, **do not paste the full file**.
Use this condensed format instead:

```
🏷️ T3 Audit — {Product Name}
Price: ${price} | Date: {YYYY-MM-DD}

📊 Scores
🟢 Tool:  {raw}/33 → {norm}/100
🟡 Toy:   {raw}/33 → {norm}/100
🔴 Trash: {raw}/42 → {norm}/100
Composite: {composite:+.1f}

🏆 Classification: {display_label}
Confidence: {confidence}

{If Eagle Eye:}
🚨 Eagle Eye: {trigger name}
"{verbatim quote A}"
vs.
"{verbatim quote B}"

🟢 Tool highlights (3 bullets)
🟡 Toy highlights (3 bullets)
🔴 Trash issues (3 bullets)

💬 One-line verdict
```

Rules for messaging output:
- No markdown tables (WhatsApp doesn't render them)
- Use **bold** for emphasis, bullet lists for details
- Keep the total message under 600 words
- If Eagle Eye triggered, always show the conflicting quotes

---

## Important Constraints

### 🚨 Information Isolation (critical)
- Brand-Blinded text is the ONLY input for auditors
- Auditors must never see original brand names, marketing copy, or each other's reports during scoring
- The Final Judge reads only the three auditor JSON outputs, not the original product text

### 📊 Objective data completeness
- Collect specs, performance, reliability, market, and cost data
- Brand Blinding must **retain** all specs and numbers
- Every score must link to extracted verbatim evidence

### Eagle Eye enforcement
- The Trash Auditor MUST check every item against [references/trash-red-flags.md](references/trash-red-flags.md)
- Eagle Eye trigger → automatic score 3 → populate `critical_issues[]`
- The Eagle Eye Validator (Step 4) re-checks triggers including **Architectural Plausibility**
- The Final Judge must respect the Eagle Eye Veto regardless of composite math

### synthesize_results.py input format
```json
{
  "tool":  { "total_score": <int 0-33>, "litmus_gate": "Yes|No", "extract_for_report": {...} },
  "toy":   { "total_score": <int 0-33>, "litmus_gate": "Yes|No", "extract_for_report": {...} },
  "trash": { "total_score": <int 0-42>, "litmus_gate": "Yes|No",
             "critical_issues": ["<eagle eye trigger text>", ...],
             "extract_for_report": {...} }
}
```

`litmus_gate` is **required** on all three. It is one of only four conditions
that decide the primary classification, so a missing gate is a wrong verdict,
not a smaller one. The script errors rather than defaulting it.

---

## Testing

```bash
tests/run_tests.sh
```

Runs the unit tests, the end-to-end golden case, and a CLI smoke test. Stdlib
Python only — no install step.

`tests/fixtures/golden-ai-pendant/` is a complete worked audit of a fictional
product: Brand-Blinded source text, all three auditor reports, and the
classification they synthesize to. It doubles as the reference for what a
finished, internally consistent auditor report looks like — the rubric guides
show only fragments.

One test worth knowing about: `test_every_quote_exists_in_the_source_text`
checks that every string in every `verbatim_evidence` array appears in
`02-brand-blinded.md`. The skill's central claim is zero hallucination, and
that makes it mechanically checkable rather than merely asserted.

`tests/test_trigger_consistency.py` pins the Eagle Eye trigger set. Four files
list the triggers, and an auditor subagent reads only one of them — so the
tables are deliberately duplicated, and pinned instead of de-duplicated. The
canonical index lives in
[references/trash-red-flags.md](references/trash-red-flags.md); add a pattern
there first, then propagate. The test fails if any copy — or the pattern table
in `validate_auditor_json.py` — drifts.

`tests/check_links.py` verifies that every file the skill tells the agent to
read actually exists — a dead reference mid-run means the agent improvises the
rubric.

| Test file | Covers |
|---|---|
| `test_synthesize.py` | Final Judge math: thresholds, Gray Zone, the veto, strict input |
| `test_validate.py` | Every rejection the Step 3.5 validator has to make |
| `test_golden_case.py` | Steps 3 → 5 end to end over the fixture |
| `test_trigger_consistency.py` | The Eagle Eye trigger set across four files and the code |
| `test_repo_consistency.py` | Frontmatter, versions, templates, marketplace, report schema |
| `test_cli.py` | Exit codes — the signal the skill's shell steps actually read |

---

## Resource Index

### Scripts
- `scripts/validate_auditor_json.py` — validate one auditor report, or validate + merge all three (Step 3.5)
- `scripts/synthesize_results.py` — Final Judge math (normalization + Eagle Eye + Litmus Gate)

### References
| File | Used In |
|------|---------|
| [organize-guide.md](references/organize-guide.md) | Step 2 |
| [brand-blinding-guide.md](references/brand-blinding-guide.md) | Step 2 |
| [tool-auditor.md](references/tool-auditor.md) | Step 3 |
| [tool-auditor-template.md](references/tool-auditor-template.md) | Step 3 |
| [toy-auditor.md](references/toy-auditor.md) | Step 3 |
| [toy-auditor-template.md](references/toy-auditor-template.md) | Step 3 |
| [trash-auditor.md](references/trash-auditor.md) | Step 3 |
| [trash-auditor-template.md](references/trash-auditor-template.md) | Step 3 |
| [trash-red-flags.md](references/trash-red-flags.md) | Step 3 (Eagle Eye) |
| [eagle-eye-validator.md](references/eagle-eye-validator.md) | Step 4 |
| [t3-classification.md](references/t3-classification.md) | Step 5 |
| [report-schema.md](references/report-schema.md) | Step 6 |
