# SPECIFICATION v4: S-1 Clinical Trial Disclosure Checker
# INSTRUCTIONS FOR CLAUDE CODE

## WHAT TO DO

Read this entire document. Then:
1. Build the v4 spec as `s1_checker_skill_spec_v4.md` in the repo root
2. Rebuild the reference files to match the operationalized framework
3. Update SKILL.md to implement v4
4. Update README.md so it accurately describes the v4 system
5. Ensure all docs are in sync

**The core change from v3**: The legal framework is no longer a 
reference document the LLM "reads and reasons about." It is now an 
**operationalized decision tree** where each check has:
- Concrete inputs (what text to extract)
- Concrete comparisons (what to compare it against, including actual 
  precedent language)
- Concrete outputs (binary or scored, with clear thresholds)
- Escalation rules (when to call LLM for further reasoning, and 
  with what specific inputs)

Think of every legal check as a function:
```
check(s1_text, standard, precedent_language) → {status, evidence, reasoning}
```

---

## THE FUNDAMENTAL ARCHITECTURE CHANGE

### OLD (v3): Vague standards + LLM reasoning
```
Standard: "Safety adjectives should be supported by data"
LLM sees S-1 text → reasons about whether it's adequate → produces finding
Problem: Non-reproducible. Different runs may produce different findings.
         No one can audit WHY the LLM concluded what it concluded.
```

### NEW (v4): Operationalized checks + targeted LLM comparison
```
Check: SAFETY_ADJECTIVE_SUPPORT
  Input: Every instance of "well-tolerated" in S-1 (code extracts)
  For each instance:
    Step 1 (CODE): Is there quantitative AE data within 500 chars? 
            (regex for "n/N", "%", "AE", "adverse")
            → YES: mark GREEN, record the data
            → NO: go to Step 2
    Step 2 (CODE): Is the instance in a Risk Factor section? 
            (section mapping)
            → YES: mark GREEN (cautionary context)
            → NO: go to Step 3
    Step 3 (LLM CALL): Present to LLM:
            - The S-1 passage (with surrounding context)
            - The SEC comment letter language that challenged 
              similar phrasing: "[exact quote from letter]"
            - The question: "Compare the S-1 language to the 
              language the SEC challenged. Is the S-1 language 
              materially similar, distinguishable, or worse?"
            → LLM produces structured comparison
    Step 4 (ACCUMULATION): After all instances checked, count:
            How many GREEN, how many flagged?
            If >10 standalone instances → PATTERN flag
```

This is **auditable**: you can see exactly what code did, what the 
LLM was asked, and what specific precedent language was compared.

---

## THE DECISION TREE ARCHITECTURE

### Layer 1: Concrete Checks (Always Run)

These are the S-1 cross-cutting and trial-level checks. Each is a 
specific, testable question with defined inputs and thresholds. 
They run EVERY TIME, regardless of what they find.

### Layer 2: Escalation Checks (Run Only When Layer 1 Raises Issues)

These are the case-law-based standards (Omnicare, Matrixx, Rule 408).
They are NOT run on every statement. They are triggered ONLY when 
Layer 1 checks have identified specific issues.

**Why this matters**: Omnicare, Matrixx, and Rule 408 are not 
standalone checks — they are LENSES applied to findings from Layer 1.
Running them on everything would produce noise. Running them only on 
flagged items produces targeted, useful analysis.

```
LAYER 1: CONCRETE CHECKS
├── Check 1: Basic Disclosure → findings[]
├── Check 2: Phase Labels → findings[]
├── Check 3: Preclinical Framing → findings[]
├── Check 4: Comparative Claims → findings[]
├── Check 5: FDA Communications → findings[]
├── Check 6: Pipeline Accuracy → findings[]
├── Check 7: Red Flag Phrases → findings[]
├── Check 8: Trial Design Match → findings[]
├── Check 9: Endpoint Hierarchy → findings[]
├── Check 10: Safety Data Match → findings[]
├── Check 11: Data Maturity → findings[]
│
│   All findings collected. Now:
│   IF any findings are YELLOW or RED → trigger Layer 2
│   IF all GREEN → skip Layer 2, report clean
│
LAYER 2: ESCALATION (only on flagged items)
├── For each RED finding:
│   ├── Omnicare Test (if finding involves opinion/characterization)
│   │   Input: the S-1 opinion + the contrary facts found
│   │   Compare to: actual Omnicare language + subsequent cases
│   │   LLM reasons with specific text comparison
│   │
│   ├── Harkonen/Clovis Test (if finding involves endpoint/statistics)
│   │   Input: the S-1 presentation + CTgov hierarchy
│   │   Compare to: actual Harkonen facts + actual Clovis facts
│   │   LLM compares specific patterns
│   │
│   └── AVEO/Tongue Test (if finding involves FDA communication)
│       Input: the S-1 FDA characterization + what's omitted
│       Compare to: actual AVEO facts + Tongue holding
│       LLM compares specific patterns
│
├── Pattern Analysis (Rule 408):
│   Input: ALL findings from Layer 1
│   Check: Are >75% of omissions in the same direction?
│   IF YES → flag pattern with specific count
│
└── Matrixx Relevance (only if small trial or significance argument):
    Input: trial sizes, whether significance is invoked
    Note: This is a DEFENSE-BLOCKER, not an independent check.
    It says: "don't dismiss the above findings on significance grounds"
```

---

## OPERATIONALIZED CHECKS: EXACT SPECIFICATION

### CHECK 1: BASIC DISCLOSURE

```python
def check_basic_disclosure(candidate_passages, candidate_info):
    """
    INPUTS:
    - candidate_passages: all S-1 passages for this drug candidate
    - candidate_info: name, phase claims, NCT numbers
    
    CHECKS (all mechanical/code):
    1.1 INDICATION: grep for disease/condition name near candidate name
        → PRESENT (with text) or ABSENT
    
    1.2 MODALITY: grep for modality keywords within candidate passages:
        ["small molecule", "antibody", "monoclonal", "gene therapy",
         "cell therapy", "peptide", "oligonucleotide", "vaccine",
         "bispecific", "ADC", "conjugate"]
        Also check INN suffixes: -mab, -nib, -tide, -gene, -mer, etc.
        → PRESENT (with text) or ABSENT
    
    1.3 DEVELOPMENT STAGE: 
        Extract all phase mentions: "Phase [1-3]", "preclinical", 
        "IND", "NDA", "BLA"
        Check: do they form a coherent progression?
        (Phase 1 date < Phase 2 date < Phase 3 date)
        → CLEAR / UNCLEAR / DATES MISSING
    
    1.4 NO APPROVED PRODUCTS:
        grep for: "no approved products", "clinical-stage", 
        "not generated.*revenue", "no products.*approved"
        → PRESENT (with text) or ABSENT
    
    OUTPUT: Table with each element, status, and the S-1 text found
    
    ESCALATION: None needed. This is a presence check.
    GREEN if all present. YELLOW if any absent.
    """
```

**Standard source**: SEC comment letter requiring basic program 
description (URL from research). The standard is: "An investor must 
be able to understand what the drug is, what it treats, and where it 
is in development."

No case law needed here — this is purely an SEC review practice.

### CHECK 2: PHASE LABELS

```python
def check_phase_labels(candidate_passages):
    """
    INPUTS: all S-1 passages for this drug candidate
    
    STEP 1 (CODE): regex for combined phase labels:
        Pattern: r'Phase\s*[12]\s*/\s*[23]' (and variations)
        Also: "Phase 1/2a", "Phase 2a/2b", "Phase 2/3"
    
    IF no combined labels found → GREEN, done.
    
    IF combined labels found → STEP 2:
    
    STEP 2 (CODE): For each combined label, extract 1000 chars 
    surrounding context. Search within that context for:
        - "Phase 1 portion" / "dose escalation" / "MTD" / "RP2D"
        - "Phase 2 portion" / "expansion" / "efficacy" / "activity"
        - "transition" / "criteria" / "trigger"
    
    IF explanation found → GREEN (label explained)
    IF explanation NOT found → YELLOW
    
    STEP 3 (LLM CALL — only if YELLOW):
    Prompt: "The S-1 uses the label '[combined label]' in this 
    context: '[passage]'. The SEC has required companies to explain 
    what each phase portion involves. Here is the SEC's comment in 
    a comparable situation: '[EXACT comment letter language]'. 
    Does this S-1 passage adequately explain both portions?"
    
    OUTPUT: Table with each combined label instance, context, and 
    whether explanation is present.
    """
```

**Standard source**: SEC comment letter on phase nomenclature (URL).
**Precedent language to compare**: "[EXACT SEC comment from the letter]"

### CHECK 3: PRECLINICAL FRAMING

```python
def check_preclinical_framing(candidate_passages):
    """
    STEP 1 (CODE): Identify preclinical references.
    grep for: "preclinical", "animal", "mouse", "rat", "primate",
    "in vitro", "in vivo", "xenograft", "DIO model", "knockout"
    
    IF none found → N/A, skip.
    
    STEP 2 (CODE): For each preclinical reference, check for 
    translation risk caveat within 2000 chars:
    grep for: "may not be predictive", "no assurance", 
    "animal.*not.*predict", "preclinical.*may not.*translate"
    → CAVEAT PRESENT or CAVEAT ABSENT
    
    STEP 3 (CODE): Check MoA language.
    Extract all sentences containing the drug's mechanism description.
    Classify each as:
    - HYPOTHETICAL: contains "designed to", "intended to", "aims to",
      "believed to", "may", "potentially"
    - FACTUAL: contains "has shown", "demonstrates", "induces", 
      "activates", "inhibits" WITHOUT qualifying language
    
    IF all hypothetical → GREEN
    IF any factual → STEP 4
    
    STEP 4 (LLM CALL): For each factual MoA statement:
    Prompt: "This S-1 states: '[exact MoA statement]'. 
    This describes the drug's mechanism of action using factual 
    language ('[specific verb]') rather than hypothetical framing.
    
    The SEC has challenged similar language. In [company]'s S-1, 
    the SEC commented: '[EXACT comment letter text]'.
    
    Is this S-1's MoA statement:
    (a) Supported by clinical (human) data cited elsewhere in the S-1?
    (b) Based only on preclinical data but stated as established fact?
    (c) Appropriately qualified despite the factual verb?"
    
    OUTPUT: Each MoA statement, classification, and assessment.
    """
```

### CHECK 4: COMPARATIVE CLAIMS

```python
def check_comparative_claims(candidate_passages):
    """
    STEP 1 (CODE): Scan for comparative language near candidate name.
    Patterns: "safer", "more effective", "superior", "differentiated",
    "best-in-class", "first-in-class", "improved over", "advantage",
    "compared favorably", "outperform"
    
    IF none found → GREEN, skip.
    
    STEP 2 (CODE): For each hit, extract 1500 chars context.
    Search within context for evidence basis:
    - "head-to-head" / "direct comparison" / "comparative trial"
    - A citation to a specific trial comparing the drugs
    → HEAD_TO_HEAD_CITED or NO_DIRECT_COMPARISON
    
    STEP 3 (LLM CALL — for each hit without head-to-head):
    Prompt: "The S-1 makes this comparative statement about 
    [candidate]: '[exact quote]'.
    
    No head-to-head clinical trial is cited to support this 
    comparison. The SEC has challenged similar language:
    '[EXACT comment letter text from comparable letter]'.
    
    In that case, the SEC asked: '[what the SEC required]'.
    
    How does this S-1's language compare to the language the 
    SEC challenged? Is it:
    (a) Materially similar (same type of unsupported comparison)
    (b) Distinguishable (this S-1 has qualifications the other lacked)
    (c) More aggressive than the language the SEC challenged"
    
    OUTPUT: Each comparative claim, basis, and comparison result.
    """
```

**KEY DESIGN POINT**: The LLM is NOT reasoning about the law from 
scratch. It is given the SPECIFIC precedent language and asked to 
COMPARE — a much more constrained and reliable task.

### CHECK 5: FDA COMMUNICATIONS

```python
def check_fda_communications(candidate_passages):
    """
    STEP 1 (CODE): Extract all FDA-related passages.
    grep for: "FDA", "Food and Drug Administration", "IND", "NDA", 
    "BLA", "Breakthrough", "Fast Track", "Orphan", "Priority Review",
    "pre-IND", "End-of-Phase", "SPA", "CRL", "PDUFA"
    
    STEP 2 (CODE): Classify each passage:
    - POSITIVE: "aligned", "agreed", "positive feedback", 
      "constructive", "granted", "designated", "approved"
    - NEGATIVE: "denied", "refused", "required additional", 
      "concerns", "deficiency", "refuse to file", "CRL"
    - NEUTRAL: factual statements without characterization
    
    STEP 3 (CODE): Count:
    - Positive characterizations: [n] (list them with section)
    - Negative disclosures: [n] (list them with section)
    - Check placement: Are positive items in Business/Summary 
      and negative items only in Risk Factors?
    
    STEP 4 (ASSESSMENT):
    IF positive = 0 and negative = 0 → N/A
    IF positive > 0 and negative = 0 → RED (one-sided)
    IF positive > 0 and negative > 0:
      Check placement symmetry:
      IF positive in Business AND negative in Business → GREEN
      IF positive in Business AND negative ONLY in Risk Factors → YELLOW
    
    STEP 5 (LLM CALL — if YELLOW or RED):
    Prompt: "The S-1 describes FDA interactions for [candidate].
    
    POSITIVE characterizations (found in [sections]):
    [list each with exact quote and section/page]
    
    NEGATIVE disclosures (found in [sections]):
    [list each with exact quote and section/page]
    
    In SEC v. AVEO Pharmaceuticals (SEC LR-24062), the company 
    was charged with fraud for selectively disclosing positive 
    FDA interactions while omitting that the FDA had recommended 
    an additional clinical trial. The SEC stated: '[EXACT language 
    from complaint/release]'.
    
    In Tongue v. Sanofi, 816 F.3d 199 (2d Cir. 2016), the court 
    held: '[EXACT holding on FDA feedback disclosure]'.
    
    Compare this S-1's pattern of FDA disclosure to these precedents:
    (a) Is there material negative FDA feedback that is omitted 
        or asymmetrically placed?
    (b) Does the positive characterization create an impression 
        that the negative disclosure undermines?
    (c) How does the severity of asymmetry here compare to AVEO?"
    
    OUTPUT: Table of FDA characterizations, placement, symmetry 
    assessment, and precedent comparison.
    """
```

### CHECK 7: RED FLAG PHRASES

```python
def check_red_flag_phrases(candidate_passages, red_flag_list):
    """
    STEP 1 (CODE): For each phrase in red_flag_list, scan all 
    candidate passages. Record:
    - Phrase matched
    - Exact sentence containing it
    - Section and approximate page
    - 500 chars surrounding context
    
    STEP 2 (CODE): For each hit, classify context:
    CATEGORY A (CAUTIONARY): Phrase appears in:
      - Risk Factor section, OR
      - Conditional: "may not be [phrase]", "cannot assure [phrase]",
        "no guarantee of [phrase]"
      → AUTO GREEN — cautionary use is acceptable
    
    CATEGORY B (SUPPORTED): Phrase appears with quantitative data 
    within 500 chars:
      - AE rates (n/N, %), specific AE types
      - Statistical results (p-values, CIs)
      - Dose/response data
      → AUTO GREEN — supported by data
    
    CATEGORY C (STANDALONE): Phrase used affirmatively without 
    nearby data and NOT in cautionary context
      → FLAG for Step 3
    
    STEP 3 (LLM CALL — for each CATEGORY C hit):
    Prompt: "The S-1 uses '[phrase]' in this context:
    '[exact passage with 500 chars context]'
    Section: [section name], approx. page [n]
    
    This usage is:
    - Not in a cautionary/conditional context
    - Not immediately supported by quantitative data
    
    The SEC has challenged similar language. In a comment letter 
    to [company], the SEC stated:
    '[EXACT SEC comment text]'
    The S-1 language that triggered this comment was:
    '[EXACT S-1 language from that company]'
    
    Compare this S-1's usage to the language the SEC challenged.
    Is this instance:
    (a) Comparable — similar standalone use without data support
    (b) Distinguishable — this context provides implicit support
    (c) Worse — more affirmative/absolute than the challenged language"
    
    STEP 4 (ACCUMULATION — CODE):
    Count total instances per phrase across all categories.
    If any single phrase has >10 STANDALONE instances → 
    PATTERN flag regardless of individual assessments.
    
    OUTPUT: Table with every instance, category, and assessment.
    Also: summary count showing pattern if applicable.
    """
```

### CHECK 8: TRIAL DESIGN MATCH (Pass 2)

```python
def check_trial_design(s1_passages_for_trial, ctgov_json):
    """
    This is almost entirely mechanical. Code builds the comparison 
    table. LLM is called ONLY for materiality assessment of gaps.
    
    STEP 1 (CODE): Extract from CTgov JSON:
    - phase = protocolSection.designModule.phases[]
    - allocation = protocolSection.designModule.designInfo.allocation
    - masking = protocolSection.designModule.designInfo.maskingInfo.masking
    - enrollment_n = protocolSection.designModule.enrollmentInfo.count
    - enrollment_type = protocolSection.designModule.enrollmentInfo.type
    - arms = protocolSection.armsInterventionsModule.armGroups[]
    - primary_endpoints = protocolSection.outcomesModule.primaryOutcomes[]
    - secondary_endpoints = protocolSection.outcomesModule.secondaryOutcomes[]
    
    STEP 2 (CODE): For each element, search S-1 passages for match:
    - Phase: grep for "Phase [n]" 
    - Allocation: grep for "randomized", "non-randomized", "single-arm"
    - Masking: grep for "double-blind", "open-label", "single-blind",
      "placebo-controlled"
    - Enrollment: grep for numbers near "patients", "subjects", 
      "participants", "enrolled"
    - Endpoints: grep for each endpoint measure term
    
    STEP 3 (CODE): Mark each element:
    - MATCH: S-1 and CTgov agree
    - ABSENT: Element in CTgov but not found in S-1
    - PARTIAL: Related language found but not exact
    - MISMATCH: S-1 says something different from CTgov
    
    STEP 4 (LLM CALL — only for ABSENT or MISMATCH items):
    For each: "This trial element is [ABSENT/MISMATCHED]:
    CTgov says: [exact value]
    S-1 says: [exact passage or 'not found']
    
    The SEC has required disclosure of [this element] in comment 
    letters. Example: '[EXACT comment text]'.
    
    Would a reasonable investor consider this omission/mismatch 
    important? Consider: (a) Does this element affect how an 
    investor would interpret the trial results? (b) Is the 
    omitted information readily available elsewhere in the S-1?"
    
    OUTPUT: Full comparison table with color coding.
    """
```

### CHECK 9: ENDPOINT HIERARCHY (The Harkonen Check)

This is the most critical check. It MUST be precise.

```python
def check_endpoint_hierarchy(s1_passages_for_trial, ctgov_json):
    """
    STEP 1 (CODE): Extract endpoint hierarchy from CTgov:
    primary_endpoints = outcomesModule.primaryOutcomes[] 
        → list of {measure, description, timeFrame}
    secondary_endpoints = outcomesModule.secondaryOutcomes[]
        → list of {measure, description, timeFrame}
    
    IF resultsSection exists:
        outcome_measures = outcomeMeasuresModule.outcomeMeasures[]
        For each: extract type (PRIMARY, SECONDARY, OTHER, POST_HOC)
        Check: did primary endpoint SUCCEED or FAIL?
        (Look at analyses[].pValue, or if no p-value, the direction 
        of effect vs what was expected)
    
    STEP 2 (CODE): Map S-1 passages to endpoints.
    For each endpoint (primary and secondary):
        Search S-1 passages for the endpoint measure term
        → DISCUSSED / NOT DISCUSSED
    
    STEP 3 (CODE): Identify what the S-1 LEADS WITH.
    The "headline finding" = the first efficacy result mentioned 
    in the Prospectus Summary or first mention in the Business 
    section for this trial.
    
    STEP 4 (CODE): THE HARKONEN PATTERN CHECK
    Conditions for RED flag (ALL must be true):
    A. The S-1 headline finding is from a SECONDARY or unregistered 
       endpoint
    B. The PRIMARY endpoint either:
       - Is not discussed at all, OR
       - Showed a null/negative result that is not highlighted
    C. The S-1 does not clearly label the headline finding as 
       secondary/exploratory
    
    IF A + B + C → RED — Harkonen pattern detected
    IF A + B but S-1 labels it as secondary → YELLOW
    IF primary endpoint is discussed prominently → GREEN
    
    STEP 5 (LLM CALL — if YELLOW or RED):
    This is where we do the DETAILED precedent comparison.
    
    Prompt: "ENDPOINT HIERARCHY ANALYSIS
    
    ClinicalTrials.gov shows this trial's endpoint structure:
    PRIMARY endpoint: [measure] — Result: [result or 'not posted']
    SECONDARY endpoints: [list] — Results: [results or 'not posted']
    
    The S-1 presents this trial as follows:
    HEADLINE (first mention): '[exact S-1 quote, section, page]'
    Primary endpoint discussion: '[exact quote or NOT FOUND]'
    
    PRECEDENT COMPARISON:
    
    In United States v. Harkonen (InterMune), the CEO was 
    convicted of wire fraud for the following pattern:
    - Trial primary endpoint: progression-free survival → 
      FAILED (p=0.52)
    - Press release headline: post-hoc subgroup analysis → 
      appeared significant (p=0.004)  
    - The press release [exact language from the case if available]
    - The primary failure was mentioned but buried
    - The court found this constituted wire fraud because [holding]
    
    In SEC v. Clovis Oncology, the company was penalized for:
    - Reporting 60% ORR using unconfirmed responses
    - Actual confirmed ORR was 28%
    - The metric definition was non-standard and undisclosed
    
    Compare this S-1's endpoint presentation pattern:
    1. Is the S-1's headline finding from the primary endpoint?
    2. If not, is the primary endpoint result also disclosed?
    3. Is the hierarchy (primary vs secondary) clearly stated?
    4. How closely does this pattern match Harkonen?
    5. Are any metrics non-standard (compare to Clovis)?
    
    Rate similarity to Harkonen pattern: 
    HIGH / MODERATE / LOW / NOT APPLICABLE"
    
    STEP 6 (RESEARCH AUGMENTATION — if RED):
    Search for more recent cases involving endpoint promotion.
    Use web search or sec-api.io to find:
    - Recent SEC enforcement actions involving clinical trial 
      disclosure
    - Recent comment letters challenging endpoint presentation
    This provides additional context for the specific finding.
    
    OUTPUT: Full endpoint hierarchy analysis with precedent 
    comparison and similarity rating.
    """
```

### CHECK 10: SAFETY DATA MATCH

```python
def check_safety_data(s1_passages_for_trial, ctgov_json):
    """
    STEP 1 (CODE): Extract from CTgov (if results posted):
    event_groups = adverseEventsModule.eventGroups[]
    For each group: deathsNumAffected, seriousNumAffected, 
                    seriousNumAtRisk, otherNumAffected, otherNumAtRisk
    serious_events = adverseEventsModule.seriousEvents[]
    other_events = adverseEventsModule.otherEvents[]
    
    Calculate: overall AE rate, SAE rate, death rate per arm
    
    STEP 2 (CODE): Extract safety characterizations from S-1:
    grep for: "well-tolerated", "safe", "safety profile", "adverse",
    "SAE", "serious adverse", "TEAE", "treatment-emergent", "death"
    
    STEP 3 (CODE): DIRECT COMPARISON
    For each S-1 safety claim, compare to CTgov data:
    
    S-1 says "well-tolerated" → CTgov AE rate = ?
    S-1 says "no SAEs" → CTgov SAE count = ?
    S-1 says "no deaths" → CTgov death count = ?
    S-1 says "[specific AE] was the most common" → CTgov confirms?
    
    Mark: SUPPORTED / CONTRADICTED / UNVERIFIABLE (no results posted)
    
    STEP 4 (CODE): Check results posting compliance.
    status = protocolSection.statusModule.overallStatus
    IF status == "COMPLETED":
        IF resultsSection present → results posted
        IF resultsSection absent:
            Calculate months since completion
            IF > 12 months → RED (FDAAA 801 potential non-compliance)
            Note: "Results not posted. S-1 claims about this trial 
            cannot be independently verified."
    
    STEP 5 (LLM CALL — if any CONTRADICTED):
    Prompt: "SAFETY DATA COMPARISON
    
    The S-1 states: '[exact safety characterization, section, page]'
    
    ClinicalTrials.gov data for this trial shows:
    - Overall AE rate: [n/N] ([%]) on drug vs [n/N] ([%]) on placebo
    - SAE rate: [n/N] ([%]) on drug vs [n/N] ([%]) on placebo
    - Deaths: [n] on drug vs [n] on placebo
    - Specific AEs: [list top 5 with rates]
    
    The S-1's characterization appears [CONTRADICTED/UNSUPPORTED] 
    because [specific discrepancy].
    
    The SEC has challenged similar safety characterizations:
    '[EXACT comment letter language]'
    
    Compare the severity of the discrepancy here to the language 
    the SEC challenged. How material is the gap between the S-1's 
    characterization and the actual data?"
    
    OUTPUT: Safety comparison table with data, S-1 claims, and 
    match status.
    """
```

### LAYER 2 ESCALATION: OMNICARE TEST

Only runs on findings from Layer 1 that involve OPINION STATEMENTS 
(characterizations, "we believe" language, adjectives like 
"well-tolerated" or "demonstrated clinical activity").

```python
def escalation_omnicare(finding, s1_text, contrary_facts):
    """
    TRIGGER: Layer 1 produced a YELLOW or RED finding involving 
    an opinion/characterization in the S-1.
    
    INPUTS:
    - finding: the Layer 1 finding (what was flagged and why)
    - s1_text: the exact S-1 opinion statement
    - contrary_facts: the specific facts from CTgov or elsewhere 
      that cut against the opinion
    
    STEP 1 (LLM CALL with specific comparison):
    Prompt: "OMNICARE OPINION ANALYSIS
    
    BACKGROUND: In Omnicare, Inc. v. Laborers District Council, 
    575 U.S. 175 (2015), the Supreme Court held that opinion 
    statements in registration statements can give rise to § 11 
    liability in two circumstances:
    
    [EXACT QUOTE FROM OPINION — Test 1 on embedded facts]
    [EXACT QUOTE FROM OPINION — Test 2 on omitted contrary facts]
    
    The Court also noted the LIMITING PRINCIPLE:
    [EXACT QUOTE about not every opinion being accurate]
    
    APPLICATION TO THIS FINDING:
    
    S-1 Opinion Statement: '[exact quote, section, page]'
    
    Known Contrary Facts:
    [list each specific fact with source (CTgov field path, 
    section of S-1, etc.)]
    
    TEST 1 — EMBEDDED FACT:
    Does '[s1_text]' embed a factual claim? If so, what is it?
    Is the embedded fact supported by the available data?
    
    TEST 2 — OMITTED CONTRARY FACTS:
    The following facts appear to cut against the impression 
    this opinion creates: [contrary_facts].
    Are these facts disclosed in the S-1?
    If not, would their omission be material to a reasonable 
    investor?
    
    LIMITING PRINCIPLE CHECK:
    Given the Court's instruction that not every opinion need 
    be accurate, is this a case where the Omnicare tests are 
    genuinely triggered, or is this normal opinion language that 
    investors would understand involves judgment?
    
    RATE: Does this opinion raise questions under Omnicare?
    SIGNIFICANT RISK / MODERATE RISK / LOW RISK / NO CONCERN
    Explain which test(s) are triggered and why."
    
    STEP 2 (RESEARCH — if SIGNIFICANT RISK):
    Search for post-Omnicare cases (2015-present) applying the 
    three-part test to similar types of statements (safety claims, 
    efficacy claims, regulatory characterizations in biotech S-1s).
    
    This adds specificity: not just "Omnicare says X" but "since 
    Omnicare, courts have applied this test to similar language 
    in [case], finding [result]."
    """
```

### LAYER 2 ESCALATION: RULE 408 PATTERN

```python
def escalation_rule_408(all_findings):
    """
    TRIGGER: Multiple YELLOW or RED findings exist from Layer 1.
    
    STEP 1 (CODE): Tabulate all findings.
    For each finding, classify direction:
    - FAVORS_COMPANY: An omission/gap that makes the drug look 
      better than the data supports
    - NEUTRAL: A gap that doesn't clearly favor either direction
    - DISFAVORS_COMPANY: An omission that makes the drug look 
      worse (rare — companies don't usually omit positive data)
    
    STEP 2 (CODE): Calculate:
    total_findings = len(all_findings)
    favors_company = count where direction == FAVORS_COMPANY
    pct_one_sided = favors_company / total_findings
    
    IF pct_one_sided < 0.5 → GREEN (no pattern)
    IF 0.5 <= pct_one_sided < 0.75 → YELLOW (possible pattern)
    IF pct_one_sided >= 0.75 → RED (strong pattern)
    
    STEP 3 (LLM CALL — if YELLOW or RED):
    Prompt: "RULE 408 PATTERN ANALYSIS
    
    Rule 408 (17 C.F.R. § 230.408) requires:
    '[EXACT regulatory text]'
    
    Across [n] findings, [favors_company] ([pct]%) involve 
    omissions or de-emphases that favor the company:
    
    [table of all findings with direction]
    
    This pattern raises questions about whether the S-1's 
    clinical trial disclosures, taken as a whole, would give 
    a reasonable investor a misleadingly optimistic view of 
    the clinical program.
    
    Assess: Is this pattern consistent and systematic, or are 
    there reasonable explanations for individual omissions?"
    
    OUTPUT: Pattern table, direction counts, and assessment.
    """
```

---

## SEC-API.IO INTEGRATION

API key: 7ef2ddea736b769ac2d44f2d63717165bd777168b8bdbb8101e6c52087275ca0
Endpoint: https://sec-api.io/

**IMPORTANT**: We have only 100 API calls. Use as FALLBACK for 
targeted research, not bulk queries.

**When to use**:
1. When a RED finding needs additional precedent comparison and 
   EDGAR full-text search doesn't return good results
2. When searching for specific S-1 language that was challenged 
   in comment letters
3. When the starting comment letter URLs from our research don't 
   resolve

**How to use**:
```python
import requests

headers = {"Authorization": "7ef2ddea736b769ac2d44f2d63717165bd777168b8bdbb8101e6c52087275ca0"}

# Full-text search for comment letters
response = requests.get(
    "https://efts.sec-api.io/v1",
    params={
        "query": '"well-tolerated" AND formType:"CORRESP"',
        "from": "0",
        "size": "10"
    },
    headers=headers
)
```

**Budget allocation** (100 calls):
- 30 calls: Building reference files (comment letter research)
- 50 calls: Runtime research augmentation (on RED findings)
- 20 calls: Reserve

**Fallback when sec-api.io calls exhausted**:
Use EDGAR full-text search (free, no limit):
https://efts.sec.gov/LATEST/search-index?q="well-tolerated"&forms=CORRESP

---

## WHAT CLAUDE CODE SHOULD BUILD

### Step 1: Write s1_checker_skill_spec_v4.md

Take everything above and produce a clean, comprehensive spec document 
that includes:
- The full architecture diagram (Layer 1 → Layer 2 tree)
- Every check operationalized as pseudocode with exact inputs/outputs
- The LLM prompt templates for each check (with slots for precedent 
  language that will be filled from reference files)
- The escalation rules (when Layer 2 triggers)
- The calibration rules from v3 (risk areas, not legal conclusions)
- The interaction flow from v3 (full process explanation upfront, 
  tables, color coding, auto-flow)
- Attribution (Jesus Alcocer, Norm.ai)

### Step 2: Rebuild reference files

Using the research already in the repo (from the previous Claude Code 
sessions), rebuild:

**reference/legal_framework.json**: 
- For each case, include the ACTUAL LANGUAGE (holding, key quotes)
- For each comment letter, include the ACTUAL SEC COMMENT TEXT
- For each enforcement action, include the ACTUAL FACTS and language
- These are what get inserted into the LLM prompt templates

**reference/operationalized_checks.json** (NEW — replaces check_descriptions.json):
- For each check: the pseudocode logic, thresholds, grep patterns
- The LLM prompt template with slots marked as {{PRECEDENT_LANGUAGE}}, 
  {{S1_TEXT}}, {{CTGOV_DATA}}
- The specific comment letter excerpt IDs that apply

**reference/comment_letter_excerpts.json**:
- Actual verbatim SEC comments organized by topic
- The S-1 language that triggered each comment
- What the company was required to do

**reference/guardrails.json**:
- Omnicare three-part test with EXACT QUOTES from the opinion
- Rule 408 pattern analysis with thresholds
- Matrixx with EXACT HOLDING LANGUAGE
- Calibration language for each

### Step 3: Update SKILL.md

The orchestrator prompt must reflect v4:
- Layer 1 → Layer 2 architecture
- Auto-flow with pauses on findings
- Table-driven output
- Research augmentation on RED findings
- Calibration language throughout

### Step 4: Update README.md

The README should describe:
- What this tool does (for someone evaluating the repo)
- The architecture (code vs LLM, Layer 1 vs Layer 2)
- The legal framework (in brief — point to spec for detail)
- How to run it
- Attribution
- File structure with descriptions

### Step 5: Ensure all docs reference each other consistently

- SKILL.md references the spec version (v4)
- README.md references the spec and SKILL.md
- Reference files are named consistently
- No orphaned references to "modules" or v2/v3 concepts

---

## RESEARCH IMPROVEMENTS

When doing the legal research for reference files, apply these 
principles:

### 1. Get the ACTUAL DISCLOSURE LANGUAGE, not just holdings

For every enforcement case, we need TWO things:
- The LEGAL HOLDING (what the court/SEC said the law requires)
- The ACTUAL S-1/PRESS RELEASE LANGUAGE that was at issue

For Harkonen: What did the InterMune press release actually say?
Get the exact words. This is what we compare new S-1 language TO.

For Clovis: What did Clovis's filings actually say about ORR?
Get the exact words.

For AVEO: What did AVEO's filings say about FDA interactions?
Get the exact words.

The comment letter research should ALSO capture the S-1 language 
that triggered each comment — not just the SEC's comment.

### 2. Search for the actual documents

Tools available:
- EDGAR full-text search: https://efts.sec.gov/LATEST/search-index
- SEC litigation releases (link to complaints which quote the language)
- sec-api.io (100 calls — use sparingly)
- Web search for news coverage that quotes the language
- Casetext/Justia for court opinions that quote the language

### 3. Build comparison pairs

The reference files should contain PAIRS:
```json
{
  "comparison_pair": {
    "problematic_language": "[exact quote from the S-1/press release that was challenged]",
    "source": "InterMune press release, August 28, 2002",
    "what_was_wrong": "Led with post-hoc subgroup (p=0.004), buried primary failure (p=0.52)",
    "legal_consequence": "Criminal wire fraud conviction",
    "comparison_instruction": "If the S-1 being analyzed presents a secondary/exploratory endpoint result as the headline finding while the primary endpoint result is omitted or buried, this pattern is analogous to Harkonen."
  }
}
```

These pairs are what the LLM uses for TEXT-TO-TEXT comparison.

### 4. Search for post-decision developments

For Omnicare (2015): Search for circuit court cases applying 
Omnicare in the biotech/pharma context (2015-2025). How have 
courts interpreted the three-part test for clinical trial 
opinions specifically?

For Matrixx (2011): Search for cases where companies tried to 
invoke a statistical significance defense post-Matrixx. How has 
the doctrine been applied?

This makes the analysis more current and specific.

---

## KICKOFF PROMPT FOR CLAUDE CODE

```
Read s1_checker_skill_spec_v4_instructions.md in this repo. 
This contains comprehensive instructions for building v4 of 
the S-1 clinical trial disclosure checker.

The key change: the legal framework is now operationalized as 
a decision tree. Every check is a function with concrete inputs, 
comparison logic, and escalation rules. The LLM is called with 
specific precedent language for text-to-text comparison, not 
for open-ended legal reasoning.

Follow the build order in the instructions:
1. First write s1_checker_skill_spec_v4.md (the clean spec)
2. Then rebuild reference files with operationalized checks
3. Then update SKILL.md
4. Then update README.md
5. Verify all docs are consistent

For the legal research in the reference files:
- Get ACTUAL LANGUAGE from cases and comment letters, not summaries
- Build comparison pairs (problematic language + what was wrong)
- Search for post-decision developments
- Use EDGAR full-text search as primary tool
- Use sec-api.io SPARINGLY (100 call budget)

Commit after each major step so I can review progress.
Start with Step 1 (the spec document).
```
