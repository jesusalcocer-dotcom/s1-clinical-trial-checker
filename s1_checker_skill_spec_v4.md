# S-1 Clinical Trial Disclosure Checker &mdash; Specification v4

**Author**: Jesus Alcocer, Norm.ai
**Version**: 4.0
**Date**: 2026-02-06

---

## 1. Purpose

This tool checks whether a biotech company's S-1 (or F-1) registration
statement adequately discloses clinical trial information by comparing
the S-1 text against the public record on ClinicalTrials.gov.

It identifies risk areas for attorney review. It does **not** determine
liability, materiality, or legal exposure.

---

## 2. Architecture: Operationalized Decision Tree

### The Core Change from Prior Versions

The legal framework is no longer a reference document the LLM "reads and
reasons about." It is an **operationalized decision tree** where each
check has:

- **Concrete inputs** &mdash; what text to extract
- **Concrete comparisons** &mdash; what to compare against, including
  actual precedent language
- **Concrete outputs** &mdash; binary or scored, with clear thresholds
- **Escalation rules** &mdash; when to call the LLM for further
  reasoning, and with what specific inputs

Every check is a function:

```
check(s1_text, standard, precedent_language) -> {status, evidence, reasoning}
```

This is **auditable**: you can see exactly what code did, what the LLM
was asked, and what specific precedent language was compared.

### Layer 1 &rarr; Layer 2

```
LAYER 1: CONCRETE CHECKS (always run)
+-- Check 1:  Basic Disclosure            -> findings[]
+-- Check 2:  Phase Labels                -> findings[]
+-- Check 3:  Preclinical Framing         -> findings[]
+-- Check 4:  Comparative Claims          -> findings[]
+-- Check 5:  FDA Communications          -> findings[]
+-- Check 6:  Pipeline Accuracy           -> findings[]
+-- Check 7:  Red Flag Phrases            -> findings[]
+-- Check 8:  Trial Design Match          -> findings[]
+-- Check 9:  Endpoint Hierarchy          -> findings[]
+-- Check 10: Safety Data Match           -> findings[]
+-- Check 11: Data Maturity               -> findings[]
|
|   All findings collected.
|   IF any YELLOW or RED -> trigger Layer 2
|   IF all GREEN -> skip Layer 2, report clean
|
LAYER 2: ESCALATION (only on flagged items)
+-- Omnicare Test       (opinion/characterization findings)
+-- Harkonen/Clovis     (endpoint/statistics findings)
+-- AVEO/Tongue         (FDA communication findings)
+-- Rule 408 Pattern    (ALL findings, direction analysis)
+-- Matrixx Relevance   (defense-blocker for small-trial findings)
```

**Why this matters**: Layer 2 checks (Omnicare, Matrixx, Rule 408) are
not standalone checks. They are **lenses** applied to findings from
Layer 1. Running them on everything produces noise. Running them only
on flagged items produces targeted, useful analysis.

---

## 3. Legal Framework Summary

### Baseline Rules (always applicable)

| Authority | Citation | Role |
|-----------|----------|------|
| Securities Act &sect; 11 | 15 U.S.C. &sect; 77k | Strict liability for S-1 signers |
| Rule 408 | 17 C.F.R. &sect; 230.408 | Must disclose whatever makes other statements not misleading |
| Rule 10b-5 | 17 C.F.R. &sect; 240.10b-5 | Anti-fraud (requires scienter) |
| FDAAA 801 | 42 U.S.C. &sect; 282(j) | Results reporting within 12 months of completion |

### Supreme Court Standards (Layer 2 escalation)

| Case | Citation | Holding |
|------|----------|---------|
| Omnicare v. Laborers | 575 U.S. 175 (2015) | Opinion statement liability: embedded facts, omitted contrary facts, inquiry basis |
| Matrixx v. Siracusano | 563 U.S. 27 (2011) | No statistical significance threshold for materiality |
| TSC Industries v. Northway | 426 U.S. 438 (1976) | Materiality = "total mix" standard |

### Enforcement Precedents (comparison pairs)

| Case | Citation | Pattern |
|------|----------|---------|
| SEC v. Clovis Oncology | LR-24273 (2018) | Non-standard metrics, inflated ORR ($20M penalty) |
| United States v. Harkonen | 510 Fed. App'x 633 (9th Cir. 2013) | Endpoint promotion, criminal conviction |
| SEC v. AVEO Pharmaceuticals | LR-24062 (2018) | Selective FDA disclosure |
| Tongue v. Sanofi | 816 F.3d 199 (2d Cir. 2016) | FDA feedback disclosure limits |
| In re Rigel Pharmaceuticals | 697 F.3d 869 (9th Cir. 2012) | Partial disclosure permissible if not misleading |

### How the SEC Enforces

Through **comment letters** (written feedback during S-1 review), not a
single industry guide. The reference files contain actual verbatim SEC
comment text organized by topic.

---

## 4. User-Facing Opening

When the skill is triggered, **before any code executes**, present the
following sections:

### Section A: What This Tool Is

> This tool was built by **Jesus Alcocer** for **Norm.ai** assessment
> purposes. It checks whether a biotech company's S-1 registration
> statement adequately discloses clinical trial information by comparing
> the S-1 text to the public record on ClinicalTrials.gov.

### Section B: What is a "Skill"?

> A skill is a structured prompt that orchestrates code and LLM analysis
> together. Think of it as a playbook: at each step, the tool either
> (a) runs a Python script for mechanical work (download a filing, count
> phrases, extract data) or (b) uses LLM reasoning for analytical
> judgment (is this characterization balanced? does this pattern match a
> precedent?).
>
> **The critical design principle: you always know which is which.** Code
> outputs are independently verifiable. LLM reasoning is shown with its
> inputs so you can evaluate it against the standard cited.

### Section C: Visual Process Flow

```
USER ENTERS TICKER
    |
[CODE] Download S-1 from EDGAR -> User confirms filing
    |
[CODE] Parse S-1, identify drug candidates -> User selects candidate
    |
[CODE + LLM] Layer 1 Pass 1: 7 cross-cutting S-1 checks (S-1 text only)
    |
[CODE] Download trial data from ClinicalTrials.gov
    |
[CODE + LLM] Layer 1 Pass 2: 4 trial-level comparison checks (S-1 vs CTgov)
    |
[LLM] Layer 2: Escalation sweep (only if issues found)
    |
Final report with all findings, sources, and reasoning
```

### Section D: Legal Framework Summary

Present the three-layer hierarchy from Section 3 above.

### Section E: Complete Checklist Preview

| # | Check | What We're Looking For | How | Source |
|---|-------|----------------------|-----|--------|
| 1 | Basic Disclosure | Drug identity, indication, stage, no-products statement | Code extracts, LLM assesses completeness | SEC comment letters |
| 2 | Phase Labels | Combined phase labels explained | Code regex, LLM context check | SEC comment letters |
| 3 | Preclinical Framing | Animal data labeled; MoA as hypothesis not fact | Code grep, LLM assessment | SEC comment letters |
| 4 | Comparative Claims | Comparisons supported by head-to-head data | Code scan, LLM comparison | SEC comment letters |
| 5 | FDA Communications | Balanced disclosure of interactions | Code scan, LLM symmetry check | AVEO, Tongue v. Sanofi |
| 6 | Pipeline Accuracy | Pipeline graphic matches text | Code compare / manual note | SEC comment letters |
| 7 | Red Flag Phrases | Safety/efficacy language qualified or supported | Code count + classify, LLM for standalone | SEC comment letters |
| &mdash; | *S-1 checks complete. Comparing to ClinicalTrials.gov.* | | | |
| 8 | Trial Design | S-1 design elements match registry | Code builds comparison table | SEC comment letters |
| 9 | Endpoints & Statistics | Results accurate; hierarchy clear; pre-specified vs post-hoc | Code extracts, LLM precedent comparison | Harkonen, Clovis |
| 10 | Safety Data | Safety claims match AE data | Code builds comparison table, LLM assessment | SEC comment letters |
| 11 | Data Maturity | Preliminary data labeled; no conclusory language | Code status check, LLM language assessment | Rigel, SEC letters |
| &mdash; | *Layer 1 complete. Escalation (only if issues found).* | | | |
| 12 | Rule 408 Pattern | Are omissions systematically one-sided? | Code tabulates direction, LLM pattern assessment | 17 C.F.R. &sect; 230.408 |
| 13 | Omnicare Test | Do opinion statements omit known contrary facts? | LLM three-part test with precedent language | 575 U.S. 175 (2015) |
| 14 | Matrixx Check | Could findings be dismissed on significance grounds? | LLM defense-blocker note | 563 U.S. 27 (2011) |

### Section F: Testing Note

> **Note**: To conserve resources, this version analyzes one drug
> candidate at a time. The architecture supports running all candidates
> automatically.

### Section G: Enter a Ticker

> Enter any pharma/biotech ticker to begin.

---

## 5. Interaction Flow

### Phase 1: Acquire S-1

```bash
python scripts/edgar_fetch.py --ticker {TICKER} --action lookup
```

Present filing metadata. **GATE 0**: User confirms the filing.

```bash
python scripts/edgar_fetch.py --ticker {TICKER} --action download \
    --url "{document_url}" --filing-date {filing_date}
```

### Phase 2: Identify Drug Candidates

```bash
python scripts/s1_parser.py --action find_candidates --file {s1_path}
```

Present candidates as a **factual table only**:

| # | Candidate | Passages | Indications | Phases |
|---|-----------|----------|-------------|--------|

**Do NOT** surface flags, red-flag counts, FDA mentions, or any
analytical observations during candidate identification. Those belong
in the checks.

**GATE 1**: User selects a candidate.

### Phase 3: Layer 1 Pass 1 &mdash; Cross-Cutting S-1 Checks

Run Checks 1-7 using the candidate's passages from the parser. Read
`reference/operationalized_checks.json` for each check's logic, prompt
templates, and precedent language.

**Auto-flow rules:**

- GREEN results: Show the table row. Do not pause. Move to next check.
- YELLOW results: Pause and present:
  ```
  I found an area for attention on [check name].
  [1-2 sentence summary]
  The relevant authority is [citation with URL].
  Would you like more detail, or shall I continue?
  ```
- RED results: Pause, run research augmentation, present:
  ```
  I found a significant concern on [check name].
  [1-2 sentence summary]
  [Research augmentation output]
  Would you like to discuss this finding, or shall I continue?
  ```

**Transition summary after Pass 1:**

```
Pass 1 Complete: Cross-cutting S-1 checks done.
[n] adequate  [n] attention areas  [n] significant concerns

Now moving to trial-level comparison...
```

### Phase 4: Download Trial Data

```bash
python scripts/ctgov_fetch.py fetch-all --drug "{candidate_name}" \
    --output-dir .
```

Present trial table:

| NCT ID | Title | Phase | Status | Results Available |
|--------|-------|-------|--------|-------------------|

**GATE 2**: User selects which trials to analyze.

### Phase 5: Layer 1 Pass 2 &mdash; Trial-Level Comparison

Run Checks 8-11 per selected trial. Use both the comparison_builder
output and structured CTgov JSON files.

```bash
python scripts/comparison_builder.py \
    --s1-json {s1_json_path} \
    --candidate "{candidate_name}" \
    --ctgov-dir {ctgov_drug_dir} \
    --output {comparison_output_path}
```

Same auto-flow rules as Pass 1.

### Phase 6: Layer 2 Escalation

**Trigger**: Any YELLOW or RED finding from Layer 1.

For each flagged finding, apply the appropriate escalation:

- **Opinion/characterization** findings &rarr; Omnicare Test
- **Endpoint/statistics** findings &rarr; Harkonen/Clovis Test
- **FDA communication** findings &rarr; AVEO/Tongue Test
- **All findings** &rarr; Rule 408 Pattern Analysis
- **Small-trial findings** &rarr; Matrixx Relevance Note

If all Layer 1 findings are GREEN, skip Layer 2.

### Phase 7: Aggregate Report

Structure:

1. **Executive Summary** (1 page): Company, ticker, filing date,
   candidate, finding counts, top 3 findings, limitations.
2. **Legal Framework** (1-2 pages): Brief description, authorities list.
3. **Pass 1 Findings**: Full table, expanded analysis for YELLOW/RED.
4. **Pass 2 Findings** (per trial): Disclosure inventory, design
   comparison, endpoint hierarchy, safety comparison, data maturity.
5. **Layer 2 Assessment**: Rule 408 pattern, Omnicare opinion, Matrixx.
6. **Appendix: Sources**: All URLs, NCT URLs, S-1 passage locations.

---

## 6. Operationalized Checks &mdash; Exact Specification

### CHECK 1: BASIC DISCLOSURE

**Inputs**: All S-1 passages for the candidate.

**Steps** (all mechanical/code):

1. **Indication**: grep for disease/condition name near candidate name.
   &rarr; PRESENT (with text) or ABSENT.
2. **Modality**: grep for modality keywords (`small molecule`, `antibody`,
   `monoclonal`, `gene therapy`, `cell therapy`, `peptide`,
   `oligonucleotide`, `vaccine`, `bispecific`, `ADC`, `conjugate`).
   Also check INN suffixes: `-mab`, `-nib`, `-tide`, `-gene`, `-mer`.
   &rarr; PRESENT or ABSENT.
3. **Development Stage**: Extract all phase mentions (`Phase [1-3]`,
   `preclinical`, `IND`, `NDA`, `BLA`). Check coherent progression
   (Phase 1 date < Phase 2 date < Phase 3 date).
   &rarr; CLEAR / UNCLEAR / DATES MISSING.
4. **No Approved Products**: grep for `no approved products`,
   `clinical-stage`, `not generated.*revenue`, `no products.*approved`.
   &rarr; PRESENT or ABSENT.

**Output**: Table with each element, status, and S-1 text found.

**Escalation**: None. GREEN if all present. YELLOW if any absent.

---

### CHECK 2: PHASE LABELS

**Inputs**: All S-1 passages for the candidate.

**Step 1** (CODE): Regex for combined phase labels:
`Phase\s*[12]\s*/\s*[23]` and variations (`Phase 1/2a`, `Phase 2a/2b`).

IF no combined labels &rarr; GREEN, done.

**Step 2** (CODE): For each combined label, extract 1000 chars context.
Search for explanation terms: `Phase 1 portion`, `dose escalation`,
`MTD`, `RP2D`, `Phase 2 portion`, `expansion`, `efficacy`, `activity`,
`transition`, `criteria`, `trigger`.

IF explanation found &rarr; GREEN (label explained).
IF not found &rarr; YELLOW.

**Step 3** (LLM &mdash; only if YELLOW):

```
The S-1 uses the label '{{COMBINED_LABEL}}' in this context:
'{{S1_PASSAGE}}'

The SEC has required companies to explain what each phase portion
involves. Here is the SEC's comment in a comparable situation:
'{{PRECEDENT_COMMENT}}'

Does this S-1 passage adequately explain both portions?
```

---

### CHECK 3: PRECLINICAL FRAMING

**Step 1** (CODE): Identify preclinical references.
grep for: `preclinical`, `animal`, `mouse`, `rat`, `primate`,
`in vitro`, `in vivo`, `xenograft`, `DIO model`, `knockout`.

IF none &rarr; N/A, skip.

**Step 2** (CODE): For each reference, check for translation risk caveat
within 2000 chars: `may not be predictive`, `no assurance`,
`animal.*not.*predict`, `preclinical.*may not.*translate`.
&rarr; CAVEAT PRESENT or ABSENT.

**Step 3** (CODE): Check MoA language. Classify each sentence with the
drug's mechanism as:
- **HYPOTHETICAL**: `designed to`, `intended to`, `aims to`, `believed to`,
  `may`, `potentially`
- **FACTUAL**: `has shown`, `demonstrates`, `induces`, `activates`,
  `inhibits` WITHOUT qualifying language

IF all hypothetical &rarr; GREEN.
IF any factual &rarr; Step 4.

**Step 4** (LLM):

```
This S-1 states: '{{MOA_STATEMENT}}'
This describes the drug's mechanism using factual language
('{{SPECIFIC_VERB}}') rather than hypothetical framing.

The SEC has challenged similar language. In {{COMPANY}}'s S-1,
the SEC commented: '{{PRECEDENT_COMMENT}}'

Is this S-1's MoA statement:
(a) Supported by clinical (human) data cited elsewhere in the S-1?
(b) Based only on preclinical data but stated as established fact?
(c) Appropriately qualified despite the factual verb?
```

---

### CHECK 4: COMPARATIVE CLAIMS

**Step 1** (CODE): Scan for comparative language near candidate name:
`safer`, `more effective`, `superior`, `differentiated`, `best-in-class`,
`first-in-class`, `improved over`, `advantage`, `compared favorably`,
`outperform`.

IF none &rarr; GREEN, skip.

**Step 2** (CODE): For each hit, extract 1500 chars context. Search for
head-to-head evidence: `head-to-head`, `direct comparison`,
`comparative trial`.
&rarr; HEAD_TO_HEAD_CITED or NO_DIRECT_COMPARISON.

**Step 3** (LLM &mdash; for each hit without head-to-head):

```
The S-1 makes this comparative statement about {{CANDIDATE}}:
'{{S1_QUOTE}}'

No head-to-head clinical trial is cited. The SEC has challenged
similar language: '{{PRECEDENT_COMMENT}}'

In that case, the SEC asked: '{{SEC_REQUIREMENT}}'

How does this S-1's language compare?
(a) Materially similar (same type of unsupported comparison)
(b) Distinguishable (this S-1 has qualifications the other lacked)
(c) More aggressive than the language the SEC challenged
```

---

### CHECK 5: FDA COMMUNICATIONS

**Step 1** (CODE): Extract all FDA-related passages.
grep for: `FDA`, `IND`, `NDA`, `BLA`, `Breakthrough`, `Fast Track`,
`Orphan`, `Priority Review`, `pre-IND`, `End-of-Phase`, `SPA`, `CRL`,
`PDUFA`.

**Step 2** (CODE): Classify each passage:
- **POSITIVE**: `aligned`, `agreed`, `positive feedback`, `constructive`,
  `granted`, `designated`, `approved`
- **NEGATIVE**: `denied`, `refused`, `required additional`, `concerns`,
  `deficiency`, `refuse to file`, `CRL`
- **NEUTRAL**: factual without characterization

**Step 3** (CODE): Count and check placement:
- Positive in Business/Summary, negative only in Risk Factors &rarr; YELLOW
- Positive >0, negative =0 &rarr; RED (one-sided)
- Both in Business &rarr; GREEN

**Step 4** (LLM &mdash; if YELLOW or RED):

```
The S-1 describes FDA interactions for {{CANDIDATE}}.

POSITIVE characterizations ({{SECTIONS}}):
{{POSITIVE_LIST}}

NEGATIVE disclosures ({{SECTIONS}}):
{{NEGATIVE_LIST}}

In SEC v. AVEO Pharmaceuticals (LR-24062), the company was
charged with fraud for selectively disclosing positive FDA
interactions while omitting the FDA's recommendation for an
additional trial: '{{AVEO_FACTS}}'

In Tongue v. Sanofi, 816 F.3d 199 (2d Cir. 2016), the court
held: '{{TONGUE_HOLDING}}'

Compare this S-1's pattern:
(a) Is there material negative FDA feedback omitted or
    asymmetrically placed?
(b) Does the positive characterization create an impression
    the negative disclosure undermines?
(c) How does the severity compare to AVEO?
```

---

### CHECK 6: PIPELINE ACCURACY

**Step 1** (CODE): Detect pipeline format.
Search HTML for `<table>` elements near `pipeline` keyword.
&rarr; HTML_TABLE or IMAGE.

IF IMAGE:
> Pipeline is embedded as an image and cannot be verified
> programmatically. Manual review recommended.
> Mark: YELLOW (cannot verify). Done.

IF HTML_TABLE:

**Step 2** (CODE): Extract phase claims per candidate from table.
Compare to phase claims in text passages.
For each candidate: `table_phases` vs `text_phases` &rarr; MATCH or MISMATCH.

**Step 3** (CODE): Check for overstated progress.
IF table shows Phase 2 but text only describes Phase 1 data &rarr; RED.
IF table shows `IND-enabling` but no IND filed &rarr; YELLOW.

---

### CHECK 7: RED FLAG PHRASES

**Step 1** (CODE): For each phrase in `red_flag_phrases.txt`, scan all
passages. Record: phrase matched, exact sentence, section, approximate
page, 500 chars context.

**Step 2** (CODE): Classify each hit:

- **CATEGORY A (CAUTIONARY)**: In Risk Factor section OR conditional
  (`may not be`, `cannot assure`, `no guarantee of`). &rarr; AUTO GREEN.
- **CATEGORY B (SUPPORTED)**: Quantitative data within 500 chars (AE
  rates n/N, %, p-values, dose/response). &rarr; AUTO GREEN.
- **CATEGORY C (STANDALONE)**: Affirmative, no nearby data, not
  cautionary. &rarr; FLAG for Step 3.

**Step 3** (LLM &mdash; for each CATEGORY C hit):

```
The S-1 uses '{{PHRASE}}' in this context:
'{{S1_PASSAGE}}'
Section: {{SECTION}}, approx. page {{PAGE}}

This usage is:
- Not in a cautionary/conditional context
- Not immediately supported by quantitative data

The SEC has challenged similar language. In a comment letter
to {{COMPANY}}, the SEC stated:
'{{SEC_COMMENT}}'
The S-1 language that triggered this comment was:
'{{TRIGGERED_LANGUAGE}}'

Compare this S-1's usage to the language the SEC challenged.
Is this instance:
(a) Comparable -- similar standalone use without data support
(b) Distinguishable -- this context provides implicit support
(c) Worse -- more affirmative/absolute than the challenged language
```

**Step 4** (CODE): Accumulation. If any single phrase has >10 STANDALONE
instances &rarr; PATTERN flag.

---

### CHECK 8: TRIAL DESIGN MATCH

**Step 1** (CODE): Extract from CTgov JSON:
- `phase`, `allocation`, `masking`, `enrollment` (count and type),
  `arms`, `primary_endpoints`, `secondary_endpoints`

**Step 2** (CODE): For each element, search S-1 passages:
- Phase: grep for `Phase [n]`
- Allocation: grep for `randomized`, `non-randomized`, `single-arm`
- Masking: grep for `double-blind`, `open-label`, `single-blind`,
  `placebo-controlled`
- Enrollment: grep for numbers near `patients`, `subjects`, `enrolled`
- Endpoints: grep for each endpoint measure term

**Step 3** (CODE): Mark each element:
- **MATCH**: S-1 and CTgov agree
- **ABSENT**: Element in CTgov but not found in S-1
- **PARTIAL**: Related language found but not exact
- **MISMATCH**: S-1 says something different

**Step 4** (LLM &mdash; only for ABSENT or MISMATCH):

```
This trial element is {{STATUS}}:
CTgov says: {{CTGOV_VALUE}}
S-1 says: {{S1_PASSAGE}} (or 'not found')

The SEC has required disclosure of this element:
'{{PRECEDENT_COMMENT}}'

Would a reasonable investor consider this omission/mismatch
important?
```

**Output**: Full comparison table with color coding:
- GREEN: MATCH
- YELLOW: PARTIAL or ABSENT (non-critical)
- RED: MISMATCH or ABSENT (critical element)

---

### CHECK 9: ENDPOINT HIERARCHY (The Harkonen Check)

This is the most critical check. It must be precise.

**Step 1** (CODE): Extract endpoint hierarchy from CTgov:
- `primaryOutcomes[]` &rarr; {measure, description, timeFrame}
- `secondaryOutcomes[]` &rarr; {measure, description, timeFrame}
- IF resultsSection exists: extract type (PRIMARY, SECONDARY, POST_HOC),
  check if primary SUCCEEDED or FAILED (via analyses[].pValue)

**Step 2** (CODE): Map S-1 passages to endpoints.
For each endpoint: search S-1 for measure term &rarr; DISCUSSED / NOT DISCUSSED.

**Step 3** (CODE): Identify what the S-1 LEADS WITH.
The "headline finding" = the first efficacy result in Prospectus Summary
or first mention in Business section.

**Step 4** (CODE): THE HARKONEN PATTERN CHECK.
Conditions for RED (ALL must be true):
A. The headline finding is from a SECONDARY or unregistered endpoint.
B. The PRIMARY endpoint is not discussed OR showed null/negative result
   not highlighted.
C. The S-1 does not label the headline finding as secondary/exploratory.

IF A + B + C &rarr; RED (Harkonen pattern).
IF A + B but labeled as secondary &rarr; YELLOW.
IF primary prominently discussed &rarr; GREEN.

**Step 5** (LLM &mdash; if YELLOW or RED):

```
ENDPOINT HIERARCHY ANALYSIS

ClinicalTrials.gov shows:
PRIMARY endpoint: {{MEASURE}} -- Result: {{RESULT}}
SECONDARY endpoints: {{LIST}} -- Results: {{RESULTS}}

The S-1 presents this trial as follows:
HEADLINE (first mention): '{{S1_QUOTE}}' ({{SECTION}}, p. {{PAGE}})
Primary endpoint discussion: '{{S1_PRIMARY_QUOTE}}'

PRECEDENT COMPARISON:

In United States v. Harkonen (InterMune):
- Primary endpoint: PFS -> FAILED (not statistically significant)
- Press release headline: '{{HARKONEN_HEADLINE}}'
- Post-hoc subgroup: p=0.004 (unblinded, not pre-specified)
- The court found this constituted wire fraud

In SEC v. Clovis Oncology:
- Reported 60% ORR using unconfirmed responses
- Confirmed ORR was 28%
- Non-standard metric definition undisclosed

Compare this S-1's endpoint presentation:
1. Is the headline from the primary endpoint?
2. If not, is the primary also disclosed?
3. Is the hierarchy clearly stated?
4. Rate similarity to Harkonen pattern:
   HIGH / MODERATE / LOW / NOT APPLICABLE
```

---

### CHECK 10: SAFETY DATA MATCH

**Step 1** (CODE): Extract from CTgov results (if posted):
- `eventGroups[]`: deathsNumAffected, seriousNumAffected, seriousNumAtRisk
- `seriousEvents[]`, `otherEvents[]`
- Calculate: overall AE rate, SAE rate, death rate per arm

**Step 2** (CODE): Extract safety characterizations from S-1:
grep for: `well-tolerated`, `safe`, `safety profile`, `adverse`, `SAE`,
`serious adverse`, `TEAE`, `treatment-emergent`, `death`.

**Step 3** (CODE): Direct comparison:
- S-1 says "well-tolerated" &rarr; CTgov AE rate = ?
- S-1 says "no SAEs" &rarr; CTgov SAE count = ?
- S-1 says "no deaths" &rarr; CTgov death count = ?
Mark: SUPPORTED / CONTRADICTED / UNVERIFIABLE.

**Step 4** (CODE): Results posting compliance (FDAAA 801).
IF status == COMPLETED and no resultsSection:
- Calculate months since completion
- IF >12 months &rarr; RED (potential FDAAA 801 non-compliance)
- ELSE &rarr; YELLOW (within window but not posted)

**Step 5** (LLM &mdash; if any CONTRADICTED):

```
SAFETY DATA COMPARISON

The S-1 states: '{{S1_SAFETY_CLAIM}}' ({{SECTION}}, p. {{PAGE}})

ClinicalTrials.gov data:
- Overall AE rate: {{DRUG_AE}} vs {{PLACEBO_AE}}
- SAE rate: {{DRUG_SAE}} vs {{PLACEBO_SAE}}
- Deaths: {{DRUG_DEATHS}} vs {{PLACEBO_DEATHS}}
- Top 5 AEs: {{AE_LIST}}

The S-1's characterization appears {{STATUS}} because {{REASON}}.

The SEC has challenged similar characterizations:
'{{PRECEDENT_COMMENT}}'

Compare the severity of the discrepancy to the language the SEC
challenged. How material is the gap?
```

---

### CHECK 11: DATA MATURITY (Interim/Topline)

**Step 1** (CODE): Determine trial status from CTgov.
`overallStatus` &rarr; COMPLETED / ACTIVE_NOT_RECRUITING / RECRUITING / etc.
`resultsSection` exists? &rarr; results_posted = true/false.

**Step 2** (CODE): Check S-1 labeling.
IF status != COMPLETED:
Search for: `interim`, `preliminary`, `topline`, `initial`, `data cutoff`.
&rarr; LABELED_PRELIMINARY or NOT_LABELED.
IF NOT_LABELED and trial ongoing &rarr; YELLOW.

**Step 3** (CODE): Check for conclusory language on preliminary data.
IF trial ongoing OR no results OR S-1 says "preliminary":
Search for: `demonstrated`, `established`, `proven`, `confirmed`,
`showed`, `validated`.
&rarr; Found [n] conclusory terms.

**Step 4** (LLM &mdash; if conclusory terms found):

```
The S-1 presents data from {{TRIAL_STATUS}} and uses:
'{{S1_PASSAGE}}'

The conclusory term '{{VERB}}' is used for data that is
{{DATA_MATURITY_LEVEL}}.

In In re Rigel Pharmaceuticals, 697 F.3d 869 (9th Cir. 2012),
the court held: '{{RIGEL_HOLDING}}'

The SEC has challenged conclusory language for preliminary data:
'{{PRECEDENT_COMMENT}}'

Is the conclusory framing appropriate given the data maturity?
```

---

## 7. Layer 2 Escalation Checks

### OMNICARE TEST

**Trigger**: Layer 1 YELLOW or RED involving opinion/characterization.

**Inputs**: The finding, the S-1 opinion text, contrary facts from CTgov.

**LLM Prompt**:

```
OMNICARE OPINION ANALYSIS

In Omnicare, Inc. v. Laborers District Council, 575 U.S. 175 (2015),
the Supreme Court held that opinion statements can be actionable:

Test 1 (Sincerity): '{{OMNICARE_TEST1_QUOTE}}'
Test 2 (Embedded Facts): '{{OMNICARE_TEST2_QUOTE}}'
Test 3 (Omitted Contrary Facts): '{{OMNICARE_TEST3_QUOTE}}'

Limiting principle: '{{OMNICARE_LIMITING_QUOTE}}'

APPLICATION:
S-1 Opinion: '{{S1_TEXT}}' ({{SECTION}}, p. {{PAGE}})
Contrary Facts: {{CONTRARY_FACTS}}

TEST 1: Does this embed a factual claim? Is it supported?
TEST 2: Are contrary facts disclosed? Would omission be material?
LIMITING PRINCIPLE: Is this a genuine trigger or normal opinion?

RATE: SIGNIFICANT RISK / MODERATE RISK / LOW RISK / NO CONCERN
```

### HARKONEN/CLOVIS TEST

**Trigger**: Layer 1 RED on Check 9 (Endpoints).

Applied within Check 9 Step 5 prompt above.

### AVEO/TONGUE TEST

**Trigger**: Layer 1 YELLOW or RED on Check 5 (FDA Communications).

Applied within Check 5 Step 4 prompt above.

### RULE 408 PATTERN

**Trigger**: Multiple YELLOW or RED findings from Layer 1.

**Step 1** (CODE): Tabulate all findings. Classify direction:
- FAVORS_COMPANY: Omission makes drug look better
- NEUTRAL: No clear direction
- DISFAVORS_COMPANY: Omission makes drug look worse

**Step 2** (CODE): Calculate:
`pct_one_sided = favors_company / total_findings`
- <50% &rarr; GREEN (no pattern)
- 50-75% &rarr; YELLOW (possible pattern)
- >=75% &rarr; RED (strong pattern)

**Step 3** (LLM &mdash; if YELLOW or RED):

```
RULE 408 PATTERN ANALYSIS

Rule 408 (17 C.F.R. section 230.408) requires:
'{{RULE_408_TEXT}}'

Across {{N}} findings, {{FAVORS}} ({{PCT}}%) involve omissions
favoring the company:

{{FINDINGS_TABLE}}

Assess: Is this pattern consistent and systematic, or are there
reasonable explanations for individual omissions?
```

### MATRIXX RELEVANCE

**Trigger**: Any finding involving small trial (N<30) or significance.

This is a DEFENSE-BLOCKER, not an independent check. It prevents
dismissal of findings on statistical significance grounds:

> Under Matrixx Initiatives, 563 U.S. 27 (2011), the materiality of
> this finding does not depend on statistical significance. The Court
> held: "medical professionals and researchers do not limit the data
> they consider to the results of randomized clinical trials or to
> statistically significant evidence."

---

## 8. Output Formats

### Pass 1 Output (per check element)

| Check | Status | Standard (with source) | S-1 Quote (section, page) | Reasoning |
|-------|--------|----------------------|--------------------------|-----------|

### Pass 2 Output (per trial)

**TABLE 1: Disclosure Inventory** &mdash; Everything the S-1 says about
this trial:

| # | S-1 Statement (exact quote) | Section | Page (approx) |
|---|---------------------------|---------|---------------|

**TABLE 2: Design Comparison** &mdash; Code-generated side-by-side:

| Element | ClinicalTrials.gov | S-1 Says | Status |
|---------|--------------------|----------|--------|

Color coding: GREEN = Match, YELLOW = Partial/Absent (non-critical),
RED = Mismatch/Absent (critical).

**TABLE 3: Check Results** &mdash; Same format as Pass 1 plus CTgov column.

### Layer 2 Output

**Rule 408 table:**

| # | Omission/Gap | Direction | Source Check |
|---|-------------|-----------|-------------|

**Omnicare table:**

| Statement | Impression Created | Known Contrary Facts | Risk Level |
|-----------|-------------------|---------------------|------------|

---

## 9. Research Augmentation

When a RED finding triggers research augmentation, present:

```
FINDING: [concise description]

LEGAL STANDARD:
[Full text pulled from reference files]

COMPARABLE PRECEDENT:
In [case/letter], the SEC/court addressed similar language.
The [filing] stated: "[EXACT quote from problematic disclosure]"
The [SEC/court] found: "[EXACT holding/comment]"
The company was required to: [action/penalty]

THIS S-1:
"[EXACT quote from S-1 being analyzed]"
(Section: [name], Page: [approx])

TEXT-TO-TEXT COMPARISON:
[Specific textual parallels between S-1 and precedent]

RISK LEVEL: RED -- [Why this pattern matches the precedent]
```

---

## 10. Calibration Rules (Mandatory)

### Rule 1: Risk areas, not legal conclusions

- SAY: "This language raises questions under [authority]"
- NOT: "This fails [test]" or "This violates [standard]"

### Rule 2: No liability determinations

- SAY: "This pattern warrants attorney review under Rule 408"
- NOT: "This is materially deficient" or "Section 11 exposure is HIGH"

### Rule 3: Severity = flag strength, not legal outcome

- RED = Strong flag: clear gap, authority directly on point, pattern
  matches enforcement precedent. Attorney should review.
- YELLOW = Moderate flag: gap or concern exists, context may justify.
  Attorney should be aware.
- GREEN = Adequate: meets the standard.

### Rule 4: Acknowledge limitations

Every report must include:

> This tool compares S-1 text to ClinicalTrials.gov only. It does not
> review published papers, FDA correspondence, or internal data.
>
> ClinicalTrials.gov data reflects what the sponsor posted &mdash; it
> could itself be incomplete.
>
> This tool identifies risk areas for attorney review. It does not
> determine liability or materiality in the full legal sense.

### Rule 5: When in doubt, flag for review

If uncertain, present as YELLOW with explanation of both possibilities.
Never conclude RED unless the factual pattern clearly matches a
precedent.

---

## 11. Scripts Requirements

### s1_parser.py

Must include:

1. **Page number approximation**: `character_position / 3000 = approx_page`.
   Every passage outputs: `section_name`, `subsection_name` (if
   identifiable), `approximate_page_number`, `character_position`.

2. **Section mapping**: Identify which standard S-1 section each passage
   belongs to (Prospectus Summary, Risk Factors, Use of Proceeds,
   Business, MD&A, Financial Statements). Critical for asymmetric
   placement analysis.

3. **Candidate disambiguation**: Distinguish company drugs from
   competitor drugs by proximity to ownership language (`our`, `we`,
   `our lead`, `our proprietary` within 200 chars = COMPANY DRUG;
   `competitor`, `approved`, other company name = COMPETITOR DRUG).

### comparison_builder.py

Must include:

1. **Color-coded output**: Each comparison element tagged as
   GREEN/YELLOW/RED.
2. **Endpoint hierarchy detection**: Identify if S-1 leads with
   secondary while primary is missing/failed.
3. **Safety claim verification**: Direct comparison of S-1 safety
   characterizations against CTgov AE data.
4. **FDAAA 801 check**: Flag completed trials without posted results.

---

## 12. Reference File Structure

### reference/legal_framework.json

For each case/statute: actual language (holdings, key quotes). For each
comment letter: actual SEC comment text. For each enforcement action:
actual facts and language. These get inserted into LLM prompt templates.

### reference/operationalized_checks.json (replaces check_descriptions.json)

For each check: pseudocode logic, thresholds, grep patterns, LLM prompt
template with slots (`{{PRECEDENT_LANGUAGE}}`, `{{S1_TEXT}}`,
`{{CTGOV_DATA}}`), specific comment letter excerpt IDs.

### reference/comment_letter_excerpts.json

Actual verbatim SEC comments organized by topic. The S-1 language that
triggered each comment. What the company was required to do.

### reference/guardrails.json

Omnicare three-part test with exact quotes. Rule 408 pattern thresholds.
Matrixx exact holding. Calibration language for each.

### reference/red_flag_phrases.txt

Machine-readable phrase list for Check 7.

---

## 13. Gap Analysis: Current Reference Files

### reference/legal_framework.json

| Element | Status | Gap |
|---------|--------|-----|
| Statutes (Section 11, Rule 408, Rule 10b-5, FDAAA 801) | COMPLETE | Operative text present and verified |
| Omnicare three-part test | MOSTLY COMPLETE | Has quotes for tests 1-3 and limiting language. Missing slip opinion page numbers for exact quote attribution. |
| Matrixx key quotes | COMPLETE | Rejecting statistical significance, medical professionals quote present |
| TSC Industries materiality | COMPLETE | "Total mix" quote present |
| Tongue v. Sanofi | COMPLETE | Detailed holding and key quotes. Caveat about retail vs sophisticated investors noted. |
| Rigel Pharmaceuticals | COMPLETE | Partial disclosure standard present |
| Clovis enforcement facts | MOSTLY COMPLETE | What they said, true numbers, penalty present. Missing exact complaint quote language. |
| Harkonen enforcement facts | MOSTLY COMPLETE | Press release headline/subhead present, trial facts detailed. Primary endpoint p-value (p=0.52) UNVERIFIED per note. |
| AVEO enforcement facts | INCOMPLETE | Only summary-level facts. Missing exact SEC complaint language and specific AVEO filing quotes. |
| Comment letter topics | COMPLETE (summary) | 7 topics with excerpt counts and IDs linking to comment_letter_excerpts.json |

### reference/comment_letter_excerpts.json

| Topic | Excerpts | Gap |
|-------|----------|-----|
| Safety characterizations | 5 | GOOD coverage. Verbatim SEC comments present. |
| Phase nomenclature | 3 | ADEQUATE. Could add 1-2 more for gene therapy / rare disease context. |
| Preclinical claims | 3 (one shared with comparative) | ADEQUATE. |
| Comparative claims | 3 | ADEQUATE. Key pattern (qualifying language doesn't cure) captured. |
| FDA communications | 3 | ADEQUATE but overlap with safety topic. Could add letters specifically about BTD/Fast Track disclosure. |
| Trial design disclosure | 3 | ADEQUATE. Good Stealth example on failed primary endpoint. |
| Statistical presentation | 3 | ADEQUATE. Powering and post-hoc clarity covered. |

### reference/operationalized_checks.json

**DOES NOT EXIST** &mdash; must be created. Currently `check_descriptions.json`
has plain-English descriptions but lacks:
- Pseudocode logic with thresholds
- LLM prompt templates with slots
- Specific grep patterns
- Comment letter excerpt ID linkages for each step

### reference/guardrails.json

| Element | Status | Gap |
|---------|--------|-----|
| Rule 408 pattern test | COMPLETE | Procedure, thresholds, calibration, table format |
| Omnicare opinion test | COMPLETE | Three-part test, procedure, calibration, limiting principle from Tongue |
| Matrixx significance check | COMPLETE | Procedure, scenarios, calibration, Rigel interaction |

### Comparison Pairs Needed

The v4 architecture requires **comparison pairs** (problematic language +
what was wrong + comparison instruction) for text-to-text LLM comparison.
These do not exist in the current reference files. Must be added to
`legal_framework.json` enforcement actions:

| Enforcement Case | Comparison Pair Status |
|-----------------|----------------------|
| Harkonen | Has press release headline text but needs structured pair format |
| Clovis | Has what-they-said/what-was-true but needs structured pair |
| AVEO | Incomplete &mdash; needs actual filing language, not just summary |

---

## 14. v2 &rarr; v4 Behavior Change Table

| v2 Did (WRONG) | v4 Does (RIGHT) | Why |
|----------------|-----------------|-----|
| Surfaced flags during candidate ID | Present ONLY factual table | Flags belong in checks, not candidate ID |
| Said "Module 2", "Module 3" | Descriptive names: "Basic Disclosure", "Phase Labels" | Lawyers don't think in modules |
| Concluded "MATERIALLY DEFICIENT" | Present findings; let attorney conclude | Legal conclusion, not tool output |
| Said findings "FAIL" Omnicare | Say findings "raise questions under" Omnicare | "Fails" implies legal determination |
| Paraphrased S-1 language | Quote EXACT S-1 language with section and page | Attorneys need actual text |
| Cited authorities without language | Include actual holding/comment language | "SEC challenged X" is useless without words |
| Did not research RED findings | Text-to-text comparison with precedent | The comparison is the point |
| Required "go ahead" between every step | Auto-flow GREEN; pause YELLOW/RED | Unnecessary friction |
| Presented findings as prose | Color-coded tables with standardized columns | Tables are scannable, auditable |
| Auto-analyzed all trials | Ask user which trials to analyze (GATE 2) | Attorney chooses material trials |
| Omnicare: "FAIL" / "PASS" | Graduated: SIGNIFICANT / MODERATE / LOW / NO CONCERN | Binary implies legal determination |
| Said "Section 11 EXPOSURE: HIGH" | Do not rate exposure; present findings | Exposure rating is attorney work product |

---

## 15. File Sync Checklist

After building is complete, verify:

- [ ] SKILL.md references "v4" and matches Layer 1 / Layer 2 architecture
- [ ] SKILL.md does NOT use the word "module" anywhere
- [ ] README.md accurately describes the current file structure
- [ ] README.md includes attribution (Jesus Alcocer, Norm.ai)
- [ ] README.md describes Layer 1 / Layer 2 architecture
- [ ] All reference JSON files use consistent ID schemes
- [ ] `operationalized_checks.json` references `legal_framework.json` by ID
- [ ] `comment_letter_excerpts.json` entries referenced by ID in
      `operationalized_checks.json`
- [ ] No orphaned references to v2 or v3 concepts
- [ ] No references to "modules" in any file
- [ ] `red_flag_phrases.txt` exists and is referenced by Check 7
- [ ] All placeholder URLs replaced with verified URLs

---

## 16. SEC-API.IO Integration

API key: `7ef2ddea736b769ac2d44f2d63717165bd777168b8bdbb8101e6c52087275ca0`
Endpoint: `https://sec-api.io/`

**Budget**: 100 API calls total.
- 30 calls: Building reference files
- 50 calls: Runtime research augmentation on RED findings
- 20 calls: Reserve

**Primary tool**: EDGAR full-text search (free, no limit):
`https://efts.sec.gov/LATEST/search-index?q="well-tolerated"&forms=CORRESP`

**sec-api.io as FALLBACK** when EDGAR search doesn't return results.

---

*End of specification.*
