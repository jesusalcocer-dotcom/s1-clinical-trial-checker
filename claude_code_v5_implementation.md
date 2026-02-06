# CLAUDE CODE IMPLEMENTATION: V5 UPDATE
# Copy-paste this entire block into Claude Code after navigating to the repo root

---

## CONTEXT: WHAT HAPPENED

Five new framework documents were produced that restructure how the
tool's legal analysis, comparison pairs, escalation prompts, and
output formatting work. These documents supersede portions of the
existing reference files and spec. Your job is to integrate them
into the codebase.

**The five new documents** (all in the repo root after you copy them):

| File | Lines | What It Contains |
|------|-------|-----------------|
| `legal_brief.md` | 802 | Lawyer-auditable legal framework: Step 1 (candidate checks), Step 2 (study checks), Step 3 (escalation). Maps ALL checks to specific legal authorities with verbatim SEC language. |
| `study_specific_output.md` | 914 | Complete Step 2 output format spec: required disclosure elements table with legal citations, technical extraction process, improved UI (✓ ✗ ≈ ⬜ ⚠), per-check escalation prompts for checks 8-11 + FDAAA 801. |
| `check2_phase_labels.md` | 473 | Check 2 deep-dive: 3 comparison pairs (Sensei, Nuvalent, Taysha) with actual S-1 text, SEC comments, severity spectrum, 3-step escalation prompt architecture. |
| `checks_3_4_5.md` | 1469 | Checks 3, 4, 5 deep-dive: 7+ comparison pairs (Curanex, Virpax, Nuvalent, Zenas, Khosla, Aerovate, Annovis) + AVEO enforcement + Tongue v. Sanofi case law. 17 placeholder slots for S-1 text. |
| `checks_6_7.md` | 1128 | Checks 6, 7 deep-dive: 7 comparison pairs (Taysha, Altamira, Graybug, Madrigal, Scopus, OS Therapies). Three-tier phrase classification system. 4-step escalation prompt for Check 7. 14 placeholder slots. |

---

## STEP 0: READ BEFORE DOING ANYTHING

Read these files IN THIS ORDER to understand the current state:

```
1. SKILL.md                              — current skill definition
2. s1_checker_skill_spec_v4.md           — current v4 spec (1143 lines)
3. reference/operationalized_checks.json — current check definitions (676 lines)
4. reference/comment_letter_excerpts.json — current comparison pairs (459 lines)
5. reference/legal_framework.json        — current legal authorities (371 lines)
6. reference/guardrails.json             — current Layer 2 procedures (139 lines)
7. reference/red_flag_phrases.txt        — current phrase list (21 lines)
```

Then read ALL FIVE new documents:

```
8. legal_brief.md
9. study_specific_output.md
10. check2_phase_labels.md
11. checks_3_4_5.md
12. checks_6_7.md
```

DO NOT start editing until you have read all 12 files.

---

## STEP 1: ADD NEW REFERENCE DOCUMENTS

### 1A. Copy the five framework docs into `reference/`

```bash
cp legal_brief.md reference/legal_brief.md
cp study_specific_output.md reference/study_specific_output.md
cp check2_phase_labels.md reference/check2_phase_labels.md
cp checks_3_4_5.md reference/checks_3_4_5.md
cp checks_6_7.md reference/checks_6_7.md
```

These become the AUTHORITATIVE source for comparison pairs,
escalation prompts, and severity spectrums. The JSON files below
will REFERENCE these documents but contain the machine-readable
skeletons only (see Architecture Decisions at bottom of this file).

**IMPORTANT: Add section anchors to each .md file** so the JSON
can reference specific sections. Use HTML comment anchors:

```markdown
<!-- ANCHOR: ESCALATION_PROMPT_ARCHITECTURE -->
<!-- ANCHOR: STEP_1 -->
<!-- ANCHOR: SEVERITY_SPECTRUM -->
<!-- ANCHOR: COMPARISON_PAIR_SENSEI -->
```

Add these at the start of each major section in all five files
during the copy. This is required for the hybrid JSON→MD
reference pattern to work at runtime.

---

## STEP 2: UPDATE `reference/operationalized_checks.json`

This is the most important file. Each check definition needs to be
enriched with the detailed content from the new framework docs.

### What to add per check:

**For EVERY check (2, 3, 4, 5, 6, 7)**, the existing JSON entry needs:

```json
{
  "id": "phase_labels",
  ...existing fields...,

  "comparison_pairs": [
    {
      "id": "sensei_phase_labels",
      "company": "Sensei Biotherapeutics",
      "filing_type": "S-1",
      "filing_date": "2021-01-15",
      "s1_text_challenged": "<<EXACT QUOTED TEXT from check2_phase_labels.md>>",
      "sec_comment_verbatim": "<<EXACT QUOTED TEXT from check2_phase_labels.md>>",
      "what_sec_required": "<<summary>>",
      "severity_level": "HIGH",
      "useful_for_comparison_because": "<<why this pair matters>>"
    }
  ],

  "severity_spectrum": {
    "description": "<<from the framework doc>>",
    "levels": [
      {"label": "GREEN_CLEAR", "description": "...", "example": "..."},
      {"label": "YELLOW_BORDERLINE", "description": "...", "example": "..."},
      {"label": "RED_MATCHES_CHALLENGED", "description": "...", "example": "..."}
    ]
  },

  "escalation_prompt": {
    "trigger": "<<when the escalation fires>>",
    "source_doc": "reference/check2_phase_labels.md",
    "source_section": "ESCALATION_PROMPT_ARCHITECTURE",
    "steps": [
      {
        "step": 1,
        "name": "text_to_text_comparison",
        "executor": "llm",
        "prompt_source": "reference/check2_phase_labels.md#STEP_1",
        "slots": ["{{S1_TEXT}}", "{{COMPARISON_PAIRS}}"],
        "output_format": {"type": "json", "keys": ["classification", "explanation_present", "severity", "step1_assessment"]}
      },
      {
        "step": 2,
        "name": "web_search_augmentation",
        "executor": "web_search",
        "trigger": "fires_only_on_CONCERN_or_SIGNIFICANT_CONCERN",
        "query_template": "SEC comment letter {{TOPIC}} {{YEAR_RANGE}}",
        "output_keys": ["search_result", "assessment: STRENGTHEN|WEAKEN|NEUTRAL"]
      },
      {
        "step": 3,
        "name": "final_determination",
        "executor": "llm",
        "prompt_source": "reference/check2_phase_labels.md#STEP_3",
        "output_keys": ["final_status: GREEN|YELLOW|RED", "narrative"]
      }
    ]
  }
}
```

### Specific instructions per check:

#### Check 2 (Phase Labels)
- Source: `check2_phase_labels.md`
- Add 3 comparison pairs: Sensei (lines 26-93), Nuvalent (lines 95-165), Taysha (lines 167-240)
- Add severity spectrum from lines ~245-280
- Add 3-step escalation prompt architecture from lines ~285-473
- The escalation prompt includes:
  - Step 1: classify as COMBINED vs SUB_PHASE, check for explanation
  - Step 2: web search (fires only on CONCERN)
  - Step 3: decision tree → GREEN/YELLOW/RED

#### Check 3 (Preclinical Framing)
- Source: `checks_3_4_5.md` — CHECK 3 section
- Add 2 comparison pairs: Curanex, Virpax
- Note: Curanex has TWO SEC comments from same letter (straddles Check 3 and 4)
- Add severity spectrum: CURANEX-LIKE → VIRPAX-LIKE → BORDERLINE
- Add 4 escalation triggers with detection logic
- **17 PLACEHOLDER slots** exist — leave these as-is with `"s1_text_challenged": "[PLACEHOLDER — to be filled from SEC filing]"` and a TODO comment

#### Check 4 (Comparative Claims)
- Source: `checks_3_4_5.md` — CHECK 4 section
- Add 4 comparison pairs: Nuvalent, Zenas, Khosla/Valo, Curanex (cross-ref)
- KEY RULE from Zenas: "qualifying language DOES NOT address the concern" — this exact sentence must be in the comparison pair because it overrides the instinct to treat "we believe" as a hedge
- Add 5-level severity spectrum: factual distinction → differentiated → best-in-class → safer/more effective → superiority over named competitor

#### Check 5 (FDA Communications)
- Source: `checks_3_4_5.md` — CHECK 5 section
- This check has MIXED authority types:
  - 1 enforcement action: SEC v. AVEO (fraud charges)
  - 1 case law: Tongue v. Sanofi (Second Circuit)
  - 2 comment letters: Aerovate, Annovis Bio
- Add the two-test framework: BALANCE test + FRAMING test
- Add section placement analysis logic

#### Check 6 (Pipeline Accuracy)
- Source: `checks_6_7.md` — CHECK 6 section
- Add 1 primary comparison pair: Taysha
- This is a simpler check — escalation fires only when HTML table is extractable and has issues
- For image-embedded pipelines → auto YELLOW (manual review)

#### Check 7 (Red Flag Phrases)
- Source: `checks_6_7.md` — CHECK 7 section
- **MOST COMPLEX CHECK** — this is the one that escalated to RED for AARD
- Add 5 comparison pairs: Altamira (anchor), Graybug, Madrigal (three-part test), Scopus, OS Therapies
- Add three-tier phrase classification:
  - Tier 1: ALWAYS CHALLENGED (safe, effective, favorable safety profile, etc.)
  - Tier 2: CHALLENGED UNLESS SUPPORTED (well-tolerated, demonstrated)
  - Tier 3: CONTEXT-DEPENDENT (no SAEs, preliminary data)
- Add 4-step escalation prompt:
  - Step 1: instance-by-instance analysis (6 sub-questions per instance)
  - Step 2: global Madrigal three-part test across entire S-1
  - Step 3: web search
  - Step 4: final status via decision tree

---

## STEP 3: UPDATE `reference/comment_letter_excerpts.json`

Add NEW comparison pairs that are in the framework docs but NOT
already in this file. Currently 23 excerpts exist. The new docs
add approximately 15 more unique SEC comment letter excerpts.

New excerpts to add (check each — some may already exist under
different IDs):

| Company | Filing | Check | Source Doc |
|---------|--------|-------|-----------|
| Sensei Biotherapeutics | S-1 | 2 | check2_phase_labels.md |
| Nuvalent | S-1 | 2, 4 | check2_phase_labels.md, checks_3_4_5.md |
| Taysha Gene Therapies | S-1 | 2, 6 | check2_phase_labels.md, checks_6_7.md |
| Curanex Pharmaceuticals | S-1/A | 3, 4 | checks_3_4_5.md |
| Virpax Pharmaceuticals | S-1 | 3 | checks_3_4_5.md |
| Zenas BioPharma | S-1 | 4 | checks_3_4_5.md |
| Aerovate Therapeutics | S-1 | 5 | checks_3_4_5.md |
| Annovis Bio | 10-K | 5 | checks_3_4_5.md |
| Scopus BioPharma | S-1 | 7 | checks_6_7.md |
| OS Therapies | S-1 | 7 | checks_6_7.md |

Use the SAME JSON schema as existing excerpts. For entries that
have PLACEHOLDER text (the 17 + 14 = 31 unfilled slots), use
this pattern:

```json
{
  "id": "excerpt_preclinical_curanex_001",
  "topic": "preclinical_framing",
  "check_ids": ["preclinical_framing", "comparative_claims"],
  "company": "Curanex Pharmaceuticals",
  "filing_type": "S-1/A",
  "letter_date": "2024-07-17",
  "sec_comment_verbatim": "<<EXACT TEXT FROM checks_3_4_5.md>>",
  "s1_language_challenged": "[PLACEHOLDER — retrieve from SEC filing]",
  "what_sec_required": "<<summary>>",
  "verified": false,
  "_todo": "Fetch S-1 text from https://www.sec.gov/Archives/edgar/data/2025942/..."
}
```

Set `"verified": false` for any entry with unfilled placeholders.

**Also create `reference/placeholders_todo.md`** — the single
human-readable tracking file (see Architecture Decisions). Populate
it by scanning `checks_3_4_5.md` and `checks_6_7.md` for all
`[PLACEHOLDER` strings, extracting the company name, check number,
and SEC filing URL for each.

Also add the enforcement actions and case law as separate entries
in the `"enforcement_and_cases"` section (create it if it doesn't
exist):

| Authority | Type | Check | Source Doc |
|-----------|------|-------|-----------|
| SEC v. AVEO | Enforcement | 5 | checks_3_4_5.md |
| Tongue v. Sanofi | Case law (2d Cir.) | 5 | checks_3_4_5.md |

---

## STEP 4: UPDATE `reference/legal_framework.json`

The `legal_brief.md` is now the AUTHORITATIVE legal framework.
Update the JSON to match:

### 4A. Add the three-step structure

Add a top-level key `"analysis_structure"`:

```json
"analysis_structure": {
  "step_1": {
    "name": "Are the drug candidates described correctly?",
    "description": "Cross-cutting S-1 language checks",
    "sub_groups": {
      "A_basic_completeness": {
        "checks": [1, 2, 6],
        "legal_basis": "Rule 408 — completeness requirement"
      },
      "B_safety_efficacy_language": {
        "checks": [7, 3, 4],
        "legal_basis": "Safety/efficacy solely within FDA authority"
      },
      "C_fda_communications_maturity": {
        "checks": [5, 11],
        "legal_basis": "Balanced disclosure + AVEO enforcement"
      }
    }
  },
  "step_2": {
    "name": "Are the clinical studies described correctly?",
    "description": "Per-study comparison against ClinicalTrials.gov",
    "required_elements_table": "See reference/study_specific_output.md §II",
    "checks": [8, 9, 10, 11, "FDAAA_801"]
  },
  "step_3": {
    "name": "Does the overall pattern mislead?",
    "description": "Escalation assessment across all findings",
    "tests": ["omnicare", "rule_408_pattern", "matrixx_defense_blocker"]
  }
}
```

### 4B. Add missing case law entries

Verify these exist or add them:

- **Tongue v. Sanofi** (Second Circuit, 2024): Material negative FDA
  feedback must be disclosed. Source: `checks_3_4_5.md`, Check 5.
- **Matrixx Initiatives v. Siracusano** (Supreme Court, 2011):
  Should already exist. Verify the defense-blocker language is present.

### 4C. Add missing enforcement action

- **SEC v. AVEO Pharmaceuticals** (D. Mass., Case No. 16-cv-10607):
  Fraud charges for selective positive disclosure while omitting
  negative FDA feedback. Source: `checks_3_4_5.md`, Check 5.

---

## STEP 5: UPDATE `reference/guardrails.json`

The Layer 2 / escalation procedures need enrichment from
`legal_brief.md` §V-VII and `study_specific_output.md` §VI-VII.

### 5A. Omnicare test — verify/add three-part structure

From `legal_brief.md` §V:

```json
"omnicare_test": {
  "question": "Does the opinion statement (a) embed a false factual claim, or (b) omit known contrary facts?",
  "three_parts": {
    "part_1_embedded_fact": "Does the opinion contain or imply a factual assertion?",
    "part_2_omitted_contrary": "Were there known facts that cut against the opinion? Were they disclosed?",
    "part_3_basis": "Did the speaker have a reasonable basis for the opinion at the time?"
  },
  "output_scale": ["NO_CONCERN", "LOW", "MODERATE", "SIGNIFICANT"]
}
```

### 5B. Add Matrixx defense-blocker

From `legal_brief.md` §VI:

```json
"matrixx_defense_blocker": {
  "legal_basis": "Matrixx Initiatives v. Siracusano, 563 U.S. 27 (2011)",
  "principle": "There is no bright-line statistical significance threshold for materiality. A reasonable investor might find even non-statistically-significant adverse event data important.",
  "application": "When a company discloses small-trial results (N<50) without noting lack of statistical power, and a YELLOW or RED finding exists, note that Matrixx forecloses the defense that 'the results weren't statistically significant enough to matter.'"
}
```

---

## STEP 6: UPDATE `reference/red_flag_phrases.txt`

The current file has 21 lines. Update it to match the three-tier
classification from `checks_6_7.md`:

```
# RED FLAG PHRASES — Three-Tier Classification
# Tier 1: ALWAYS CHALLENGED (remove regardless of context)
# Tier 2: CHALLENGED UNLESS SUPPORTED (requires nearby data)
# Tier 3: CONTEXT-DEPENDENT (may be acceptable with proper framing)

## TIER 1 — ALWAYS CHALLENGED
safe
effective
safe and effective
safe and well tolerated
proven safety
proven efficacy
established safety
established efficacy
favorable safety profile
acceptable safety profile
demonstrated efficacy
demonstrated safety
superior
best-in-class

## TIER 2 — CHALLENGED UNLESS SUPPORTED
well-tolerated
well tolerated
demonstrated that .* was well tolerated
favorable tolerability
favorable safety and tolerability

## TIER 3 — CONTEXT-DEPENDENT
no serious adverse events
no SAEs
no treatment-related SAEs
preliminary
preliminary data
```

This needs to be parseable by the code — maintain the `##` headers
as section markers so `s1_parser.py` can classify each hit by tier.

---

## STEP 7: UPDATE `reference/study_specific_output.md`

This is already the full file from Step 1A. But make sure the
REQUIRED DISCLOSURE ELEMENTS table (§II) includes ALL of these
with their legal citations:

| Element | Authority |
|---------|-----------|
| Number of patients enrolled/treated | Immunocore (Dec. 14, 2020) |
| Participation criteria | Immunocore |
| Duration of treatment | Immunocore |
| Dosage information | Immunocore |
| Primary and secondary endpoints | Maze (Jul. 25, 2024) |
| Whether endpoints achieved | Maze |
| Statistical significance | OS Therapies (Mar. 27, 2023) |
| SAE description and count | Maze |
| Primary endpoint failure (if applicable) | Stealth (Nov. 21, 2018) |
| Statistical power disclosures | Coya (Nov. 4, 2022) |
| Data maturity label (if preliminary) | Sensei (Dec. 9, 2020) |
| Results on CTgov (within 12 mo) | FDAAA § 801 |

---

## STEP 8: UPDATE `SKILL.md`

The SKILL.md needs to reflect the new three-step legal structure.

### Changes:

1. **Section E (Checklist Preview)**: Reorganize the table to show
   the three-step grouping from `legal_brief.md`:

   ```
   STEP 1: Are the drug candidates described correctly?
     A. Basic Completeness: Checks 1, 2, 6
     B. Safety & Efficacy Language: Checks 7, 3, 4
     C. FDA Communications: Checks 5, 11

   STEP 2: Are the clinical studies described correctly?
     Checks 8, 9, 10, 11, FDAAA 801

   STEP 3: Does the overall pattern mislead?
     Omnicare, Rule 408 Pattern, Matrixx
   ```

2. **Section D (Legal Framework)**: Replace with the concise
   version from `legal_brief.md` §I (the "Statement of Law" and
   "How we derive the specific standards" sections).

3. **Phase 5 output format**: Replace with the improved UI from
   `study_specific_output.md`:
   - Summary table first (✓ ✗ ≈ ⬜ ⚠ icons)
   - Then unfurled detail per check
   - Full S-1 text in comparison cells (not just "Referenced")

4. **Phase 6 (Layer 2)**: Add the plain-English explanation from
   `legal_brief.md` §V-VII so a lawyer reading the SKILL.md
   understands what Layer 2 does and why.

5. **Reference Files section**: Add the five new files:
   ```
   - reference/legal_brief.md
   - reference/study_specific_output.md
   - reference/check2_phase_labels.md
   - reference/checks_3_4_5.md
   - reference/checks_6_7.md
   ```

---

## STEP 9: UPDATE `s1_checker_skill_spec_v4.md` → `s1_checker_skill_spec_v5.md`

Create a new spec version. Key changes:

1. Increment version to 5.0.

2. Add §3: "Legal Framework (Lawyer-Auditable)" — a condensed
   version of `legal_brief.md`. Not the full 802 lines, but the
   structural skeleton: the three steps, the checks within each
   step, the legal authorities for each check. Reference
   `legal_brief.md` for full text.

3. Update all 11 check definitions (§4-§14 or however structured)
   to include:
   - Comparison pairs with cross-reference to source doc
   - Severity spectrum
   - Escalation prompt architecture (the multi-step prompts)
   - Placeholder tracking (which pairs still need S-1 text)

4. Add §15: "Step 2 Output Specification" — reference
   `study_specific_output.md`, summarize the required elements
   table, the UI format, and the per-check structure.

5. Add §16: "Placeholder Tracking" — list all 31 unfilled
   S-1 text slots (17 from checks_3_4_5 + 14 from checks_6_7)
   with their SEC filing URLs for future retrieval.

6. Update the Reference File manifest to include all new files.

---

## STEP 10: UPDATE `scripts/s1_parser.py`

The parser needs two enhancements from `study_specific_output.md`:

### 10A. Red flag phrase tier classification

Currently the parser finds red flag phrases. Update it to also
classify each hit by tier (1, 2, 3) using the updated
`red_flag_phrases.txt` format with `##` section headers.

Add a method or update existing:

```python
def classify_red_flag_tier(phrase_match, context_window):
    """
    Returns: {
        "phrase": str,
        "tier": 1|2|3,
        "context_type": "CAUTIONARY"|"SUPPORTED"|"STANDALONE",
        "nearby_data": bool,  # True if SAE/AE data within 500 chars
        "section": str  # RISK_FACTORS, BUSINESS, SUMMARY, etc.
    }
    """
```

### 10B. Passage-to-trial linking

From `study_specific_output.md` §III.B — the parser needs to link
S-1 passages to specific trials using NCT IDs, trial titles, or
contextual clues (phase + indication + enrollment number).

Add a method:

```python
def link_passages_to_trials(passages, ctgov_trials):
    """
    For each passage, attempt to match to a specific CTgov trial.
    Returns passages annotated with trial_nct_id or 'UNMATCHED'.
    """
```

---

## STEP 11: UPDATE `scripts/comparison_builder.py`

### 11A. Required elements checklist

From `study_specific_output.md` §II — the comparison builder
needs to check for ALL required disclosure elements (the 12-item
table), not just the design elements it currently checks.

Add the required elements as a constant:

```python
REQUIRED_ELEMENTS = [
    {"element": "enrollment", "authority": "Immunocore (Dec. 14, 2020)"},
    {"element": "participation_criteria", "authority": "Immunocore"},
    {"element": "treatment_duration", "authority": "Immunocore"},
    {"element": "dosage", "authority": "Immunocore"},
    {"element": "primary_endpoint", "authority": "Maze (Jul. 25, 2024)"},
    {"element": "secondary_endpoints", "authority": "Maze"},
    {"element": "endpoints_achieved", "authority": "Maze"},
    {"element": "statistical_significance", "authority": "OS Therapies (Mar. 27, 2023)"},
    {"element": "sae_description_count", "authority": "Maze"},
    {"element": "primary_endpoint_failure", "authority": "Stealth (Nov. 21, 2018)"},
    {"element": "statistical_power", "authority": "Coya (Nov. 4, 2022)"},
    {"element": "data_maturity_label", "authority": "Sensei (Dec. 9, 2020)"},
]
```

### 11B. Improved output format

Update the comparison output to use the new UI format:

```
STATUS ICONS:
  ✓  = MATCH (GREEN)
  ✗  = MISMATCH (RED)
  ≈  = PARTIAL MATCH (YELLOW)
  ⬜ = UNVERIFIABLE
  ⚠  = ESCALATED / ALERT
```

The output should include FULL S-1 text for each element, not
just "Referenced" — quote the actual passage with section and
approximate page number.

---

## STEP 12: FDAAA 801 SUB-CHECK

From `study_specific_output.md` §V.E — this needs to be either
a standalone check or a clearly separated sub-check within the
trial-level analysis.

### Logic:

```python
def check_fdaaa_801(ctgov_trial):
    """
    FDAAA § 801 requires results posting within 12 months of
    primary completion date.

    Returns:
      GREEN: results posted
      RED: trial completed >12 months ago, no results posted
      YELLOW: trial completed <12 months ago, no results yet
      N/A: trial not yet completed
    """
    if trial.results_posted:
        return "GREEN"
    if trial.primary_completion_date:
        months_since = (today - trial.primary_completion_date).days / 30
        if months_since > 12:
            return "RED"
        elif months_since > 9:
            return "YELLOW"  # approaching deadline
    return "NA"
```

### Output:

```
FDAAA 801 Compliance
  Trial completed: {date}
  Months since completion: {N}
  Results posted: YES/NO
  Status: ✓/✗/⚠
  Note: {if RED → "FDAAA 801 requires results within 12 months.
         S-1 does not disclose this gap."}
```

---

## STEP 13: VALIDATION CHECKLIST

After all updates, verify:

- [ ] All 11 checks in `operationalized_checks.json` have `comparison_pairs` arrays
- [ ] Check 7 has all 5 comparison pairs and the 3-tier classification
- [ ] Check 5 has both enforcement (AVEO) and case law (Tongue) entries
- [ ] `red_flag_phrases.txt` has three tiers with `##` headers
- [ ] `legal_brief.md` is in `reference/` and cross-referenced from SKILL.md
- [ ] `study_specific_output.md` is in `reference/` and its required elements table matches `comparison_builder.py`
- [ ] FDAAA 801 sub-check exists in comparison_builder.py or a new module
- [ ] All placeholder entries have `"verified": false` and `"_todo"` with the SEC filing URL
- [ ] `SKILL.md` checklist preview shows the 3-step grouping
- [ ] New spec file `s1_checker_skill_spec_v5.md` exists
- [ ] `s1_parser.py` has tier classification for red flag phrases
- [ ] Comparison builder uses ✓ ✗ ≈ ⬜ ⚠ output format

---

## STEP 14: DO NOT DO THESE THINGS

1. **Do NOT delete existing comparison pairs** in comment_letter_excerpts.json — only ADD new ones.
2. **Do NOT change the Python script APIs** (command-line arguments) — only add new methods/constants.
3. **Do NOT fill the 31 placeholder slots** — those are explicitly deferred. Mark them clearly.
4. **Do NOT run or test the code** — this session is docs and reference file updates only.
5. **Do NOT change `edgar_fetch.py` or `ctgov_fetch.py`** — those scripts are stable.

---

## ORDER OF OPERATIONS

```
1. Read all 12 files (Step 0)
2. Copy 5 framework docs to reference/ (Step 1)
3. Update operationalized_checks.json (Step 2) — BIGGEST task
4. Update comment_letter_excerpts.json (Step 3)
5. Update legal_framework.json (Step 4)
6. Update guardrails.json (Step 5)
7. Update red_flag_phrases.txt (Step 6)
8. Update SKILL.md (Step 8)
9. Create s1_checker_skill_spec_v5.md (Step 9)
10. Update s1_parser.py — red flag tier classification (Step 10A)
11. Update s1_parser.py — passage-to-trial linking (Step 10B)
12. Update comparison_builder.py — required elements + UI (Step 11)
13. Add FDAAA 801 sub-check (Step 12)
14. Run validation checklist (Step 13)
```

Do steps 2-7 first (reference files), then 8-9 (docs), then
10-13 (code). Present a summary after each major step.

---

## ESTIMATED SCOPE

| Category | Files Changed | Estimated Lines Added |
|----------|--------------|----------------------|
| Reference JSON | 4 files | ~1500 lines |
| Reference MD | 5 files added | ~4786 lines (copied) |
| Spec docs | 2 files (SKILL.md + new v5 spec) | ~400 lines |
| Python scripts | 2 files | ~200 lines |
| **Total** | **13 files** | **~6886 lines** |

---

## ARCHITECTURE DECISIONS (RESOLVED)

### Q1: Full escalation prompts in JSON vs. reference by section?

**ANSWER: HYBRID.** `operationalized_checks.json` contains the
SKELETON — trigger conditions, step names, input/output contracts,
and slot variable names (e.g., `{{S1_TEXT}}`, `{{COMPARISON_PAIRS}}`).
The FULL prompt body text lives in the framework `.md` files in
`reference/`. The JSON references them by file + section anchor:

```json
"escalation_prompt": {
  "trigger": "combined_label_without_explanation",
  "source_doc": "reference/check2_phase_labels.md",
  "source_section": "ESCALATION_PROMPT_ARCHITECTURE",
  "steps": [
    {
      "step": 1,
      "name": "text_to_text_comparison",
      "executor": "llm",
      "prompt_source": "reference/check2_phase_labels.md#STEP_1",
      "slots": ["{{S1_TEXT}}", "{{COMPARISON_PAIRS}}"],
      "output_format": {"type": "json", "keys": ["classification", "explanation_present", "severity", "step1_assessment"]}
    }
  ]
}
```

**WHY:** The JSON stays machine-readable and under 1000 lines.
The prompts are human-readable in Markdown where a lawyer can
audit them. At runtime, the code reads the JSON skeleton, then
loads the full prompt text from the referenced `.md` section.
This means the `.md` files need consistent section anchors —
add `<!-- ANCHOR: STEP_1 -->` markers when copying them to
`reference/`.

### Q2: Placeholder tracking — separate file or `_todo` in JSON?

**ANSWER: BOTH.** Create `reference/placeholders_todo.md` as the
SINGLE tracking file a human reads. Keep `"verified": false` and
a minimal `"_todo"` field in the JSON for programmatic filtering.

The tracking file format:

```markdown
# PLACEHOLDER TRACKING
# 31 S-1 text slots that need to be filled from SEC filings

## STATUS SUMMARY
- Total: 31
- Filled: 0
- Remaining: 31

## CHECKS 3, 4, 5 (17 slots) — Source: checks_3_4_5.md
| # | Company | Check | Filing URL | Status |
|---|---------|-------|-----------|--------|
| 1 | Curanex | 3 | https://www.sec.gov/Archives/edgar/data/2025942/... | PENDING |
...

## CHECKS 6, 7 (14 slots) — Source: checks_6_7.md
| # | Company | Check | Filing URL | Status |
...
```

**WHY:** A lawyer or researcher filling these slots needs one
place to look, not to grep through JSON. The JSON `_todo` field
exists so code can `jq '.excerpts[] | select(.verified==false)'`
to find unfilled entries programmatically.

### Q3: Trial-level prompts — in operationalized_checks.json or separate?

**ANSWER: SAME FILE.** Checks 8-11 and FDAAA 801 already have
entries in `operationalized_checks.json`. Add their escalation
prompts there using the same hybrid pattern (skeleton in JSON,
full prompt in `reference/study_specific_output.md` with anchors).

**WHY:** One file = one schema = one place to look up any check.
Splitting into `trial_level_prompts.json` creates a second source
of truth for the same checks. The file is already organized by
`"pass": "pass_1_crosscutting"` vs `"pass": "pass_2_trial_level"`,
which is sufficient separation.
