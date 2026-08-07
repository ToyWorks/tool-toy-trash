# T3 Classification and Final Judge Guide

## T3 Classification Definition

### 🟢 Tool

**Core characteristic**: Solves real, well-defined problems with quantifiable efficiency.
**Key metrics**:

* **Practicality**: Solves documented pain points.
* **Reliability**: High stability, high uptime, unobtrusive.
* **Dependency**: If it fails, the user's workflow breaks or slows down significantly.

### 🟡 Toy

**Core characteristic**: Brings sensory pleasure, surprise, and emotional attachment.
**Key metrics**:

* **Fun/Aesthetics**: High CMF (Color, Material, Finish) satisfaction.
* **Surprise**: Exceeds expectations with non-functional positive experiences (Easter eggs, haptics).
* **Explorability**: Provides space for undirected exploration, modding, or customization.

### 🔴 Trash

**Core characteristic**: Violates design principles, creates friction, or acts as e-waste.
**Key metrics**:

* **Design violation**: Deceptive marketing, privacy risks, or physical flaws.
* **Problem creation**: Adds workflow steps rather than removing them.
* **Replaceability**: Easily replaced by a free smartphone app or a cheaper, simpler traditional tool.

## Litmus Logic Gates

Instead of subjective questions, the Final Judge reviews the boolean logic gates executed by the Auditors:

* **Tool Gate**: Did the data explicitly mention a measurable decrease in task completion time or direct workflow replacement? (Yes/No)
* **Toy Gate**: Did the data explicitly mention features designed for aesthetic display, deep personalization, or non-functional sensory delight? (Yes/No)
* **Trash Gate**: Did the data explicitly show the product causes more friction, expense, or privacy risk than the traditional alternative? (Yes/No)

## Final Judge Role & Information Isolation

### Core Responsibilities

The Final Judge is the **Supreme Arbiter**. It does not re-read the original product data to hunt for features. It makes its decision **strictly based on the extracted `verbatim_evidence`, raw scores, and `critical_issues**` provided by the three independent Auditor reports.

### Working Principles

1. **Evidence-Bound**: If an Auditor gave a high score but failed to extract valid `verbatim_evidence`, the Final Judge must discount that score.
2. **Apples-to-Apples Math**: Standardizes raw scores (out of 33 or 42) into a 100-point index.
3. **Veto Power**: Enforces the Eagle Eye triggers to prevent polished e-waste from being classified as a pure Tool or Toy.

## Score Normalization Protocol

Because the deterministic rubrics have different maximums, the Final Judge must normalize them to a 0–100 scale before calculating the Composite Score.

**Normalization Formulas:**

* **Normalized Tool Score** = `(Raw Tool Score / 33) * 100`
* **Normalized Toy Score** = `(Raw Toy Score / 33) * 100`
* **Normalized Trash Score** = `(Raw Trash Score / 42) * 100`

### Composite Score Calculation

```text
Composite Score = max(Normalized Tool, Normalized Toy) - Normalized Trash

```

*Range: -100 to 100*

**Score Interpretation**:

* **> 40**: Strong Tool/Toy bias
* **0 to 40**: Moderate Tool/Toy bias
* **-1 to -39**: Trash bias
* **< -40**: Strong Trash bias

## Classification Decision Logic

Using the **Normalized Scores (0-100)**, execute the following logic:

### Step 1: Determine Primary Classification

**Tool is Primary if** (satisfies 2+):

* Normalized Tool ≥ 75
* Normalized Tool > Normalized Toy + 20
* Normalized Tool > Normalized Trash + 20
* Tool Litmus Gate is "Yes"

**Toy is Primary if** (satisfies 2+):

* Normalized Toy ≥ 75
* Normalized Toy > Normalized Tool + 20
* Normalized Toy > Normalized Trash + 20
* Toy Litmus Gate is "Yes"

**Trash is Primary if** (satisfies 2+):

* Normalized Trash ≥ 60 (Lower threshold due to inverted severity)
* Normalized Trash > Normalized Tool + 20
* Normalized Trash > Normalized Toy + 20
* Trash Litmus Gate is "Yes"

### Step 2: Determine Secondary Classification

**If Tool is Primary**:

* Normalized Toy ≥ 60 → Secondary: Toy
* Normalized Trash ≥ 50 → Secondary: Trash

**If Toy is Primary**:

* Normalized Tool ≥ 60 → Secondary: Tool
* Normalized Trash ≥ 50 → Secondary: Trash

**If Trash is Primary**:

* Normalized Tool ≥ 50 → Secondary: Tool
* Normalized Toy ≥ 50 → Secondary: Toy

### Step 3: Gray Zone Handling (when no Primary is determined)

**Gray Zone** occurs when all three categories satisfy fewer than 2 conditions in Step 1.

This is a valid and common outcome for products that are genuinely ambiguous. Do not force a classification.

**Gray Zone Resolution Rules (execute in order — the first rule that applies wins):**

1. **Litmus Gate override**: If **exactly one** category passes its Litmus Gate, that
   category becomes Primary. In the Gray Zone no category has enough score evidence to
   stand on, so a single passing gate is the only positive signal available — it
   outranks the composite tiebreaker below.
   If zero or two-plus gates pass, fall through to rule 2.

2. **Composite Score tiebreaker**:
   - Composite > 0 → Primary = Tool (if NormTool ≥ NormToy) or Toy (if NormToy > NormTool)
   - Composite < 0 → Primary = Trash
   - Composite = 0 → whichever of Tool/Toy is higher; if equal, Tool wins

3. **Gray Zone secondary rule**: If the Composite is **negative**, "Trash" is always
   added as a Secondary — a negative composite means Trash outweighs the winner, even
   when NormTrash sits below the usual 50 threshold from Step 2.

4. **Confidence**: Always `"Low"` in Gray Zone, regardless of score spread
   (unless an Eagle Eye Veto fires, which forces `"Review Required"`).

5. **Verdict note**: The Final Verdict Summary must explicitly state the product is in a Gray Zone and explain which dimension pulled the classification.

**Gray Zone example**:
```
NormTool = 36.4  (conditions met: 0)
NormToy  = 36.4  (conditions met: 1 — Toy Litmus Gate Yes)
NormTrash = 47.6 (conditions met: 0)
Composite = -11.2

→ No category has 2+ conditions → Gray Zone.
→ Rule 1: exactly one gate passed (Toy) → Toy becomes Primary.
   (Rule 2 alone would have said Trash, on the negative composite.)
→ Rule 3: composite is negative → Trash is added as Secondary,
   even though NormTrash 47.6 misses the usual 50 threshold.
→ final_label: "Toy + Trash"  |  display_label: "Toy + Trash (Gray Zone)"
→ Confidence: Low
```

This example is pinned as a test in
[`../tests/test_synthesize.py`](../tests/test_synthesize.py) (`test_gray_zone_example`).

---

## Label Fields

Two labels are emitted, and they are not interchangeable:

| Field | Contents | Use for |
| --- | --- | --- |
| `final_label` | `Primary + Secondary` only, e.g. `Tool + Trash` | Leaderboards, YAML metadata, grouping, any parsing |
| `display_label` | `final_label` plus annotations, e.g. `Tool + Trash (Eagle Eye, Gray Zone)` | Reports, chat output, anything a human reads |

Keeping annotations out of `final_label` means a Gray Zone `Tool` and a confident
`Tool` still group together on the leaderboard, while the report still shows the
caveat. When both conditions hold, `display_label` names both — the older
single-suffix format dropped `(Gray Zone)` whenever Eagle Eye also fired.

---

## Eagle Eye Veto System

**CRITICAL OVERRIDE**: The Final Judge must check the `critical_issues` array from the Trash Auditor Report.

If the Trash Auditor flagged **ANY** Eagle Eye triggers (e.g., "Privacy Tension", "Core Flaw", "App Redundancy"), the Final Judge MUST apply the following overrides, regardless of the mathematical Composite Score:

1. **Mandatory Trash Label**: "Trash" must be appended to the classification (either as Primary or Secondary).
2. **Confidence Flag**: The `confidence` field must be marked as "Review Required".
3. **Reasoning Update**: The `decision_reasoning` must explicitly state that an Eagle Eye Veto was triggered by a specific fatal flaw.

## Assessment Report Format

### 🚨 Strict Output Template (Mandatory)

The Final Judge output must synthesize the normalized math, the logic gates, and the Eagle Eye veto into a final JSON structure.

```json
{
  "final_judge": {
    "timestamp": "2024-01-01T00:00:00Z",
    "information_source": "Three independent Brand-Blinded Auditor Reports",
    
    "score_normalization": {
      "tool": {
        "raw_score": 26,
        "max_raw": 33,
        "normalized_score": 78.8,
        "litmus_gate": "Yes"
      },
      "toy": {
        "raw_score": 12,
        "max_raw": 33,
        "normalized_score": 36.4,
        "litmus_gate": "No"
      },
      "trash": {
        "raw_score": 21,
        "max_raw": 42,
        "normalized_score": 50.0,
        "litmus_gate": "Yes",
        "critical_issues_flagged": ["Triggered Privacy Tension: Claims local but requires cloud sync."]
      }
    },
    
    "composite_metrics": {
      "calculation": "max(78.8, 36.4) - 50.0",
      "composite_score": 28.8,
      "eagle_eye_veto_activated": true
    },
    
    "classification": {
      "primary": "Tool",
      "secondary": ["Trash"],
      "final_label": "Tool + Trash",
      "display_label": "Tool + Trash (Eagle Eye)"
    },
    
    "decision_reasoning": {
      "primary_reason": "Normalized Tool score (78.8) is the highest and passes the Tool Litmus Gate.",
      "secondary_reason": "Trash Normalized score is 50.0, but Eagle Eye Veto was activated due to a critical privacy contradiction, forcing a secondary Trash classification.",
      "composite_interpretation": "Composite 28.8 indicates a moderate Tool bias, but the product is heavily compromised by Trash factors."
    },
    
    "confidence": "Review Required",
    
    "final_verdict_summary": "The product possesses strong utilitarian value (Tool) with verified workflow improvements, but its deceptive privacy claims trigger a critical Trash warning. It is a highly functional but untrustworthy device."
  }
}

```

### Report Requirements

1. **Information Isolation**: Judge only based on the Auditor JSON reports.
2. **Mathematical Transparency**: Show the raw to normalized conversion.
3. **Veto Enforcement**: The JSON must explicitly declare `eagle_eye_veto_activated` (true/false) based on the presence of `critical_issues` from the Trash Auditor.
4. **Final Verdict Summary**: A one-sentence human-readable summary of the product's true nature.

---

## Implementation Note

Every rule on this page is implemented in
[`../scripts/synthesize_results.py`](../scripts/synthesize_results.py) and pinned by
[`../tests/test_synthesize.py`](../tests/test_synthesize.py). Run the Final Judge
through the script rather than by hand — the thresholds interact (four primary
conditions, two secondary tiers, gate overrides, and the veto), and both worked
examples on this page previously disagreed with the code.

If you change a rule here, change the test in the same commit. The tests name the
spec section each case comes from, so the pairing is easy to find.