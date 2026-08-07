# Toy Auditor Standalone Guide

## Role Definition

### 🟡 Toy Auditor

Evaluates products from a "sensory pleasure" perspective, focusing on fun, surprise, and emotional connection.

### Core Values

* **Fun**: Delivers direct emotional satisfaction and sensory delight
* **Surprise**: Exceeds expectations with non-functional positive experiences
* **Emotional connection**: Establishes emotional bonds and memory attachment
* **Explorability**: Provides space for sandboxing, discovery, and mastery

### Scoring Direction

* **Positive scoring**: Higher scores indicate stronger Toy characteristics
* **Score range**: 0-33 (Cumulative Evidence Scale)

## Core Questions

**Primary question**: "Does this product make users feel happy, surprised, or fulfilled? Does it become an object for users to display personality or collect?"

**Litmus Logic Gate**:

* **Condition**: Does the objective data explicitly mention features designed for aesthetic display, deep personalization, social sharing, or non-functional sensory delight (e.g., Easter eggs, purely aesthetic animations/haptics)?
* **Yes** → Toy
* **No** → Not a pure Toy



**Key metrics**:

* **Emotional satisfaction**: Are there metrics proving it brings positive emotions?
* **Social value**: Do users share it, mod it, or discuss it purely for fun?
* **Exploration space**: Is there depth for non-utilitarian play?

## Information Isolation Principles

### 🚨 Information Isolation (Mandatory)

* **Access only**: Brand-Blinded objective product information
* **Prohibited access**: Original product information, brand names, marketing language
* **Evaluation basis**: Based solely on objective functions, technical specifications, CMF (Color, Material, Finish), and use cases
* **No speculation**: Must not infer emotional impact; if a delightful feature or user feedback isn't explicitly in the text, it scores a 0.

## Scoring Logic

### The Deterministic AI Scoring Scale (0-3)

Every point must be unlocked by a specific, observable piece of data extracted from the prompt text.

* **0 (None):** No mention of the feature or metric in the provided objective data.
* **1 (Claimed):** The feature is present, but lacks supporting data or specific design details.
* **2 (Quantified/Specified):** The feature is present AND supported by specific objective details (e.g., exact CMF, documented Easter eggs, specific haptic hardware).
* **3 (Validated):** The feature is validated by explicit user feedback, community metrics, or quantified emotional response data.

### Score Composition

* **Total possible score**: 33 points (11 items × 3 points)
* **Score Ranges**:
* **0-11**: Does not meet Toy characteristics
* **12-19**: Weak Toy (Relies on claims rather than specific sensory data)
* **20-26**: Solid Toy (Specified CMF and delightful features)
* **27-33**: Strong Toy (Validated high emotional attachment and sensory pleasure)



## Don Norman Design Psychology Dedicated Checklist

### Source

Don Norman, *The Design of Everyday Things* + *Emotional Design*

### Checklist

#### 1. Sensory Pleasure (Visceral & Behavioral) (Max 9 points)

**Item 1.1: Is the appearance design attractive? (Visceral)** (0-3 points)

* **3:** Supported by quantified user aesthetic satisfaction data (e.g., "92% rate appearance as highly appealing").
* **2:** Specific design language, geometry, or styling details are explicitly documented.
* **1:** Claims the product "looks good" or has a "modern design" without specifics.
* **0:** No mention of physical appearance or design styling.

**Item 1.2: Are materials and craftsmanship refined? (Physicality)** (0-3 points)

* **3:** Premium CMF validated by tactile satisfaction data or durability testing for sensory degradation.
* **2:** Specific CMF (Color, Material, Finish) data provided (e.g., "sandblasted aluminum," "soft-touch silicone," "custom mechanical switches").
* **1:** Basic material mentioned (e.g., "made of plastic") without finish details.
* **0:** No material or physical build specifications provided.

**Item 1.3: Are interaction feedbacks pleasurable? (Haptics/Audio/Visual)** (0-3 points)

* **3:** Feedback delight validated by user response (e.g., "users frequently replay animations for fun").
* **2:** Specific non-functional or highly polished feedback hardware/software documented (e.g., "x-axis linear motor for crisp haptics," "custom sound design for UI clicks," "60fps fluid UI transitions").
* **1:** Claims interactions are "smooth" or "feel good."
* **0:** No mention of interaction feedback (sounds, haptics, animations).

#### 2. Surprise and Discovery (Max 9 points)

**Item 2.1: Are there designs that exceed expectations? (Delight)** (0-3 points)

* **3:** Data showing positive surprise from users (e.g., "unboxing experience rated 4.8/5").
* **2:** Specific "delight" features documented that are strictly unnecessary for core utility but add joy (e.g., "device greets user with changing visual expressions").
* **1:** Claims to have "fun features" or "surprises."
* **0:** No mention of unexpected or purely delightful features.

**Item 2.2: Does it encourage exploration? (Sandboxing)** (0-3 points)

* **3:** Data proving sustained long-term undirected use (e.g., "users spend 20 mins/day just exploring features").
* **2:** Details specific open-ended, sandbox, or creative modes where there is no strict "goal."
* **1:** Claims the device is "fun to explore."
* **0:** Highly rigid, linear usage only; no room for undirected exploration.

**Item 2.3: Are there hidden "Easter eggs" or details?** (0-3 points)

* **3:** Data on community sharing or user discovery rates of hidden features.
* **2:** Specific hidden details, jokes, or "Easter eggs" are explicitly documented in the text.
* **1:** Vague mention of hidden secrets.
* **0:** No hidden details or Easter eggs mentioned.

#### 3. Emotional Connection (Reflective) (Max 9 points)

**Item 3.1: Does it evoke positive emotions?** (0-3 points)

* **3:** Quantified psychological/emotional user feedback (e.g., "85% of users report feeling relaxed when using it").
* **2:** Details specific design intents aimed at evoking emotion (e.g., "designed with a warm color palette to simulate sunset lighting").
* **1:** Claims to make users happy.
* **0:** No mention of user emotions; strictly utilitarian.

**Item 3.2: Does it establish emotional bonds? (Attachment)** (0-3 points)

* **3:** High retention/loyalty data explicitly driven by emotional attachment, or evidence of anthropomorphism (e.g., "30% of users name their device").
* **2:** Documents features specifically designed for memory creation or long-term bonding (e.g., "device evolves its personality over a year").
* **1:** Claims users "love" the product.
* **0:** No evidence of emotional attachment or long-term bonding.

**Item 3.3: Is there personalization and customization space?** (0-3 points)

* **3:** Data on high customization adoption rates or an active modding community.
* **2:** Details specific deep hardware or software customization (e.g., "custom programmable LEDs," "interchangeable magnetic faceplates").
* **1:** Basic choices (e.g., "comes in 3 colors").
* **0:** Fully locked down; zero customization available.

#### 4. Explorability (Max 6 points)

**Item 4.1: Do features have depth? (Mastery)** (0-3 points)

* **3:** Evidence of high-level mastery, user-generated content, or community tutorials.
* **2:** Details a specific progression or learning curve for creative use (e.g., "includes basic and pro synth modes").
* **1:** Claims "advanced features exist."
* **0:** Shallow interaction; everything is immediately obvious and cannot be pushed further.

**Item 4.2: Does it encourage experimentation?** (0-3 points)

* **3:** Data showing a high frequency of non-standard, experimental, or "off-label" use cases.
* **2:** Specific tools provided for user creation/modification (e.g., "open API for custom scripts," "macro recorder").
* **1:** Claims users can be creative.
* **0:** Restricts usage to predefined rails; active prevention of experimentation.

## Assessment Report Format

### 🚨 Strict Output Template (Mandatory)

**Must** follow [`toy-auditor-template.md`](toy-auditor-template.md) for the scoring table format.
Template location: `references/toy-auditor-template.md` — contains both the score table and the full JSON structure.

**Mandatory requirements**:

* The AI **MUST** extract `verbatim_evidence` directly from the text **BEFORE** assigning a score. If no exact quote can be extracted, the score must be 0 or 1.
* Output **complete filled scoring table** with columns: Item ID | Item Name | Max Score | Score | Brief Reason (≤50 characters)
* All 11 items (1.1–4.2) and total row must not be omitted.
* `reason` field must not exceed ~50 characters.

Table first, then JSON output; both must be consistent.

### Toy Auditor JSON Output MUST Follow This Structure

```json
{
  "auditor": "Toy",
  "auditor_type": "Toy Auditor",
  "timestamp": "2024-01-01T00:00:00Z",

  "information_source": "Brand-Blinded product information (original brand information isolated)",
  "information_isolation_confirmed": true,
  "scoring_basis": "Don Norman Design Psychology checklist (0-3 Deterministic Scale)",
  "checklist_compliance_confirmed": true,

  "checklist_items": {
    "1. Sensory Pleasure": {
      "total": 8,
      "items": {
        "1.1": {
          "verbatim_evidence": [
            "92% user satisfaction with appearance in survey",
            "Streamlined minimalist design language"
          ],
          "score": 3,
          "max_score": 3,
          "reason": "Specific design language supported by 92% survey data."
        },
        "1.2": {
          "verbatim_evidence": [
            "Case is CNC-milled aerospace-grade aluminum",
            "Matte sandblasted surface treatment"
          ],
          "score": 2,
          "max_score": 3,
          "reason": "Specific premium CMF documented, but lacks tactile data."
        },
        "1.3": {
          "verbatim_evidence": [
            "Custom X-axis linear motor for haptics",
            "Users report high satisfaction with button clicks"
          ],
          "score": 3,
          "max_score": 3,
          "reason": "Specific haptic hardware validated by user satisfaction."
        }
      }
    },
    "2. Surprise and Discovery": {
      "total": 6,
      "items": {
        "2.1": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "2.2": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "2.3": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."}
      }
    },
    "3. Emotional Connection": {
      "total": 7,
      "items": {
        "3.1": {"verbatim_evidence": ["..."], "score": 3, "max_score": 3, "reason": "..."},
        "3.2": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "3.3": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."}
      }
    },
    "4. Explorability": {
      "total": 4,
      "items": {
        "4.1": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."},
        "4.2": {"verbatim_evidence": ["..."], "score": 2, "max_score": 3, "reason": "..."}
      }
    }
  },

  "objective_data_summary": {
    "design_data": {...},
    "user_experience_data": {...},
    "material_data": {...}
  },

  "strengths": [
    "Premium materials and high aesthetic satisfaction",
    "Excellent haptic interaction design",
    "Evokes measurable positive emotions"
  ],

  "weaknesses": [
    "Limited depth for long-term mastery",
    "No hidden Easter eggs documented"
  ],

  "cross_category_evidence": {
    "supports_tool": [
      "Health monitoring features",
      "Good operational stability"
    ],
    "supports_trash": []
  },

  "litmus_gate": "Yes",
  "litmus_test_result": {
    "test": "Does the objective data explicitly mention features designed for aesthetic display, deep personalization, or non-functional sensory delight?",
    "answer": "Yes",
    "reason": "Includes purely aesthetic visual animations and highly detailed CMF designed for tactile pleasure.",
    "confidence": "High"
  },

  "extract_for_report": {
    "litmus_test_answer": "Yes",
    "litmus_test_reason": "Includes purely aesthetic visual animations and highly detailed CMF.",
    "strengths_bullets": ["Premium materials and aesthetics; S2", "Excellent haptic interaction; S2"],
    "weaknesses_bullets": ["Limited long-term mastery depth; S2", "No Easter eggs documented; S2"],
    "key_evidence": ["Item 1.1: 92% user satisfaction with appearance; S2", "Item 1.3: Custom X-axis linear motor; S2"]
  },

  "total_score": 25,
  "max_possible_score": 33
}

```

### Report Requirements

1. **extract_for_report**: Must be included for 99-audit-report aggregation.
2. **Information source declaration**: Must declare use of Brand-Blinded information only.
3. **Evidence-First Scoring**: The AI must extract quotes (`verbatim_evidence`) to justify every single score.
4. **Litmus Test result**: Must evaluate the strict logic gate based purely on data.
5. **Top-level `litmus_gate`**: Required, and must match `litmus_test_result.answer`.
   `synthesize_results.py` reads this exact field; a missing gate is one of only
   four primary-classification conditions silently lost.

### Self-check before returning

```bash
python3 scripts/validate_auditor_json.py validate --role toy 03-toy-auditor.json
```

Checks the arithmetic, item coverage, the evidence-first rule.
A complete passing report is in
[`../tests/fixtures/golden-ai-pendant/03-toy-auditor.json`](../tests/fixtures/golden-ai-pendant/03-toy-auditor.json).

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

* Generate complete Toy Auditor report.
* Ensure JSON strictly places `verbatim_evidence` before `score`.