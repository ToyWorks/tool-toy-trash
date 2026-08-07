# Trash Auditor High-Sensitivity Trigger List (Eagle Eye)

## Purpose

Beyond the standard Dieter Rams checklist, the Eagle Eye protocol identifies **critical Trash risk** product patterns. To eliminate AI subjectivity and leniency, if any of the following trigger conditions are explicitly supported by objective data, the Trash Auditor must **automatically assign a maximum score of 3** for the corresponding item and flag it as a critical failure.

---

## Canonical Trigger Index

**This table is the single source of truth for the Eagle Eye trigger set.**
Every other file that lists triggers — [trash-auditor.md](trash-auditor.md),
[trash-auditor-template.md](trash-auditor-template.md),
[eagle-eye-validator.md](eagle-eye-validator.md) — must match it exactly, and
[`../tests/test_trigger_consistency.py`](../tests/test_trigger_consistency.py)
fails the build if one drifts. Add a pattern here first, then propagate.

| Pattern | Item | Fires when |
| --- | --- | --- |
| **Core Flaw** | 1.2 | Reviews or testing state the primary marketed capability fails |
| **Snake Oil** | 1.2 | Health/psych claim + no clinical data + a medical-device disclaimer |
| **False Pain Point** | 1.2 | The "problem" it solves does not exist for the target user |
| **Privacy Tension** | 1.5 | Claims local/no-cloud but needs continuous cloud for core features |
| **Inconsistent Claims** | 1.5 | Official sources contradict each other |
| **Broken "Never" Promise** | 1.5 | Claims never to listen/store/share data it must transmit to work |
| **Architectural Implausibility** | 1.5 | On-device AI claim not credible for the disclosed form factor |
| **Severe Side Effects** | 2.1 | Documented new hazards: overheating, security holes, data loss |
| **Workflow Sabotage** | 2.1 | Adds massive friction to a previously simple task |
| **Price vs. Doubt** | 3.2 | Price ≥ $200 AND core capability unreliable or unverified |
| **Promise vs. Delivery** | 3.2 | Users explicitly mock the hype-versus-reality gap |
| **Subscription Trap / Brick** | 3.3 | Hardware stops working if the subscription lapses |
| **App Redundancy** | 4.1 | A free smartphone app does the same thing with less friction |
| **Delusional Raison d'être** | 4.2 | Unverified premise + 0% adoption or universal panning |

14 patterns across 7 scored items (1.2, 1.5, 2.1, 3.2, 3.3, 4.1, 4.2). The
sections below give the verbatim-evidence requirement for each.

---

## I. Honesty Principle Reinforcement (Item 1.5: Honest)

### Trigger Conditions (Automatic Score 3)

| Pattern | Item | Evidence Requirement (Must extract verbatim) |
| --- | --- | --- |
| **Privacy Tension** | 1.5 | Text contains marketing claims of "local/no-cloud/doesn't store" AND technical specs/user data showing it requires continuous cloud collection of sensitive signals (acoustic, biometric). |
| **Inconsistent Claims** | 1.5 | Explicit, conflicting statements from different official sources (e.g., product page says "100% waterproof," user manual says "do not expose to moisture"). |
| **Broken "Never" Promise** | 1.5 | Claims "never listen/store/share," but the technical architecture inherently requires transmitting that exact type of data to function. |
| **Architectural Implausibility** | 1.5 | Product claims "fully on-device" / "local AI" processing, but the described capabilities (e.g., LLM inference, real-time multi-modal AI fusion) are technically implausible within the disclosed form factor (e.g., pendant, ring, earbuds) without cloud offloading. Evaluate based on: (a) compute requirements of claimed AI tasks, (b) power/thermal constraints of the form factor, (c) absence of disclosed edge AI chipset or model architecture. |

### Objective Data Requirements

* The AI must extract **both** conflicting quotes into the `verbatim_evidence` array to prove the contradiction.
* For **Architectural Implausibility**: extract the "on-device" claim AND the description of AI capabilities that would typically require cloud compute. The validator must reason about technical feasibility — this is the one Eagle Eye pattern where **engineering judgment** is expected, not just text-matching.
* Do not speculate on undisclosed facts for other patterns; judge only based on disclosed, clashing information.

---

## II. Usefulness Principle Reinforcement (Item 1.2: Useful)

### Trigger Conditions (Automatic Score 3)

| Pattern | Item | Evidence Requirement (Must extract verbatim) |
| --- | --- | --- |
| **Core Flaw** | 1.2 | User reviews or testing data explicitly state the product's *primary marketed capability* fails, hallucinates, or is wildly inaccurate. |
| **Snake Oil** | 1.2 | Product claims a specific health, emotional, or psychological capability BUT explicitly disclaims being a medical device AND lacks any clinical/independent verification data. |
| **False Pain Point** | 1.2 | Text explicitly details that the "problem" it solves either doesn't exist for the target user, or the device forces users to abandon a vastly superior traditional method. |

### Objective Data Requirements

* Distinguish "no data" from "negative data"—only explicit negative data or explicit lack of required clinical backing triggers a 3.
* If data is simply missing (not explicitly disclaimed), score a 1 or 2 based on the standard rubric.

---

## III. Value Deficit Reinforcement (Items 3.2: Cost-effectiveness, 3.3: Sustainable Value)

### Trigger Conditions (Automatic Score 3)

| Pattern | Item | Evidence Requirement (Must extract verbatim) |
| --- | --- | --- |
| **Price vs. Doubt** | 3.2 | Price is explicitly stated as high (e.g., ≥$200) AND the text contains data showing the core capability is unreliable or unverified. |
| **Promise vs. Delivery** | 3.2 | Explicit user feedback directly mocking or lamenting the gap between the marketing hype and the actual delivery (e.g., "overhyped," "scam," "nothing like the ad"). |
| **Subscription Trap / Brick** | 3.3 | The hardware becomes non-functional (a "brick") if a mandatory software subscription is not maintained, completely killing its sustainable physical value. |

---

## IV. Problem Creation Reinforcement (Item 2.1: Creating New Problems)

### Trigger Conditions (Automatic Score 3)

| Pattern | Item | Evidence Requirement (Must extract verbatim) |
| --- | --- | --- |
| **Severe Side Effects** | 2.1 | Text explicitly documents the product creating new hazards (e.g., device overheating, severe security vulnerabilities, data loss, physical discomfort). |
| **Workflow Sabotage** | 2.1 | Text explicitly shows the device adds massive friction to a previously simple task (e.g., "takes 3 minutes to pair just to turn on a light"). |

---

## V. Replaceability Reinforcement (Items 4.1, 4.2)

### Trigger Conditions (Automatic Score 3)

| Pattern | Item | Evidence Requirement (Must extract verbatim) |
| --- | --- | --- |
| **App Redundancy** | 4.1 | The text explicitly mentions that a standard, free smartphone application can achieve the exact same utility with less friction. |
| **Delusional Raison d'être** | 4.2 | Product relies entirely on an unverified "what if" algorithm to justify its physical existence, validated by 0% market adoption or universal reviewer panning. |

---

## VI. Execution Flow

### Insert Point in Trash Auditor Workflow

1. **Extraction Pass**: Read the Brand-Blinded text and extract relevant `verbatim_evidence` for the 14 Dieter Rams items.
2. **Eagle Eye Check**: Compare the extracted quotes against this trigger list.
3. **Score Override**: If a trigger condition is met:
* Set the score for that item to **3**.
* Start the `reason` field with: `"Triggered: [Pattern Name]."` (e.g., `"Triggered: App Redundancy. Free app does it better."`)


4. **Report Compilation**: Add every triggered pattern to the `critical_issues` array in the final JSON output.

Step 4 is what makes the veto fire. `critical_issues` is the only field
`synthesize_results.py` reads for the Eagle Eye Veto — a trigger that is scored
a 3 but never recorded there has no effect on the final classification.

### JSON Output Example

```json
"1.5": {
  "verbatim_evidence": [
    "Claims: All voice processing is done locally on-device.",
    "Tear-down: Device sends unencrypted audio files to AWS servers."
  ],
  "score": 3,
  "max_score": 3,
  "reason": "Triggered: Privacy Tension. Claims local, uses cloud."
}

```

---

## VII. Counterexamples: Avoid Over-Inference

The following situations **should not** trigger an Eagle Eye override (Score 3). Do not speculate; rely only on facts.

* **Missing Reviews:** If there is simply no user feedback available, do not trigger "Core Flaw" just because usefulness isn't proven. Score it a 1 (Claimed) or 0 (No data) on the standard scale.
* **Assumed Cloud Usage:** If the device uses AI, but there is no explicit text stating it secretly uses the cloud against its claims, do not trigger "Privacy Tension." However, **do** evaluate Architectural Implausibility — if the AI workload is clearly beyond what the form factor can handle locally, that IS a valid trigger even without leaked cloud evidence.
* **Valid Niche:** If a product is expensive and niche, but works exactly as advertised for that specific niche, do not trigger "Price vs. Doubt."
* **Legitimate Edge AI:** If the product discloses a specific edge AI chipset (e.g., "NPU with 10 TOPS") or a known lightweight model architecture (e.g., "TinyML", "quantized ONNX"), do not trigger Architectural Implausibility — the engineering is plausible.
* **Unbranded Health Language:** General wellness phrasing with no specific clinical claim is not "Snake Oil." The trigger needs a concrete capability claim plus the disclaimer that contradicts it.

**Golden Rule**: Eagle Eye means you are highly sensitive to **existing evidence of failure**, not that you penalize the product for **missing evidence of success**. The exception is Architectural Implausibility, where the AI auditor applies engineering reasoning to assess whether "on-device" claims are physically credible.
