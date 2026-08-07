# Brand Blinding Guide

## Purpose

### Why Brand Blinding?

Brand influence can bias hardware product evaluation. We must remove the brand identity without destroying the data footprint of the product.

### Goals

* **Objectivity**: Remove subjective brand-halo influence.
* **Evidence Preservation**: Keep exact marketing claims and emotional language intact. Downstream Auditors *need* this text to evaluate "Promise vs. Delivery" (Trash Auditor) or "Sensory Pleasure" (Toy Auditor).

## Principles

### 1. Redact, Do Not Rewrite

Use bracketed redaction `[BRAND]` or `[PRODUCT]` instead of rewriting sentences into generic summaries. Paraphrasing destroys the `verbatim_evidence` needed by downstream auditors.

### 2. Preserve the "Vibe" for the Auditors

The Toy Auditor needs to see words like "beautiful" to score Aesthetic intent. The Trash Auditor needs to see words like "revolutionary" to check for deceptive marketing. **Do not delete adjectives; simply decouple them from the brand name.**

## Filtering Rules

### Rule 1: Redact Brand Names (Strictly)

**Action**: Replace brand names, product line names, and trademarks with generic bracketed tags.

* `[BRAND]` for the company.
* `[PRODUCT]` for the item.
* `[FEATURE]` for trademarked software/tech names.

**Example**:

* *Raw*: "Apple Watch Series 9 features Apple's revolutionary S9 chip."
* *Blinded*: "`[PRODUCT]` (9th gen) features `[BRAND]`'s revolutionary `[FEATURE]` chip."

### Rule 2: Preserve Marketing & Emotional Language

**🔴 CRITICAL CHANGE**: Do NOT delete hype, slogans, or emotional adjectives ("amazing," "revolutionary," "premium").

**Action**: Leave them exactly as written. The downstream AI Auditors are now programmed to mathematically evaluate these claims (e.g., The Trash Auditor's Eagle Eye checks if "revolutionary" claims are backed by specs). If you delete them, you break the audit.

**Example**:

* *Raw*: "The elegant design provides ultimate comfort for all-day wear."
* *Blinded*: "The elegant design provides ultimate comfort for all-day wear." *(Unchanged, as there is no brand name to redact).*

### Rule 3: Preserve Functional Information & Third-Party Claims

**Action**: All objective data, test data, and third-party claims must be fully preserved. Do not alter numbers, metrics, or reviewer quotes.

**Example**:

* *Raw*: "Rated 'Best in Class' by Wired Magazine, boasting a 99% accuracy rate."
* *Blinded*: "Rated 'Best in Class' by tech publication, boasting a 99% accuracy rate."

### Rule 4: Do Not Synthesize Data

If the source text is a bulleted list of messy specs, leave it as a bulleted list. Do not attempt to write a flowing paragraph. The Auditors are looking for hard data points to extract.

## Process

1. **Scan**: Identify brand names, trademarks, and specific proprietary ecosystem references.
2. **Redact**: Replace those specific proper nouns with `[BRAND]`, `[PRODUCT]`, or `[FEATURE]`.
3. **Verify Integrity**: Read the blinded sentence. Does it contain the exact same adjectives, numbers, and claims as the original? If yes, it is ready.

## Examples

### Smartwatch

**Raw**:

```
Apple Watch Series 9 features Apple's revolutionary S9 chip,
delivering stunning performance with the most advanced display
ever. The beautiful aluminum case is crafted with premium materials,
offering up to 18 hours of battery life. Rated 4.8 stars by users.

```

**Brand-Blinded**:

```
[PRODUCT] (9th gen) features [BRAND]'s revolutionary [FEATURE] chip,
delivering stunning performance with the most advanced display
ever. The beautiful aluminum case is crafted with premium materials,
offering up to 18 hours of battery life. Rated 4.8 stars by users.

```

*(Notice how "revolutionary", "stunning", and "beautiful" are preserved so the Toy and Trash auditors can evaluate the marketing vs. the 18-hour battery spec).*

### Wireless Headphones

**Raw**:

```
Dyson Zone is the groundbreaking noise-canceling headphones with
purifying visor, featuring amazing electrostatic technology. The
elegant design provides ultimate comfort for all-day wear.

```

**Brand-Blinded**:

```
[PRODUCT] is the groundbreaking noise-canceling headphones with
purifying visor, featuring amazing electrostatic technology. The
elegant design provides ultimate comfort for all-day wear.

```

## Common Pitfalls

1. **Over-sterilization**: Deleting "marketing fluff." *Do not do this. The Trash Auditor relies on finding fluff to penalize the product.*
2. **Paraphrasing**: Rewriting a clunky sentence to sound better. *Do not do this. It ruins the exact quote extraction for the Auditors.*
3. **Brand residue**: Missing hidden ecosystem terms (e.g., forgetting to redact "MagSafe" or "Siri").

## Brand Blinding Checklist

* [ ] All proper brand names and trademarks replaced with `[BRAND]` / `[PRODUCT]` / `[FEATURE]`.
* [ ] ALL adjectives, marketing hype, and emotional language **preserved exactly as written**.
* [ ] All technical specs, numbers, and metrics preserved.
* [ ] No paraphrasing or summarizing applied to the original sentence structure.