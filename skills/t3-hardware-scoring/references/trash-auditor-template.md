# Trash Auditor Score Table Template

## Scoring Table (Mandatory — fill all rows)

| Item ID | Item Name | Max Score | Score | Brief Reason (≤50 chars) |
|---------|-----------|-----------|-------|--------------------------|
| 1.1 | Innovative Violation (Copycat) | 3 | _ | |
| 1.2 | Useful Violation (Uselessness) | 3 | _ | |
| 1.3 | Aesthetic Violation (Ugly) | 3 | _ | |
| 1.4 | Understandable Violation (Confusing) | 3 | _ | |
| 1.5 | Honest Violation (Deceptive) | 3 | _ | |
| 1.6 | Long-lasting Violation (E-waste) | 3 | _ | |
| 2.1 | Creates New Problems | 3 | _ | |
| 2.2 | Increases User Burden | 3 | _ | |
| 2.3 | Unnecessary Complexity | 3 | _ | |
| 3.1 | No Clear Value Proposition | 3 | _ | |
| 3.2 | Not Worth the Cost | 3 | _ | |
| 3.3 | No Sustainable Value | 3 | _ | |
| 4.1 | Easily Replaceable | 3 | _ | |
| 4.2 | No Reason to Exist | 3 | _ | |
| **TOTAL** | | **42** | **_** | |

*Note the inverted direction: a HIGH score means STRONGER Trash characteristics.*

## Scoring Scale Reminder

| Score | Meaning | Requirement |
|-------|---------|-------------|
| 0 | Fine | No mention of this flaw in the data |
| 1 | Claimed Issue | Minor complaint, vague negative feedback, theoretical issue |
| 2 | Quantified Flaw | Specific data showing failure (rates, steps, measurements) |
| 3 | Severe / Eagle Eye | Critical failure backed by data, or an Eagle Eye trigger |

## Eagle Eye Trigger Quick Reference

Full conditions and counterexamples: [trash-red-flags.md](trash-red-flags.md).
A trigger is not optional — if the condition is met, the score **must** be 3.

| Pattern | Item | Fires when |
|---------|------|-----------|
| **Core Flaw** | 1.2 | Reviews state the primary marketed capability fails |
| **Snake Oil** | 1.2 | Health/psych claim + no clinical data + medical-device disclaimer |
| **False Pain Point** | 1.2 | The "problem" it solves does not exist for the target user |
| **Privacy Tension** | 1.5 | Claims local/no-cloud but needs continuous cloud for core features |
| **Inconsistent Claims** | 1.5 | Official sources contradict each other |
| **Broken "Never" Promise** | 1.5 | Claims never to listen/store/share data it must transmit to work |
| **Architectural Implausibility** | 1.5 | On-device AI claim not credible for the disclosed form factor |
| **Severe Side Effects** | 2.1 | Documented new hazards (overheating, security holes, data loss) |
| **Workflow Sabotage** | 2.1 | Adds massive friction to a previously simple task |
| **Price vs. Doubt** | 3.2 | Price ≥ $200 AND core capability unreliable or unverified |
| **Promise vs. Delivery** | 3.2 | Users explicitly mock the hype-vs-reality gap |
| **Subscription Trap / Brick** | 3.3 | Hardware stops working if the subscription lapses |
| **App Redundancy** | 4.1 | A free smartphone app does the same thing with less friction |
| **Delusional Raison d'être** | 4.2 | Unverified premise + 0% adoption or universal panning |

When a trigger fires:

1. Set that item's score to **3**.
2. Start the `reason` with `"Triggered: <Pattern Name>."`
3. Add a matching entry to the top-level `critical_issues` array.

Step 3 is what makes the veto fire — `critical_issues` is the only field
`synthesize_results.py` reads for the Eagle Eye Veto. A trigger that is scored
but never recorded there has no effect on the verdict.

## JSON Output Template

```json
{
  "auditor": "Trash",
  "auditor_type": "Trash Auditor",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "information_source": "Brand-Blinded product information (original brand information isolated)",
  "information_isolation_confirmed": true,
  "scoring_basis": "Dieter Rams Checklist & Eagle Eye Triggers (0-3 Scale)",
  "checklist_compliance_confirmed": true,
  "checklist_items": {
    "1. Principle Violation": {
      "total": 0,
      "items": {
        "1.1": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "1.2": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "1.3": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "1.4": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "1.5": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "1.6": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" }
      }
    },
    "2. Problem Creation": {
      "total": 0,
      "items": {
        "2.1": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "2.2": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "2.3": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" }
      }
    },
    "3. Value Deficit": {
      "total": 0,
      "items": {
        "3.1": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "3.2": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "3.3": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" }
      }
    },
    "4. Replaceability": {
      "total": 0,
      "items": {
        "4.1": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" },
        "4.2": { "verbatim_evidence": [], "score": 0, "max_score": 3, "reason": "" }
      }
    }
  },
  "critical_issues": [],
  "strengths": [],
  "cross_category_evidence": {
    "supports_tool": [],
    "supports_toy": []
  },
  "litmus_gate": "No",
  "litmus_test_result": {
    "test": "Does the data explicitly show the product causes more friction, expense, or privacy risk than the traditional alternative?",
    "answer": "No",
    "reason": "",
    "confidence": "Low"
  },
  "extract_for_report": {
    "litmus_test_answer": "No",
    "litmus_test_reason": "",
    "strengths_bullets": [],
    "weaknesses_bullets": [],
    "key_evidence": [],
    "critical_issues": []
  },
  "total_score": 0,
  "max_possible_score": 42
}
```

## Filling Rules

1. `verbatim_evidence` MUST be extracted from the Brand-Blinded text **before**
   assigning a score
2. If no exact quote exists → score must be 0 (or 1 for a vague mention)
3. `reason` field ≤ 50 characters; Eagle Eye reasons start `"Triggered: ..."`
4. `litmus_gate` top-level field: `"Yes"` or `"No"` — **required**;
   `synthesize_results.py` reads this exact field, and its absence used to be
   read silently as `"No"`
5. `total_score` = sum of all 14 item scores (max 42)
6. `critical_issues` must have exactly one entry per `"Triggered:"` item

## Self-check before returning

```bash
python3 scripts/validate_auditor_json.py validate --role trash 03-trash-auditor.json
```

This checks the arithmetic, the item coverage, the evidence-first rule, and the
trigger/`critical_issues` correspondence. A worked example of a passing report
is in [`../tests/fixtures/golden-ai-pendant/03-trash-auditor.json`](../tests/fixtures/golden-ai-pendant/03-trash-auditor.json).
