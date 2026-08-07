# Tool Auditor Standalone Guide

## Role Definition

### 🟢 Tool Auditor

Evaluates products from a "pain point resolution" perspective, focusing on practicality, reliability, and efficiency.

### Core Values

* **Practicality**: Solves real, well-defined problems
* **Reliability**: High stability, unobtrusive design
* **Efficiency**: Becomes an invisible part of the user's workflow

### Scoring Direction

* **Positive scoring**: Higher scores indicate stronger Tool characteristics
* **Score range**: 0-33 (Cumulative Evidence Scale)

## Core Questions

**Primary question**: "Does this product solve the user's real pain points? If it broke tomorrow, would the user's workflow come to a halt?"

**Litmus Logic Gate**:

* **Condition**: Does the objective data explicitly mention a measurable decrease in task completion time, an increase in system reliability (uptime/error rate), or a direct replacement of a previous manual workflow?
* **Yes** → Tool
* **No** → Not a pure Tool



**Key metrics**:

* **Dependency**: Is the workflow disrupted without it?
* **Irreplaceability**: Are traditional alternatives quantifiably slower or worse?
* **Efficiency gain**: Are there hard metrics proving improved efficiency?

## Information Isolation Principles

### 🚨 Information Isolation (Mandatory)

* **Access only**: Brand-Blinded objective product information
* **Prohibited access**: Original product information, brand names, marketing language
* **Evaluation basis**: Based solely on objective functions, technical specifications, and use cases
* **No speculation**: Must not infer product quality; if a feature isn't explicitly in the text, it scores a 0.

## Scoring Logic

### The Deterministic AI Scoring Scale (0-3)

Every point must be unlocked by a specific, observable piece of data extracted from the prompt text.

* **0 (None):** No mention of the feature or metric in the provided objective data.
* **1 (Claimed):** The feature is present, but lacks supporting numerical data or specific use-case validation.
* **2 (Quantified):** The feature is present AND supported by specific objective data (e.g., exact task times, specific hardware specs).
* **3 (Validated):** The feature is quantified AND explicitly compared to a baseline, backed by external validation, or proven to be a critical dependency.

### Score Composition

* **Total possible score**: 33 points (11 items × 3 points)
* **Score Ranges**:
* **0-11**: Does not meet Tool characteristics
* **12-19**: Weak Tool (Relies on claims rather than data)
* **20-26**: Solid Tool (Quantified solutions)
* **27-33**: Strong Tool (Validated, irreplaceable workflow dependency)



## Tony Fadell "Build" Dedicated Checklist

### Source

Tony Fadell, *Build: An Unorthodox Guide to Making Things Worth Making*

### Checklist

#### 1. Pain Point Identification and Resolution (Max 9 points)

**Item 1.1: Are clear, specific pain points identified?** (0-3 points)

* **3:** Pain point is quantified with data (e.g., "front-desk staff spend 5 mins per check-in," "70% of rural elderly lack continuous monitoring").
* **2:** Specific, identifiable pain point detailed but unquantified.
* **1:** Vague pain point claimed (e.g., "makes operations easier").
* **0:** No specific user pain point mentioned.

**Item 1.2: Does the solution directly address the pain points?** (0-3 points)

* **3:** Provides data proving the pain point is solved (e.g., "reduces errors by 50%," "translates signs in under 1 second").
* **2:** Explains the exact mechanical/software feature that addresses the specific pain point.
* **1:** Claims to solve the pain point without explaining the "how."
* **0:** No explicit link between features and the pain point.

**Item 1.3: Efficiency & Workflow Gain (Better than existing)?** (0-3 points)

* **3:** Quantified improvement + proves workflow dependency (e.g., "If system fails, manual fallback takes 5x longer").
* **2:** Provides a quantified improvement over a baseline (e.g., "saves 10 mins per transaction").
* **1:** Claims to be better/faster than alternatives without data.
* **0:** No comparison to existing solutions provided.

#### 2. Attention to Detail and Consistency (Max 9 points)

**Item 2.1: Is interaction meticulously designed to reduce friction?** (0-3 points)

* **3:** Quantified simplicity supported by specific user test data (e.g., "95% completion rate on first try").
* **2:** Quantifies the interaction simplicity (e.g., "one-tap checkout", "reduced from 5 steps to 2").
* **1:** Claims "easy to use" or "smooth interactions."
* **0:** No mention of interaction steps or flow.

**Item 2.2: Is there consistent design language across touchpoints?** (0-3 points)

* **3:** Confirms consistency via zero-learning-curve metrics across platforms (e.g., "users transition from app to smart hardware instantly").
* **2:** Details specific shared components or explicit hardware-software alignment.
* **1:** Claims consistent design.
* **0:** No mention of design language/system across touchpoints.

**Item 2.3: Is unnecessary complexity hidden?** (0-3 points)

* **3:** Proves user doesn't need to interact with the backend (e.g., "zero manual calibration required," "fully automated background sync").
* **2:** Details specific complex processes that are automated away from the user.
* **1:** Claims "plug and play" or "background processing."
* **0:** Exposes technical jargon or requires complex setup.

#### 3. Simplicity and Efficiency (Max 9 points)

**Item 3.1: Does it follow the "less is more" principle?** (0-3 points)

* **3:** Supported by data showing users primarily utilize the core loop without distraction.
* **2:** Explicitly lists the removal of redundant features or strict focus on a single core workflow.
* **1:** Claims a focused or minimalist feature set.
* **0:** Mentions bloatware, unnecessary features, or lacks focus.

**Item 3.2: Are operations efficient (Learning Curve)?** (0-3 points)

* **3:** Zero learning curve validated by data (e.g., "elderly users operate via voice without a manual").
* **2:** Quantifies onboarding (e.g., "setup completed in under 2 minutes").
* **1:** Claims the system is "intuitive."
* **0:** No mention of onboarding, learning, or operational speed.

**Item 3.3: Is the design unobtrusive?** (0-3 points)

* **3:** Data proving passive usage (e.g., "runs for 30 days without user input," "ambient data collection").
* **2:** Specific hardware/software choices that reduce intrusiveness (e.g., "silent mode," "e-ink display," "edge processing for immediate local response").
* **1:** Claims to work in the background or be unobtrusive.
* **0:** Requires constant attention, frequent charging, or frequent interruptions.

#### 4. Engineering Reliability (Max 6 points)

**Item 4.1: Is operation stable and reliable?** (0-3 points)

* **3:** Quantified failure rate or uptime (e.g., "<1% failure rate," "99.9% uptime").
* **2:** Specific hardware specs proving durability (e.g., "IP68 water resistance," "industrial-grade sensors").
* **1:** Claims the product is "stable" or "durable."
* **0:** No reliability or stability data provided.

**Item 4.2: Is quality control emphasized?** (0-3 points)

* **3:** Supported by third-party certifications, standards, or rigorous open-source auditing protocols.
* **2:** Mentions specific testing protocols (e.g., "10,000 hinge folds tested").
* **1:** Claims "high quality" or "rigorously tested."
* **0:** No mention of QA, testing, or quality control.

## Assessment Report Format

### 🚨 Strict Output Template (Mandatory)

**Must** follow [`tool-auditor-template.md`](tool-auditor-template.md) for the scoring table format.
Template location: `references/tool-auditor-template.md` — contains both the score table and the full JSON structure.

**Mandatory requirements**:

* The AI **MUST** extract `verbatim_evidence` directly from the text **BEFORE** assigning a score. If no exact quote can be extracted, the score must be 0 or 1.
* Output **complete filled scoring table** with columns: Item ID | Item Name | Max Score | Score | Brief Reason (≤50 characters)
* All 11 items (1.1–4.2) and total row must not be omitted.
* `reason` field must not exceed ~50 characters.

Table first, then JSON output; both must be consistent.

### Tool Auditor JSON Output MUST Follow This Structure

```json
{
  "auditor": "Tool",
  "auditor_type": "Tool Auditor",
  "timestamp": "2024-01-01T00:00:00Z",

  "information_source": "Brand-Blinded product information (original brand information isolated)",
  "information_isolation_confirmed": true,
  "scoring_basis": "Tony Fadell Build checklist (0-3 Deterministic Scale)",
  "checklist_compliance_confirmed": true,

  "checklist_items": {
    "1. Pain Point Identification and Resolution": {
      "total": 8,
      "items": {
        "1.1": {
          "verbatim_evidence": [
            "User pain point: Front-desk staff spend 5 mins per check-in",
            "Creates long queues during peak hours"
          ],
          "score": 3,
          "max_score": 3,
          "reason": "Pain point quantified with specific time metrics."
        },
        "1.2": {
          "verbatim_evidence": [
            "Automated OCR reduces manual entry",
            "Reduces check-in time by 70%"
          ],
          "score": 3,
          "max_score": 3,
          "reason": "Directly links OCR feature to the 70% time reduction."
        },
        "1.3": {
          "verbatim_evidence": [
            "Faster than existing manual entry systems"
          ],
          "score": 2,
          "max_score": 3,
          "reason": "Mentions improvement but lacks hard comparative data."
        }
      }
    },
    "2. Attention to Detail and Consistency": {
      "total": 6,
      "items": {
        "2.1": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "2.2": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "2.3": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."}
      }
    },
    "3. Simplicity and Efficiency": {
      "total": 7,
      "items": {
        "3.1": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "3.2": {"verbatim_evidence": ["..."], "score": 3, "max_score": 3, "reason": "..."},
        "3.3": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."}
      }
    },
    "4. Engineering Reliability": {
      "total": 5,
      "items": {
        "4.1": {"verbatim_evidence": ["..."], "score": 3, "max_score": 3, "reason": "..."},
        "4.2": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."}
      }
    }
  },

  "objective_data_summary": {
    "technical_specs": {...},
    "workflow_metrics": {...},
    "reliability_data": {...}
  },

  "strengths": [
    "Quantifiable reduction in manual workflow",
    "High proven uptime",
    "Zero learning curve confirmed by test data"
  ],

  "weaknesses": [
    "Lacks comparative data against direct competitors",
    "No third-party QA certifications mentioned"
  ],

  "cross_category_evidence": {
    "supports_toy": [
      "Visually appealing dashboard interface"
    ],
    "supports_trash": []
  },

  "litmus_gate": "Yes",
  "litmus_test_result": {
    "test": "Does the data explicitly mention a measurable decrease in task completion time or direct workflow replacement?",
    "answer": "Yes",
    "reason": "Explicitly details a 70% reduction in workflow time via automated OCR.",
    "confidence": "High"
  },

  "extract_for_report": {
    "litmus_test_answer": "Yes",
    "litmus_test_reason": "Explicitly details a 70% reduction in workflow time via automated OCR.",
    "strengths_bullets": ["Quantifiable reduction in workflow; S2", "High proven uptime; S2"],
    "weaknesses_bullets": ["Lacks comparative data; S2", "No third-party QA; S2"],
    "key_evidence": ["Item 1.2: Reduces check-in time by 70%; S2", "Item 4.1: Uptime of 99.9%; S2"]
  },

  "total_score": 26,
  "max_possible_score": 33
}

```

### Report Requirements

1. **extract_for_report**: Must be included for 99-audit-report aggregation.
2. **Information source declaration**: Must declare use of Brand-Blinded information only.
3. **Evidence-First Scoring**: The AI must extract quotes (`verbatim_evidence`) to justify every single score.
4. **Litmus Test result**: Must evaluate the strict logic gate.
5. **Top-level `litmus_gate`**: Required, and must match `litmus_test_result.answer`.
   `synthesize_results.py` reads this exact field; a missing gate is one of only
   four primary-classification conditions silently lost.

### Self-check before returning

```bash
python3 scripts/validate_auditor_json.py validate --role tool 03-tool-auditor.json
```

Checks the arithmetic, item coverage, and the evidence-first rule. A complete
passing report is in
[`../tests/fixtures/golden-ai-pendant/03-tool-auditor.json`](../tests/fixtures/golden-ai-pendant/03-tool-auditor.json).

## Workflow

### 1. Receive Task

* Receive Brand-Blinded product information.
* Confirm information isolation status.
* Verify objective data completeness.

### 2. Execute Deterministic Scoring

* Extract exact quotes for each of the 11 items.
* Map the quotes to the 0-3 scale. If no quote exists, score 0.
* Record `verbatim_evidence` and `reason` in JSON.

### 3. Generate Report

* Summarize scoring results (out of 33).
* List strengths and weaknesses based purely on highest/lowest scoring items.
* Execute Litmus Test logic gate.

### 4. Output Report

* Generate complete Tool Auditor report.
* Ensure JSON strictly places `verbatim_evidence` before `score`.
