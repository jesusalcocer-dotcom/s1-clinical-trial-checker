# STEP 2 OUTPUT FORMAT: PER-STUDY COMPARISON
# Specification for ClinicalTrials.gov vs. S-1 Analysis

---

## I. HOW STEP 2 IS STRUCTURED

Step 2 runs once PER CLINICAL TRIAL for each drug candidate. If
a candidate has three registered trials, Step 2 produces three
complete analysis blocks.

### Processing sequence:

```
1. GATHER     Collect ALL S-1 passages about this candidate
              (across all sections, all trials)

2. MATCH      Link each S-1 passage to a specific CTgov trial
              using NCT ID, trial title, or contextual clues

3. REQUIRE    For each trial, check the required disclosure
              elements (the "what they should include" list)

4. COMPARE    Element-by-element comparison: CTgov vs. S-1

5. ASSESS     Per-check analysis (8, 9, 10, 11, FDAAA 801)

6. DISPLAY    Summary table → unfurled detail per check
```


---

## II. WHAT THE S-1 MUST INCLUDE PER TRIAL

### The Required Disclosure Elements

These are not arbitrary — each is derived from a specific SEC
comment letter that required the information. The table below
lists what must be disclosed and the legal authority for each.

```
┌─────────────────────────┬──────────────────────────────────┐
│ REQUIRED ELEMENT        │ LEGAL SUPPORT                    │
├─────────────────────────┼──────────────────────────────────┤
│ Number of patients      │ Immunocore (Dec. 14, 2020):      │
│ enrolled and treated    │ "the number of patients (e.g.,   │
│                         │ number of patients enrolled and   │
│                         │ treated)"                         │
├─────────────────────────┼──────────────────────────────────┤
│ Participation criteria  │ Immunocore: "the criteria for    │
│                         │ participation in the study"       │
├─────────────────────────┼──────────────────────────────────┤
│ Duration of treatment   │ Immunocore: "duration of         │
│                         │ treatment"                        │
├─────────────────────────┼──────────────────────────────────┤
│ Dosage information      │ Immunocore: "dosage information" │
├─────────────────────────┼──────────────────────────────────┤
│ Primary and secondary   │ Maze (Jul. 25, 2024): "describe  │
│ endpoints               │ any primary and secondary        │
│                         │ endpoints"                        │
├─────────────────────────┼──────────────────────────────────┤
│ Whether endpoints       │ Maze: "and whether they were     │
│ were achieved           │ achieved"                         │
├─────────────────────────┼──────────────────────────────────┤
│ Statistical             │ OS Therapies (Mar. 27, 2023):    │
│ significance            │ "whether the reported results     │
│                         │ were or were not statistically    │
│                         │ significant"                      │
├─────────────────────────┼──────────────────────────────────┤
│ SAE description         │ Maze: "describe them and quantify│
│ and count               │ the number of each type of event"│
├─────────────────────────┼──────────────────────────────────┤
│ Primary endpoint        │ Stealth (Nov. 21, 2018):         │
│ failure (if applicable) │ "disclose that the Phase 2       │
│                         │ clinical trial did not meet its   │
│                         │ primary endpoint"                 │
├─────────────────────────┼──────────────────────────────────┤
│ Statistical power       │ Coya (Nov. 4, 2022): "clarify,   │
│ disclosures             │ if true, that the ... trials were │
│                         │ not powered for statistical       │
│                         │ significance"                     │
├─────────────────────────┼──────────────────────────────────┤
│ Data maturity label     │ Sensei (Dec. 9, 2020): "present  │
│ (if preliminary)        │ a balanced view of the ongoing    │
│                         │ clinical trial and the meaning of │
│                         │ the results" (re: 9-patient data) │
├─────────────────────────┼──────────────────────────────────┤
│ Results on CTgov        │ FDAAA § 801 (42 U.S.C.           │
│ (within 12 mo. of       │ § 282(j)(3)(C)): results must be │
│ primary completion)     │ posted within 12 months           │
└─────────────────────────┴──────────────────────────────────┘
```


---

## III. TECHNICAL EXTRACTION PROCESS

### A. Gathering All Candidate Text

Before any comparison, we extract EVERY passage in the S-1 that
mentions the candidate. This matters because information about a
single trial may be scattered across multiple sections.

```
s1_parser.py → _extract_passages_for_name(candidate_name)

INPUT:  Full S-1 text + candidate name (e.g., "ARD-101")
PROCESS:
  1. Regex finds all occurrences of the name
  2. For each occurrence, extracts 800-char context window
     (400 chars before and after the name)
  3. Classifies section using header detection:
     PROSPECTUS_SUMMARY, RISK_FACTORS, BUSINESS,
     USE_OF_PROCEEDS, MD&A, GOVERNMENT_REGULATION
  4. Estimates page number: char_offset / 3000

OUTPUT: JSON array of passages:
  {
    "text": "[800-char context window]",
    "section": "BUSINESS",
    "page_approx": 45,
    "char_offset": 135000,
    "nct_ids_nearby": ["NCT06203379"]
  }
```

**Why 800 chars?** The SEC comment letters consistently challenge
language "on page X and elsewhere" — meaning the concern is about
what appears NEAR the claim, not just the claim itself. The 800-
char window captures sufficient surrounding context to determine
whether supporting data, caveats, or qualifying language appears
nearby.

### B. Matching Passages to Specific Trials

A company may have multiple trials for the same candidate. Each
S-1 passage must be linked to the correct CTgov record.

```
comparison_builder.py → _match_passages_to_trials()

INPUT:  S-1 passages + CTgov trial records
PROCESS:
  1. If passage contains NCT ID → direct match
  2. If passage mentions trial phase + indication → match by
     phase/condition overlap with CTgov records
  3. If passage is ambiguous → mark as "CANDIDATE_GENERAL"
     (applies to the candidate overall, not a specific trial)

OUTPUT: Passages grouped by trial:
  {
    "NCT06203379": [passage1, passage2, ...],
    "NCT_UNKNOWN": [passage_a, passage_b, ...],
    "CANDIDATE_GENERAL": [passage_x, passage_y, ...]
  }
```

### C. Element-by-Element Comparison

For each trial, we compare specific CTgov fields against the
matched S-1 passages.

```
comparison_builder.py → _compare_elements(trial, passages)

For each element:
  1. Extract the GROUND TRUTH from CTgov JSON
     (e.g., designModule.phases → "PHASE2")
  2. Search S-1 passages for the corresponding claim
     (e.g., regex for "Phase 2", "phase 2", "Phase II")
  3. Compare:
     - Values match → ✓ MATCH
     - S-1 says something different → ✗ MISMATCH
     - S-1 doesn't mention it → — ABSENT
     - CTgov has no data to compare → ⬜ UNVERIFIABLE
```


---

## IV. OUTPUT FORMAT

### A. Summary Table (appears FIRST)

The summary shows one row per check. This is what the lawyer sees
at a glance before deciding what to drill into.

```
┌──────────────────────────────┬────────┬───────────────────────┐
│ Check                        │ Status │ Finding               │
├──────────────────────────────┼────────┼───────────────────────┤
│ 8. Trial Design Match        │   ✓    │ Design elements match │
│ 9. Endpoint Hierarchy        │   ✓    │ Primary endpoint      │
│                              │        │ appropriately          │
│                              │        │ acknowledged           │
│10. Safety Data Match         │   ⬜   │ No CTgov results to   │
│                              │        │ verify against         │
│11. Data Maturity             │   ✓    │ Data labeled as       │
│                              │        │ preliminary            │
│ FDAAA 801                    │   ✗    │ Trial completed >12   │
│                              │        │ months ago; no results │
│                              │        │ posted                 │
└──────────────────────────────┴────────┴───────────────────────┘

STATUS KEY:
  ✓  = Pass (GREEN)
  ✗  = Fail (RED)
  ≈  = Attention needed (YELLOW)
  ⬜ = Unverifiable (cannot confirm)
  ⚠  = Escalated to LLM for analysis
```

### B. Unfurled Detail — Check 8: Trial Design Match

When the lawyer clicks into Check 8, they see the element-by-
element comparison. The "S-1 Says" column contains the FULL
relevant text, not a summary.

```
TRIAL: NCT06203379 — Phase 2a Open-Label Study of ARD-101
       in Prader-Willi Syndrome

┌──────────────┬────────────────────┬────────────────────────────────────┬────────┐
│ Element      │ ClinicalTrials.gov │ S-1 Says                           │ Status │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Phase        │ PHASE2             │ "We initiated our Phase 2a         │   ✓    │
│              │                    │ clinical trial of ARD-101 in       │        │
│              │                    │ individuals with Prader-Willi      │        │
│              │                    │ Syndrome, or PWS, in March 2024."  │        │
│              │                    │ (BUSINESS, p.~45)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Masking      │ NONE               │ "open-label"                       │   ✓    │
│              │ (open-label)       │ (BUSINESS, p.~46)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Allocation   │ NA                 │ "single-arm"                       │   ✓    │
│              │ (single-arm)       │ (BUSINESS, p.~46)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Enrollment   │ 19 (actual)        │ "In this Phase 2a clinical trial,  │   ✓    │
│              │                    │ we enrolled 19 subjects with        │        │
│              │                    │ genetically confirmed PWS..."       │        │
│              │                    │ (BUSINESS, p.~47)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Primary EP   │ Incidence of       │ "The primary endpoint of the       │   ✓    │
│              │ treatment-         │ Phase 2a clinical trial was safety  │        │
│              │ emergent AEs       │ as measured by the incidence of     │        │
│              │ (safety)           │ treatment-emergent adverse events." │        │
│              │                    │ (BUSINESS, p.~47)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Results      │ NO                 │ N/A — S-1 presents results but     │   ✗    │
│ posted       │                    │ CTgov has none posted.              │ FDAAA  │
│              │                    │ Trial completed 2024-09-24.         │  801   │
│              │                    │ (~16 months ago)                   │        │
└──────────────┴────────────────────┴────────────────────────────────────┴────────┘
```

**NOTES ON THE "S-1 SAYS" COLUMN:**

The S-1 Says column always contains:
1. The FULL relevant quote (enough to see context)
2. The section where it appears (in parentheses)
3. The approximate page number

If the S-1 does not mention an element, the column says:
"Not mentioned. Searched all [N] passages for [search terms].
No reference to [element] found."

If the S-1 mentions the element ambiguously, the column shows
the full passage and notes the ambiguity.


---

## V. INDIVIDUAL CHECK SPECIFICATIONS

Each check below explains: what it measures, what data it uses,
how the LLM is prompted (if escalated), and the legal authority.

### CHECK 8: TRIAL DESIGN MATCH

**What it measures:** Whether the S-1's description of trial
structure matches the federal registry record. This is a factual
accuracy check — did the company describe its own trial correctly?

**Data sources:**
- CTgov: `protocolSection.designModule` (phases, designInfo,
  enrollmentInfo)
- CTgov: `protocolSection.outcomesModule` (primaryOutcomes,
  secondaryOutcomes)
- S-1: All candidate passages matched to this trial

**Elements compared:**

| Element | CTgov field | S-1 search terms |
|---------|------------|-----------------|
| Phase | `designModule.phases` | "Phase 1", "Phase 2", etc. |
| Masking | `designInfo.maskingInfo.masking` | "open-label", "single-blind", "double-blind" |
| Allocation | `designInfo.allocation` | "randomized", "single-arm", "non-randomized" |
| Model | `designInfo.interventionModel` | "parallel", "crossover", "sequential" |
| Enrollment | `enrollmentInfo.count` | digits near "enroll", "patient", "subject" |
| Primary EP | `outcomesModule.primaryOutcomes[].measure` | endpoint-specific keywords |
| Secondary EP | `outcomesModule.secondaryOutcomes[].measure` | endpoint-specific keywords |

**Status determination (per element):**
- ✓ MATCH: S-1 value matches CTgov (with normalization)
- ✗ MISMATCH: S-1 states something contradicting CTgov
- — ABSENT: S-1 does not mention this element
- ⬜ N/A: CTgov does not contain this field

**Overall check status:**
- All ✓ → ✓ GREEN
- Any — (ABSENT) → ≈ YELLOW (may trigger escalation)
- Any ✗ (MISMATCH) → ✗ RED (always triggers escalation)

**Escalation prompt (if ABSENT or MISMATCH):**

```
SLOT 1 — ELEMENT AND CTGOV VALUE:
"The ClinicalTrials.gov record for [NCT ID] shows
[element] = [value]."

SLOT 2 — ALL S-1 PASSAGES FOR THIS TRIAL:
[Full text of every passage matched to this trial,
with section and page.]

SLOT 3 — SEC COMMENT LETTER TEXT:
Immunocore (Dec. 14, 2020): "please disclose, as
applicable, the number of patients (e.g., number of
patients enrolled and treated and the criteria for
participation in the study); duration of treatment,
dosage information; and the specific endpoints
established by the trial protocol."

Maze (Jul. 25, 2024): "Please provide the number of
volunteers that enrolled in your Phase 1 trial for
MZE001, describe any primary and secondary endpoints
and whether they were achieved."

SLOT 4 — QUESTION:
"The ClinicalTrials.gov record shows [element] =
[value]. The S-1 [states X / does not mention this
element]. Based on the SEC comment letters above, is
this omission likely to be material to investors?
Consider: (a) Is this an element the SEC has
specifically required? (b) Does the omission affect
an investor's understanding of the trial design?"
```


---

### CHECK 9: ENDPOINT HIERARCHY — "The Harkonen Check"

**What it measures:** Whether the S-1 gives appropriate prominence
to the primary endpoint. Specifically: does the S-1 lead with
secondary or exploratory results while burying the primary —
especially if the primary endpoint failed?

**Why this is the highest-stakes check:** This pattern resulted
in a criminal conviction (Harkonen) and a $20M civil penalty
(Clovis). It is the disclosure pattern most likely to produce
personal liability.

**Data sources:**
- CTgov: `outcomesModule.primaryOutcomes` and `secondaryOutcomes`
- S-1: All candidate passages, especially in Prospectus Summary
  and Business sections

**Assessment logic:**

```
Step 1: Extract CTgov primary and secondary endpoints.
        What was the trial DESIGNED to measure?

Step 2: Find the S-1's "headline finding" — the FIRST efficacy
        result mentioned in the Prospectus Summary or Business
        section. This is what investors see first.
        Search terms: response rate, ORR, PFS, OS, complete
        remission, "met...endpoint", "achieved...endpoint",
        percentage results

Step 3: Classify the headline finding:
        Does it match a PRIMARY endpoint? → OK
        Does it match a SECONDARY endpoint? → FLAG
        Is it from a post-hoc/exploratory analysis? → RED FLAG

Step 4: Check whether the primary endpoint is discussed
        ANYWHERE in the S-1 (not just the headline):
        - Primary discussed prominently → OK
        - Primary discussed but buried → YELLOW
        - Primary NOT discussed → RED (Harkonen pattern)
```

**Status determination:**
- ✓ GREEN: Headline matches primary endpoint, or primary is
  prominently discussed
- ≈ YELLOW: Headline is secondary but primary is discussed
  elsewhere
- ✗ RED: Primary is absent or buried while secondary leads

**Escalation prompt (if YELLOW or RED):**

```
SLOT 1 — S-1 HEADLINE PASSAGE:
"[The first efficacy result in Prospectus Summary or
Business section — full quote, section, page]"

SLOT 2 — CTGOV ENDPOINTS:
"Primary: [measure text from CTgov]
 Secondary: [measure text from CTgov]"

SLOT 3 — WHETHER PRIMARY DISCUSSED ELSEWHERE:
"[Yes/No. If yes, quote the passage, section, page.
If no, state: 'No reference to primary endpoint found
in any of [N] candidate passages.']"

SLOT 4 — HARKONEN COMPARISON:
"In United States v. Harkonen (9th Cir. 2013), the
trial primary endpoint (overall survival) failed
(p=0.52). The CEO's press release led with a post-hoc
subgroup that appeared significant (p=0.004). The
primary failure was mentioned but buried. Result:
criminal wire fraud conviction."

SLOT 5 — CLOVIS COMPARISON:
"In SEC v. Clovis Oncology (2018), the company reported
a 60% objective response rate using unconfirmed
responses — the confirmed ORR was only 28%. The non-
standard metric was not disclosed. Result: $20M penalty."

SLOT 6 — QUESTION:
"(a) Is the S-1's headline finding from a primary or
secondary endpoint?
(b) If secondary: is the primary endpoint given
appropriate prominence elsewhere?
(c) How closely does this pattern match Harkonen
(primary buried, secondary leads)?
(d) Are any metrics non-standard or unconfirmed
per Clovis?"
```


---

### CHECK 10: SAFETY DATA MATCH

**What it measures:** Whether the S-1's safety characterizations
are supported by the actual adverse event data. This check
requires CTgov results to be posted — if they are not, the
S-1's safety claims cannot be independently verified.

**Data sources:**
- CTgov: `resultsSection.adverseEventsModule` (if posted):
  `seriousNumAffected`, `otherNumAffected`, frequency tables
- S-1: All passages containing safety characterizations
  (identified by Check 7 red flag phrase scan)

**Assessment logic:**

```
Step 1: Are results posted on CTgov?
        YES → proceed to comparison
        NO  → status = ⬜ UNVERIFIABLE
              (S-1 claims cannot be confirmed or denied)

Step 2: Extract CTgov AE data:
        - Total SAEs (count and rate)
        - Total AEs (count and rate)
        - Most common AEs (by frequency)

Step 3: For each S-1 safety characterization:
        - "well-tolerated": Does SAE rate support this?
          SAE rate >20% → likely CONTRADICTED
          SAE rate <5% and no drug-related SAEs → SUPPORTED
        - "no SAEs": Does CTgov confirm zero SAEs?
        - "favorable safety profile": Does AE profile
          support this characterization?

Step 4: Apply Madrigal three-part test:
        (a) Is the characterization true per the data?
        (b) Are SAEs disclosed in the S-1?
        (c) If SAEs occurred, is the basis explained?
```

**Status determination:**
- ✓ GREEN: Safety characterizations supported by CTgov data
- ≈ YELLOW: Partially supported or data is ambiguous
- ✗ RED: Safety characterization contradicted by CTgov data
- ⬜ UNVERIFIABLE: No CTgov results posted; S-1 claims cannot
  be independently confirmed

**Escalation prompt (if CONTRADICTED or UNVERIFIABLE with
aggressive S-1 claims):**

```
SLOT 1 — S-1 SAFETY CHARACTERIZATION:
"[Full quote of the safety claim, section, page.
E.g., 'ARD-101 has been generally well tolerated
in clinical trials to date.' (PROSPECTUS SUMMARY,
p.~3)]"

SLOT 2 — CTGOV AE DATA (if available):
"SAEs: [count]/[total] ([rate]%)
 AEs:  [count]/[total] ([rate]%)
 Most common: [list]"
OR:
"No results posted on ClinicalTrials.gov. Trial
completed [date]. S-1 claims cannot be independently
verified."

SLOT 3 — SEC COMMENT LETTER TEXT:
Altamira (Feb. 24, 2023): "[full Altamira text]"
Madrigal (Nov. 21, 2023): "[full three-part test]"

SLOT 4 — QUESTION:
"(a) Does the available data (or lack thereof) support
the S-1's safety characterization?
(b) Apply the Madrigal three-part test: Is the claim
true? Are SAEs disclosed? Is the basis explained?
(c) If no CTgov results are posted: does the S-1's
level of confidence in its safety characterization
match the available evidentiary basis?"
```


---

### CHECK 11: DATA MATURITY (per study)

**What it measures:** Whether the S-1 appropriately labels data
as preliminary, interim, or topline — and whether it applies
conclusory verbs ("demonstrated", "established", "proven") to
data that is not final or independently verified.

**Data sources:**
- CTgov: `overallStatus`, `statusModule.completionDateStruct`,
  `hasResults`
- S-1: All candidate passages, searching for conclusory verbs
  and data-maturity labels

**Assessment logic:**

```
Step 1: Determine trial status from CTgov:
        - RECRUITING → data is interim at best
        - COMPLETED → data may be final but unverified
          if results not posted
        - COMPLETED + RESULTS POSTED → data is final
          and publicly available

Step 2: Scan S-1 passages for conclusory verbs:
        "demonstrated", "established", "proven",
        "confirmed", "showed" (in conclusory context)

Step 3: Scan for data-maturity labels:
        "preliminary", "topline", "interim", "subject
        to change", "unpublished", "not yet verified"

Step 4: Cross-reference:
        IF conclusory verb + recruiting trial → RED
        IF conclusory verb + completed/no results → YELLOW
        IF conclusory verb + data labeled preliminary → OK
        IF data labeled as preliminary → GREEN
```

**Status determination:**
- ✓ GREEN: Data properly labeled as preliminary, or conclusory
  language accompanied by maturity caveats
- ≈ YELLOW: Conclusory language for completed trial without
  posted results
- ✗ RED: Conclusory language for ongoing trial, or data presented
  as final when it is not

**Escalation prompt (if YELLOW or RED):**

```
SLOT 1 — S-1 PASSAGE WITH CONCLUSORY LANGUAGE:
"[Full quote, section, page]"

SLOT 2 — CTGOV TRIAL STATUS:
"Trial [NCT ID]:
 Status: [RECRUITING / COMPLETED / TERMINATED]
 Primary completion: [date]
 Results posted: [YES / NO]
 Time since completion: [N months]"

SLOT 3 — SEC COMMENT LETTER TEXT:
Stealth BioTherapeutics (Nov. 21, 2018): "Please
expand your discussion... to disclose that the
Phase 2 clinical trial did not meet its primary
endpoint."

Sensei (Dec. 9, 2020): "given that only nine patients
have been evaluated to date, please revise your
disclosure in the Summary to present a balanced view
of the ongoing clinical trial and the meaning of the
results."

SLOT 4 — QUESTION:
"(a) Is the S-1's use of [conclusory verb] appropriate
given that the trial is [status] and results [are/are
not] posted on ClinicalTrials.gov?
(b) Does the S-1 label this data as preliminary or
subject to change?
(c) Compare to the SEC's concern in Sensei (9 patients
= too little data for conclusory characterization) and
Stealth (primary failure must be disclosed)."
```


---

### FDAAA 801 COMPLIANCE

**What it measures:** Whether the company has complied with the
federal requirement to post trial results on ClinicalTrials.gov
within 12 months of primary completion — and whether the S-1
discloses any non-compliance.

**Legal basis:** 42 U.S.C. § 282(j)(3)(C) requires posting within
12 months. Non-compliance subjects the company to civil monetary
penalties of up to $10,000/day (42 U.S.C. § 282(j)(5)(C)). Under
Rule 408, potential liability for non-compliance with a federal
reporting obligation is material information that may need to be
disclosed.

**Data sources:**
- CTgov: `statusModule.completionDateStruct.date` (primary
  completion date)
- CTgov: `hasResults` (boolean)
- Current date

**Assessment logic:**

```
Step 1: Extract primary completion date from CTgov
Step 2: Calculate months since completion
Step 3: Check whether results are posted

IF months_since_completion <= 12:
  → N/A (still within statutory period)

IF months_since_completion > 12 AND results posted:
  → ✓ GREEN (compliant)

IF months_since_completion > 12 AND results NOT posted:
  → ✗ RED
  → Check whether S-1 discloses this non-compliance:
    IF S-1 mentions FDAAA 801 gap → ≈ YELLOW
    IF S-1 does not mention → ✗ RED
```

**Status determination:**
- ✓ GREEN: Results posted, or within 12-month window
- ≈ YELLOW: Non-compliant but S-1 discloses
- ✗ RED: Non-compliant and S-1 silent

**This check does NOT escalate to LLM.** It is a binary factual
check: either results are posted within 12 months or they are not.
The only judgment call is whether the S-1's silence about non-
compliance is material — and the Rule 408 standard (material
information necessary to make statements not misleading) provides
the answer.


---

## VI. COMPLETE OUTPUT EXAMPLE (ARD-101, NCT06203379)

### STEP 2 SUMMARY — ARD-101

```
CANDIDATE:  ARD-101
TRIAL:      NCT06203379 — Phase 2a Open-Label Study in PWS
SOURCE:     ClinicalTrials.gov (last updated [date])
S-1 TEXT:   [N] passages across [sections] matched to this trial

┌──────────────────────────────┬────────┬───────────────────────────┐
│ Check                        │ Status │ Finding                   │
├──────────────────────────────┼────────┼───────────────────────────┤
│ 8. Trial Design Match        │   ✓    │ Design elements match     │
├──────────────────────────────┼────────┼───────────────────────────┤
│ 9. Endpoint Hierarchy        │   ✓    │ Primary endpoint (safety/ │
│                              │        │ TEAE) acknowledged; HQ-CT │
│                              │        │ appropriately described   │
│                              │        │ as efficacy evaluation    │
├──────────────────────────────┼────────┼───────────────────────────┤
│10. Safety Data Match         │   ⬜   │ No results posted on      │
│                              │        │ CTgov. S-1 claims "no     │
│                              │        │ SAEs" and "well-tolerated"│
│                              │        │ cannot be independently   │
│                              │        │ verified.                 │
├──────────────────────────────┼────────┼───────────────────────────┤
│11. Data Maturity             │   ✓    │ S-1 explicitly labels     │
│                              │        │ Phase 2a data as          │
│                              │        │ "preliminary, unpublished │
│                              │        │ data and may be subject   │
│                              │        │ to change"               │
├──────────────────────────────┼────────┼───────────────────────────┤
│ FDAAA 801                    │   ✗    │ Trial completed           │
│                              │        │ 2024-09-24 (~16 mo. ago). │
│                              │        │ No results posted.        │
│                              │        │ FDAAA 801 requires within │
│                              │        │ 12 months. S-1 does not   │
│                              │        │ disclose this gap.        │
└──────────────────────────────┴────────┴───────────────────────────┘
```

### UNFURLED: Check 8 — Trial Design Match

```
┌──────────────┬────────────────────┬────────────────────────────────────┬────────┐
│ Element      │ ClinicalTrials.gov │ S-1 Says                           │ Status │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Phase        │ PHASE2             │ "We initiated our Phase 2a         │   ✓    │
│              │                    │ clinical trial of ARD-101 in       │        │
│              │                    │ individuals with Prader-Willi      │        │
│              │                    │ Syndrome, or PWS, in March 2024."  │        │
│              │                    │ (BUSINESS, p.~45)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Masking      │ NONE               │ "This was an open-label, single-   │   ✓    │
│              │ (open-label)       │ arm study evaluating..."           │        │
│              │                    │ (BUSINESS, p.~46)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Allocation   │ NA                 │ "...single-arm study..."           │   ✓    │
│              │ (single-arm)       │ (BUSINESS, p.~46)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Enrollment   │ 19 (actual)        │ "In this Phase 2a clinical trial,  │   ✓    │
│              │                    │ we enrolled 19 subjects with        │        │
│              │                    │ genetically confirmed PWS across    │        │
│              │                    │ four clinical trial sites."        │        │
│              │                    │ (BUSINESS, p.~47)                  │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Primary EP   │ Incidence of       │ "The primary endpoint of the       │   ✓    │
│              │ treatment-         │ Phase 2a clinical trial was safety  │        │
│              │ emergent           │ as measured by the incidence of     │        │
│              │ adverse            │ treatment-emergent adverse events." │        │
│              │ events             │ (BUSINESS, p.~47)                  │        │
│              │ (safety)           │                                    │        │
├──────────────┼────────────────────┼────────────────────────────────────┼────────┤
│ Results      │ NOT POSTED         │ S-1 presents safety and efficacy   │   ✗    │
│ posted       │                    │ data from this trial, but CTgov    │ FDAAA  │
│              │                    │ shows no results. Trial primary     │  801   │
│              │                    │ completion: 2024-09-24.            │        │
│              │                    │ Months elapsed: ~16.               │        │
└──────────────┴────────────────────┴────────────────────────────────────┴────────┘
```

### UNFURLED: Check 9 — Endpoint Hierarchy

**What was measured:** Whether the S-1's headline efficacy finding
comes from the primary endpoint, and whether the primary endpoint
is given appropriate prominence.

**CTgov primary endpoint:** Incidence of treatment-emergent
adverse events (TEAE) — this is a SAFETY endpoint.

**CTgov secondary endpoints:** [List from CTgov — e.g., food-
related behaviors, body composition, hormonal markers]

**S-1 headline finding:**
[PLACEHOLDER — the first efficacy result mentioned in the
Prospectus Summary. E.g., "ARD-101 demonstrated improvements in
hyperphagia..." — need exact text with section and page.]

**Assessment:** The primary endpoint is a safety endpoint (TEAE
incidence). The S-1 acknowledges this and characterizes the HQ-CT
(Hyperphagia Questionnaire for Clinical Trials) results as an
efficacy evaluation within a safety-primary trial. This is
appropriate framing — the S-1 is not leading with a secondary
endpoint while burying a failed primary.

**Status:** ✓ GREEN

---

### UNFURLED: Check 10 — Safety Data Match

**What was measured:** Whether the S-1's safety characterizations
can be verified against ClinicalTrials.gov data.

**CTgov results:** NOT POSTED. No adverse event data available
for comparison.

**S-1 safety characterizations (from Check 7 scan):**
[PLACEHOLDER — list each safety claim found in candidate passages
with full quote, section, page. E.g.:
- "ARD-101 has been generally well tolerated..." (SUMMARY, p.~3)
- "No SAEs were reported..." (BUSINESS, p.~48)
- etc.]

**Assessment:** Because CTgov results are not posted, these claims
cannot be independently verified. The S-1 is the only source for
this safety data. This does not mean the claims are false — it
means they depend entirely on company-reported data that has not
been subjected to the public reporting requirements of FDAAA 801.

**Connection to Check 7:** The 9 standalone "well-tolerated"
instances flagged in Check 7 are the same claims that cannot be
verified here. The combination — aggressive safety language (RED
from Check 7) + inability to verify (UNVERIFIABLE from Check 10)
— feeds into Step 3's Omnicare analysis.

**Status:** ⬜ UNVERIFIABLE

---

### UNFURLED: Check 11 — Data Maturity

**What was measured:** Whether the S-1 appropriately labels its
clinical data as preliminary.

**CTgov trial status:** COMPLETED (primary completion 2024-09-24).
Results NOT posted.

**S-1 data labeling:**
[PLACEHOLDER — exact quote where S-1 labels data as preliminary.
E.g., "The data presented herein represent preliminary, unpublished
data and may be subject to change following further analysis."
(BUSINESS, p.~48)]

**Conclusory verb scan:**
[PLACEHOLDER — list any conclusory verbs found in passages about
this trial. E.g., "demonstrated improvements in..." — is this
conclusory or descriptive?]

**Assessment:** The S-1 includes an explicit preliminary data
caveat. This satisfies the Sensei standard (balanced view of
limited data) and distinguishes the S-1 from the Stealth pattern
(failure to disclose limitations).

**Status:** ✓ GREEN

---

### UNFURLED: FDAAA 801

**What was measured:** Whether the company has posted trial results
on ClinicalTrials.gov within the statutory 12-month window.

**Facts:**
- Trial: NCT06203379
- Primary completion date: 2024-09-24
- Current date: 2026-02-06
- Months since completion: ~16
- Results posted: NO
- Statutory deadline: 12 months (expired ~Sep. 2025)

**S-1 disclosure of this gap:**
[PLACEHOLDER — search S-1 for any mention of FDAAA 801, results
posting requirements, or this specific non-compliance. If found,
quote. If not found, state: "No reference to FDAAA 801 compliance
or results posting requirements found in any S-1 passage."]

**Legal analysis:**
Non-compliance with FDAAA 801 exposes the company to civil
monetary penalties of up to $10,000/day. This is a contingent
liability that may be material to investors. Under Rule 408, if
the S-1 does not disclose this potential liability, the omission
may make the required statements misleading — particularly in
light of the S-1's affirmative claims about trial results that
cannot be verified against the public record.

**Status:** ✗ RED


---

## VII. HOW CHECKS 8-11 CONNECT TO STEP 3

The per-study findings feed directly into the Step 3 escalation:

```
Check 7  (Step 1): 9 standalone "well-tolerated" → RED
Check 10 (Step 2): Same claims unverifiable → ⬜
Check 11 (Step 2): Data labeled preliminary → ✓
FDAAA 801 (Step 2): Results not posted → ✗

STEP 3 INPUTS:
┌─────────────────────────────────────────┬──────────┐
│ Finding                                 │ Direction│
├─────────────────────────────────────────┼──────────┤
│ 9 standalone "well-tolerated"           │ FAVORS   │
│ 2 affirmative "safe"                    │ FAVORS   │
│ Safety claims unverifiable (no CTgov)   │ FAVORS   │
│ FDAAA 801 non-compliance undisclosed    │ FAVORS   │
│ Data labeled as preliminary             │ NEUTRAL  │
│ Primary endpoint acknowledged           │ NEUTRAL  │
│ Trial design accurately described       │ NEUTRAL  │
│ FDA denial disclosed alongside ODD      │ NEUTRAL  │
└─────────────────────────────────────────┴──────────┘

One-sided calculation:
  FAVORS COMPANY: 4
  NEUTRAL: 4
  Total: 8
  One-sided percentage: 4/8 = 50% → YELLOW threshold

→ Step 3 Rule 408 Pattern Analysis: YELLOW
  "The omissions and characterization choices show a
  pattern — aggressive safety language (Check 7) cannot
  be verified because results are not posted (Check 10),
  and the company has not disclosed its FDAAA 801 non-
  compliance (FDAAA 801). Each finding individually
  might be borderline, but taken together, every gap
  favors the company."
```

This is how Layer 2 works: it takes the individual findings
from Steps 1 and 2, classifies their direction, and asks whether
the pattern itself is misleading — even if no single finding would
be dispositive alone.
