<!-- ANCHOR: CHECK_6_PIPELINE -->
═══════════════════════════════════════════════════════════════
CHECK 6: PIPELINE ACCURACY
═══════════════════════════════════════════════════════════════

LAW / STANDARD BEING CHECKED:

  If the S-1 includes a pipeline table or graphic, the phase
  designations must accurately reflect the regulatory status of
  each program AND must match the text descriptions elsewhere
  in the document. Two sub-issues:

  (A) LABEL ACCURACY: Pipeline table must use standard FDA phase
      designations (Phase 1, Phase 2, Phase 3), not marketing
      terminology ("Pivotal", "Registrational", "Late-Stage").
      Combined labels ("Phase 1/2") are subject to the same
      concerns as Check 2.

  (B) TABLE-TO-TEXT CONSISTENCY: If the pipeline table shows a
      program in "Phase 2" but the text describes it as "Phase 1
      dose escalation," there is an internal inconsistency that
      could mislead investors about the program's actual stage.

  Rule 408 (17 C.F.R. § 230.408): Material information must not
  be misleading. A pipeline graphic that overstates development
  stage is misleading.


───────────────────────────────────────────────────────────────
SOURCES / AUTHORITIES — SEC COMMENT LETTERS + CHALLENGED S-1 TEXT
───────────────────────────────────────────────────────────────

<!-- ANCHOR: COMPARISON_PAIR_TAYSHA_PIPELINE -->
COMPARISON PAIR 1: TAYSHA GENE THERAPIES (S-1, filed Sep. 1, 2020)

  S-1 TEXT THAT WAS CHALLENGED:

    [PLACEHOLDER — FETCH FROM:
    https://www.sec.gov/Archives/edgar/data/1806310/
    000119312520247565/d938924ds1a.htm

    Known from comment letter and search results: Taysha's S-1
    included a pipeline table showing:
    - Multiple product candidates labeled "Phase 1/2"
    - "Pivotal" column instead of "Phase 3"
    - Separate "Preclinical" and "IND-enabling" columns

    The pipeline table was a graphic showing TSHA-118, TSHA-120,
    TSHA-104, and other candidates across development stages.

    NEED: The actual pipeline table/graphic description, plus the
    text descriptions of each program's status to show the
    table-vs-text comparison the SEC was concerned about.]

  SEC COMMENT LETTER (Sep. 1, 2020) — THREE REQUIREMENTS:

    Requirement 1 — Phase Labels:
    "Include separate columns for Phase 1 and Phase 2 trials or
    tell us the basis for your belief that you will be able to
    conduct Phase 1/2 trials for all your product candidates."

    Requirement 2 — "Pivotal" → "Phase 3":
    [The SEC required Taysha to replace "Pivotal" with "Phase 3"
    in the pipeline table. "Pivotal" is marketing terminology
    that obscures the regulatory phase designation.]

    Requirement 3 — Column Consolidation:
    [The SEC required merging "Preclinical" and "IND-enabling"
    into a single column, as "IND-enabling" implied a more
    advanced preclinical stage that doesn't correspond to a
    standard regulatory designation.]

  WHAT THE SEC CHALLENGED:
  - Pipeline tables are visual summaries investors rely on for
    quick assessment. If the visual suggests more progress than
    the text supports, it's misleading.
  - "Pivotal" sounds like a regulatory milestone, but it's not
    an FDA-recognized phase designation.
  - Showing "Phase 1/2" in the table without justification
    implies a combined trial design that may not exist.
  - Extra columns ("IND-enabling") create visual impression of
    more development stages = more progress.

  KEY PATTERN: The SEC treats pipeline graphics as visual claims
  subject to the same disclosure standards as text. A misleading
  graphic is treated identically to a misleading text statement.

  SOURCE: SEC comment letter to Taysha Gene Therapies, Sep. 1, 2020


COMPARISON PAIR 2: ALTAMIRA THERAPEUTICS (F-1, Feb. 24, 2023)

  The Altamira letter (primarily about red flag phrases — Check 7)
  also referenced the pipeline presentation. While the main thrust
  was safety/efficacy language, the SEC's instruction to "remove
  all statements throughout your registration statement" included
  pipeline-adjacent claims about trial results.

  [Cross-reference to Check 7 for Altamira's full comparison pair.]


ADDITIONAL AUTHORITY — GENERAL SEC GUIDANCE:

  The SEC has issued multiple comment letters requiring:
  - "Phase 3" not "Pivotal" or "Registration-enabling"
  - "Phase 1" not "First-in-human" in pipeline tables
  - Removal of "Lead optimization" as a separate stage
  - Consistency between pipeline graphic coloring/shading and
    the actual trial status described in text

  The underlying principle: pipeline tables should use standard
  FDA terminology and should not use visual design (wider bars,
  additional columns, marketing labels) to imply more progress.


───────────────────────────────────────────────────────────────
HOW THIS CHECK WAS PROCESSED:
───────────────────────────────────────────────────────────────

  Script: s1_parser.py → _extract_pipeline_table()

  STEP A — TABLE DETECTION:
  Code scans for HTML <table> elements containing phase-related
  keywords ("Phase", "Preclinical", "IND", "Clinical"). If found,
  parses into structured data: {candidate_name, phase_claimed,
  indication}.

  STEP B — IMAGE DETECTION:
  If no HTML table found, checks for <img> tags near pipeline-
  related headers ("Our Pipeline", "Product Pipeline",
  "Development Pipeline"). If image found → table is embedded
  as a graphic → cannot parse programmatically.

  STEP C — TABLE-TO-TEXT CROSS-REFERENCE (if HTML table found):
  For each candidate in the pipeline table:
  1. Search all candidate passages for the same drug name
  2. Extract phase mentions from text
  3. Compare: table says "Phase 2" + text says "Phase 1 dose
     escalation" = MISMATCH → flag
  4. Check for marketing labels: "Pivotal", "Registrational",
     "Registration-enabling", "Lead optimization" → flag

  STEP D — COMBINED LABEL CHECK (if HTML table found):
  Check table for "Phase 1/2" or "Phase 2/3" → triggers Check 2
  cross-reference.


───────────────────────────────────────────────────────────────
S-1 TEXT FOUND [FOR THE S-1 UNDER REVIEW]:
───────────────────────────────────────────────────────────────

  Pipeline graphic is embedded as an IMAGE file — not an HTML
  table. Code cannot extract phase claims from the graphic to
  compare against text.

  [PLACEHOLDER — describe the AARD pipeline graphic if visible
  in the S-1: what candidates are shown, what phases are
  indicated visually, and how this compares to the text
  descriptions of each program.]

  Known from text scan:
  - ARD-101: described as Phase 2a in text
  - ARD-201: described as preclinical/IND-enabling in text
  - Pipeline graphic presumably shows both — but cannot verify
    programmatically


───────────────────────────────────────────────────────────────
ESCALATION TRIGGERS:
───────────────────────────────────────────────────────────────

  TRIGGER 1: Image-embedded pipeline → CANNOT VERIFY
  PROGRAMMATICALLY → 🟡 YELLOW (manual review needed).

  TRIGGER 2: HTML pipeline table with phase mismatch to text →
  ESCALATE TO LLM for severity assessment.

  TRIGGER 3: Marketing labels in pipeline table ("Pivotal",
  "Registrational") → ESCALATE (Taysha pattern).

  TRIGGER 4: Combined labels in pipeline table → cross-reference
  Check 2.


───────────────────────────────────────────────────────────────
STATUS: 🟡 YELLOW (cannot verify programmatically)
───────────────────────────────────────────────────────────────

  Pipeline graphic embedded as image. Recommend manual review
  to verify:
  (a) Phase designations match text descriptions
  (b) No marketing labels used ("Pivotal", "Registration-
      enabling")
  (c) No combined labels without justification
  (d) No visual design implying more progress than described

  This is a known limitation of automated parsing. If the S-1
  is converted to a format with an extractable pipeline table,
  the check can be re-run at full fidelity.


═══════════════════════════════════════════════════════════════
ESCALATION PROMPT DESIGN — CHECK 6
(fires only when HTML pipeline table is found with issues)
═══════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────
STEP 1: TABLE-TO-TEXT CONSISTENCY ANALYSIS
───────────────────────────────────────────────────────────────

SYSTEM CONTEXT:
  You are reviewing an S-1 pipeline table for consistency with
  the S-1's text descriptions and compliance with SEC standards.
  The SEC requires pipeline tables to use standard FDA phase
  designations, not marketing terminology.

SLOT 1 — EXTRACTED PIPELINE TABLE:
  [Structured data: {candidate, phase_in_table, indication}
  for each row.]

SLOT 2 — TEXT PHASE DESCRIPTIONS:
  [For each candidate: all phase mentions found in text, with
  section and page.]

SLOT 3 — SEC COMMENT LETTER:
  TAYSHA: "Include separate columns for Phase 1 and Phase 2...
  replace 'Pivotal' with 'Phase 3'... merge 'Preclinical' and
  'IND-enabling'."

SLOT 4 — STRUCTURED ANALYSIS QUESTIONS:

  For each candidate in the pipeline:

  (a) TABLE-TEXT MATCH: Does the phase in the table match the
      phase described in text?
      - Match → OK
      - Table says later phase than text → OVERSTATED
      - Table says earlier phase than text → UNDERSTATED (rare)

  (b) LABEL CHECK: Does the table use standard FDA phases?
      - "Phase 1", "Phase 2", "Phase 3" → OK
      - "Pivotal", "Registrational" → TAYSHA VIOLATION
      - "Phase 1/2" → CHECK 2 CROSS-REFERENCE
      - "IND-enabling" as separate column → TAYSHA VIOLATION

  (c) VISUAL DESIGN: Does the table use shading, arrows, or
      wider bars to imply more progress?

REQUIRED OUTPUT FORMAT:

  {
    "candidates": [
      {
        "name": "[drug name]",
        "phase_in_table": "[as shown]",
        "phase_in_text": "[from text passages]",
        "match": "CONSISTENT" | "OVERSTATED" | "UNDERSTATED",
        "label_standard": true | false,
        "label_issue": "[description]" | null
      }
    ],
    "marketing_labels_found": ["Pivotal", ...] | [],
    "combined_labels_found": ["Phase 1/2", ...] | [],
    "mismatches": 0,
    "step1_assessment": "CLEAR" | "CONCERN" | "SIGNIFICANT_CONCERN"
  }

DECISION TREE:

  CLEAR (no mismatches, standard labels) → 🟢 GREEN
  CONCERN (minor inconsistency or 1 marketing label) → 🟡 YELLOW
  SIGNIFICANT_CONCERN (overstatement or multiple issues) → 🔴 RED


═══════════════════════════════════════════════════════════════
<!-- ANCHOR: CHECK_7_RED_FLAGS -->
═══════════════════════════════════════════════════════════════
CHECK 7: RED FLAG PHRASES
═══════════════════════════════════════════════════════════════

LAW / STANDARD BEING CHECKED:

  The SEC has consistently challenged specific words and phrases
  in biotech S-1s that state or imply safety or efficacy
  determinations. The SEC's standard formulation appears in
  virtually every comment letter on this topic:

    "Safety and efficacy determinations are solely within the
    authority of the FDA."

  This check is DISTINCT from Check 3 (preclinical framing) and
  Check 5 (FDA communications) because it focuses on SPECIFIC
  WORDS regardless of context — the SEC challenges these phrases
  even when used to describe clinical trial results, even with
  qualifying language, and even for drugs with substantial human
  data.

  THE RED FLAG PHRASE LIST:

  TIER 1 — ALWAYS CHALLENGED (regardless of context):
  - "safe" (when describing the company's own drug, not in "safe
    harbor" or "safety" as a noun)
  - "effective" (when describing the company's own drug, not
    describing the market)
  - "safe and effective"
  - "safe and well tolerated"
  - "proven"
  - "established safety/efficacy"

  TIER 2 — CHALLENGED UNLESS SUPPORTED:
  - "well-tolerated" (permitted IF supported by AE data and SAE
    counts, per Altamira and OS Therapies)
  - "favorable safety profile" (challenged by Altamira, Graybug)
  - "acceptable safety profile" (challenged by Scopus)
  - "demonstrated clinical activity" (permitted IF accompanied
    by objective endpoint data)
  - "demonstrated efficacy" (challenged unless FDA-approved)

  TIER 3 — CONTEXT-DEPENDENT:
  - "promising" (preclinical context = challenged per Curanex;
    clinical context with data = borderline)
  - "encouraging" (similar to "promising")
  - "positive results" (borderline — depends on whether specific
    data accompanies it)

  THE SEC's PERMITTED ALTERNATIVES:
  - "well-tolerated" → PERMITTED if true AND supported by data
  - "no SAEs reported" / "no treatment-related SAEs" → PERMITTED
    if true
  - "the trial met its primary endpoint of [specific endpoint]
    with [specific result]" → PERMITTED (objective data)
  - "X% of patients achieved [endpoint]" → PERMITTED (objective)

  THE KEY DISTINCTION:
  CHALLENGED: "ARD-101 has demonstrated a favorable safety
  profile" (company's conclusion about safety)
  PERMITTED: "In the Phase 2a trial, treatment-related adverse
  events occurred in X% of patients; no SAEs were reported"
  (objective data, no safety conclusion)


───────────────────────────────────────────────────────────────
SOURCES / AUTHORITIES — SEC COMMENT LETTERS + CHALLENGED S-1 TEXT
───────────────────────────────────────────────────────────────

<!-- ANCHOR: COMPARISON_PAIR_ALTAMIRA -->
COMPARISON PAIR 1: ALTAMIRA THERAPEUTICS (F-1, Feb. 24, 2023)
— THE ANCHOR CASE

  S-1 TEXT THAT WAS CHALLENGED (pages 1, 11, 55-57, 79, 84,
  88, 89):

    [PLACEHOLDER — FETCH FROM ALTAMIRA F-1 (EDGAR):

    The SEC's comment letter identifies specific pages. Known
    challenged phrases from the letter:
    - "safe and effective" (describing OligoPhore/SemaPhore
      platform technology) — pages 1, 11
    - "safe and well tolerated" (describing clinical trial
      results) — pages 55-57
    - "favorable safety profile" (describing trial outcomes)
      — pages 84, 88, 89
    - Additional safety/efficacy language on page 79

    NEED: Full paragraphs from each of these pages showing:
    (a) The exact phrase in context
    (b) What section it appeared in
    (c) Whether any supporting data appeared nearby
    (d) Whether any caveat appeared nearby

    This is critical because Altamira is the ANCHOR CASE — the
    most detailed SEC comment letter on red flag phrases, with
    the most specific guidance on what IS and IS NOT permitted.]

  SEC COMMENT LETTER (Feb. 24, 2023) — THE FULL TEXT:

    "We note statements in numerous places throughout the
    registration statement stating or suggesting that your
    OligoPhore and SemaPhore peptide polyplex platform technology
    is 'safe and effective.' For example, on pages 1 and 11, you
    make reference to the 'favorable safety profile' and 'proven
    safety profile' of OligoPhore / SemaPhore nanoparticles, on
    page 79, you state that AM-401 'is designed to leverage the
    favorable safety profile and proven anti-tumor activity of
    anti-CTLA-4 agents' and the 'proprietary SemaPhore / AION
    delivery platform enables a favorable safety profile.'
    Similarly, your discussions of various clinical trials include
    statements that your product candidates are 'safe and well
    tolerated' or have a 'favorable safety profile,' such as on
    pages 55-57 and 84, 88, and 89. Please remove all statements
    throughout your registration statement that state or imply
    your conclusions regarding the safety or efficacy of your
    product candidates and technologies, as these determinations
    are solely within the authority of the FDA and comparable
    regulatory bodies. With respect to safety, we will not object
    to statements that your product candidates are well-tolerated,
    if true, or that no serious adverse events deemed to be study
    related were reported. You may also present a balanced summary
    of objective pre-clinical and clinical data, including whether
    clinical trials met primary and secondary endpoints, without
    including your conclusions related to efficacy."

  WHY THIS IS THE ANCHOR CASE:
  This is the most comprehensive SEC statement on red flag phrases
  because it provides:
  1. WHAT IS CHALLENGED: "safe and effective", "safe and well
     tolerated", "favorable safety profile", "proven safety
     profile", "proven anti-tumor activity"
  2. WHAT IS PERMITTED: "well-tolerated, if true", "no SAEs
     deemed study-related were reported"
  3. WHAT ELSE IS PERMITTED: "balanced summary of objective...
     data, including whether clinical trials met primary and
     secondary endpoints, without including your conclusions
     related to efficacy"
  4. THE STANDARD: "solely within the authority of the FDA"

  This letter is the TEMPLATE for Check 7 analysis.

  SOURCE: SEC comment letter to Altamira Therapeutics, Feb. 24, 2023


<!-- ANCHOR: COMPARISON_PAIR_GRAYBUG -->
COMPARISON PAIR 2: GRAYBUG VISION (S-1, Aug. 27, 2020)

  S-1 TEXT THAT WAS CHALLENGED (page 21 and elsewhere):

    [PLACEHOLDER — FETCH FROM GRAYBUG S-1 (EDGAR):

    Known: S-1 stated GB-102 demonstrated a "favorable safety
    and tolerability."

    NEED: Full paragraph from page 21 and any other instances
    identified in the comment letter.]

  SEC COMMENT LETTER (Aug. 27, 2020):

    "We note your references on page 21 and elsewhere that
    GB-102 demonstrated a 'favorable safety and tolerability.'
    Please revise your disclosure here and throughout your
    prospectus to remove your characterization of GB-102 as safe,
    as a determination of whether a product candidate is safe is
    solely within the authority of the U.S. Food and Drug
    Administration and comparable regulatory bodies."

  WHAT THE SEC CHALLENGED:
  - "favorable safety and tolerability" — even though "tolerability"
    is less aggressive than "efficacy," pairing it with "favorable
    safety" triggered the standard challenge.
  - "demonstrated" + "favorable safety" = company concluding its
    drug is safe based on trial data, which is FDA's determination.

  KEY PATTERN: "Favorable" + "safety" is a consistent trigger
  regardless of the specific formulation.

  SOURCE: SEC comment letter to Graybug Vision, Aug. 27, 2020


<!-- ANCHOR: COMPARISON_PAIR_MADRIGAL -->
COMPARISON PAIR 3: MADRIGAL PHARMACEUTICALS (10-K, Nov. 21, 2023)
— THE THREE-PART TEST

  10-K TEXT THAT WAS CHALLENGED (page 10):

    [PLACEHOLDER — FETCH FROM:
    https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany
    &CIK=0001157601 (Madrigal 10-K, filed ~Mar. 2023)

    Known: 10-K stated that Resmetirom "was safe and well
    tolerated."

    CRITICAL CONTEXT: Resmetirom was subsequently approved by
    the FDA as Rezdiffra on March 14, 2024. But at the time of
    the 10-K filing, it had NOT yet been approved. The SEC
    challenged the language even though the drug was in late-
    stage development with substantial clinical data.

    NEED: Full paragraph from page 10 showing the "safe and well
    tolerated" claim and surrounding context.]

  SEC COMMENT LETTER (Nov. 21, 2023) — THREE-PART REQUIREMENT:

    "(a) Determinations related to safety are within the sole
    authority of the FDA. In future filings, please refrain from
    making such assessments related to product candidates that
    have not been approved.

    (b) Additionally, please disclose all serious adverse events
    related to Resmetirom and disclose the number of such events.

    (c) Explain how you have determined that the candidate is well
    tolerated when trial participants experienced serious adverse
    events."

  WHAT THE SEC CHALLENGED:
  - Part (a): Restates the standard — only the FDA determines
    safety. Even for a Phase 3 drug with extensive data.
  - Part (b): AFFIRMATIVE OBLIGATION — if you claim "well
    tolerated," you must also disclose ALL SAEs. Cherry-picking
    positive data while omitting SAEs is misleading.
  - Part (c): THE LOGICAL TEST — if SAEs occurred, how can you
    call it "well tolerated"? You must explain the basis, or the
    characterization is unsupported.

  WHY THIS MATTERS:
  Madrigal is the most important comparison pair for companies
  that DO have clinical data (like AARD). Even with Phase 3
  data, the SEC said:
  - You cannot call your drug "safe"
  - If you call it "well tolerated," you must disclose SAEs
  - If SAEs occurred, you must explain why "well tolerated" is
    still accurate

  This creates the THREE-PART TEST for "well-tolerated":
  1. Is the characterization true? (Were AEs actually mild/moderate?)
  2. Are SAEs disclosed alongside the claim? (Balanced presentation)
  3. If SAEs occurred, is the basis for "well tolerated" explained?

  SOURCE: SEC comment letter to Madrigal, Nov. 21, 2023


<!-- ANCHOR: COMPARISON_PAIR_SCOPUS -->
COMPARISON PAIR 4: SCOPUS BIOPHARMA (Form 1-A, Jun. 24, 2020)

  Form 1-A TEXT THAT WAS CHALLENGED:

    [PLACEHOLDER — FETCH FROM SCOPUS 1-A (EDGAR):

    Known: Filing stated "NIH researchers demonstrated that
    MRI-1867 has an acceptable safety profile."

    NEED: Full paragraph with context.]

  SEC COMMENT LETTER (Jun. 24, 2020):

    "We note your disclosure that NIH researchers demonstrated
    that MRI-1867 has an acceptable safety profile. Safety is a
    determination that is solely within the authority of the FDA
    or similar foreign regulators."

  WHAT THE SEC CHALLENGED:
  - "acceptable safety profile" — even attributed to external
    researchers (NIH), the SEC challenged it. The attribution
    does NOT cure the problem — the S-1 is still presenting a
    safety conclusion.
  - "demonstrated" + "acceptable safety" = company (or third
    party) concluding the drug has adequate safety.

  KEY PATTERN: Attributing a safety conclusion to third-party
  researchers does NOT avoid the SEC challenge. The issue is that
  the conclusion appears in the S-1, not who made it.

  SOURCE: SEC comment letter to Scopus BioPharma, Jun. 24, 2020


<!-- ANCHOR: COMPARISON_PAIR_OS_THERAPIES -->
COMPARISON PAIR 5: OS THERAPIES (S-1, Mar. 27, 2023)

  S-1 TEXT THAT WAS CHALLENGED:

    [PLACEHOLDER — FETCH FROM OS THERAPIES S-1 (EDGAR):

    Known: S-1 stated "the data presented from the Phase Ib trial
    demonstrated that ADXS31-164 was well tolerated."

    NEED: Full paragraph with context, including what endpoint
    data (if any) appeared nearby.]

  SEC COMMENT LETTER (Mar. 27, 2023):

    "...investors should be able to assess how the drug candidate
    performed relative to the established endpoints, including
    whether the reported results were or were not statistically
    significant, and also assess your conclusion that 'the data
    presented from the Phase Ib trial demonstrated that
    ADXS31-164 was well tolerated.'"

  WHAT THE SEC CHALLENGED:
  - "demonstrated that [drug] was well tolerated" — even though
    "well tolerated" is on the SEC's PERMITTED list (per Altamira),
    the SEC challenged it here because the company drew a
    CONCLUSION ("demonstrated that") rather than presenting data
    and letting investors draw their own conclusion.
  - The SEC's instruction: investors should be able to "assess
    your conclusion" — meaning the data must be presented so
    investors can verify the claim independently.

  KEY PATTERN: "Well tolerated" is permitted ONLY IF:
  (a) It is true
  (b) It is supported by specific AE/SAE data nearby
  (c) Investors can independently verify the characterization
  Using "demonstrated that [drug] was well tolerated" converts
  it from a supported characterization to a company conclusion,
  which the SEC challenges.

  SOURCE: SEC comment letter to OS Therapies, Mar. 27, 2023


<!-- ANCHOR: THREE_TIER_CLASSIFICATION -->
───────────────────────────────────────────────────────────────
THE UNDERLYING SEC FRAMEWORK (synthesized from all 5 letters):
───────────────────────────────────────────────────────────────

  THE BRIGHT LINE RULE:
  "Safety and efficacy determinations are solely within the
  authority of the FDA."

  ┌─────────────────────────────────────────────────────────┐
  │              ALWAYS CHALLENGED (Tier 1)                 │
  │                                                         │
  │  "safe" · "effective" · "safe and effective"            │
  │  "safe and well tolerated" · "proven"                   │
  │  "established safety" · "proven efficacy"               │
  │  "favorable safety profile" · "acceptable safety        │
  │   profile" · "demonstrated efficacy"                    │
  │                                                         │
  │  → Must be REMOVED regardless of context, hedging,      │
  │    or data support.                                     │
  ├─────────────────────────────────────────────────────────┤
  │           PERMITTED IF SUPPORTED (Tier 2)               │
  │                                                         │
  │  "well-tolerated"                                       │
  │    → PERMITTED if true AND supported by:                │
  │      • Specific AE rates / incidence data               │
  │      • SAE count and description                        │
  │      • Explanation of basis (per Madrigal part (c))     │
  │    → CHALLENGED if standalone assertion without data     │
  │    → CHALLENGED if "demonstrated that [drug] was well   │
  │      tolerated" (OS Therapies — conclusion framing)     │
  │                                                         │
  │  "no SAEs reported" / "no treatment-related SAEs"       │
  │    → PERMITTED if true (per Altamira)                   │
  │                                                         │
  │  "the trial met its primary endpoint of [X]"            │
  │    → PERMITTED (objective data, no efficacy conclusion) │
  │                                                         │
  │  "X% of patients achieved [endpoint]"                   │
  │    → PERMITTED (objective data presentation)            │
  ├─────────────────────────────────────────────────────────┤
  │           CONTEXT-DEPENDENT (Tier 3)                    │
  │                                                         │
  │  "promising" · "encouraging" · "positive results"       │
  │    → Preclinical context: CHALLENGED (Curanex, Check 3) │
  │    → Clinical context with data: BORDERLINE             │
  │    → With specific endpoint data: usually permitted     │
  └─────────────────────────────────────────────────────────┘

  THE MADRIGAL THREE-PART TEST (for "well-tolerated"):
  1. Is it TRUE? (Were AEs actually mild/moderate in majority?)
  2. Are SAEs DISCLOSED alongside? (No cherry-picking)
  3. If SAEs occurred, is the BASIS EXPLAINED?
  All three must be satisfied. Failure on any = challenged.

  THE OS THERAPIES CONCLUSION TEST:
  - "Data showed X" (presenting data) → OK
  - "Data demonstrated that drug was well tolerated" (drawing
    conclusion) → CHALLENGED
  The difference: "showed" presents; "demonstrated that... was
  well tolerated" concludes.


───────────────────────────────────────────────────────────────
HOW THIS CHECK WAS PROCESSED:
───────────────────────────────────────────────────────────────

  Script: s1_parser.py → _scan_red_flags()

  STEP A — PHRASE SCAN:
  Scans against reference/red_flag_phrases.txt — a curated list
  derived from every SEC comment letter in the authority set:

  TIER 1 PHRASES:
    "safe and effective", "safe and well tolerated",
    "proven safety", "proven efficacy", "established safety",
    "established efficacy", "favorable safety profile",
    "acceptable safety profile", "demonstrated efficacy"

  TIER 2 PHRASES:
    "well-tolerated", "well tolerated", "no SAEs",
    "demonstrated clinical activity"

  TIER 3 PHRASES:
    "promising", "encouraging", "positive results"

  STANDALONE "safe" and "effective" scanned separately with
  context filters to exclude:
    - "safe harbor" (legal term)
    - "safety" as a noun (describing the concept, not the drug)
    - "cost-effective", "effective date" (non-drug uses)
    - "effective" describing competitor drugs or market

  STEP B — CONTEXT CLASSIFICATION:
  Each hit classified into one of three categories:

  (1) CAUTIONARY: Appears in Risk Factors section OR uses
      conditional/negative framing ("may not be safe",
      "there is no guarantee of efficacy", "even if well
      tolerated"). → AUTO GREEN — these are appropriate
      cautionary disclosures.

  (2) SUPPORTED: Appears within 500 chars of quantitative
      clinical data (AE percentages, SAE counts, endpoint
      results, p-values). → AUTO GREEN for Tier 2 phrases.
      Still flagged for Tier 1 phrases (data doesn't cure
      "safe and effective").

  (3) STANDALONE: Affirmative use without nearby data or
      cautionary context. → FLAGGED for escalation.

  STEP C — PATTERN DETECTION:
  If any single phrase has >5 STANDALONE instances → PATTERN
  flag. This matches the Altamira concern about language
  appearing in "numerous places throughout."

  STEP D — SPECIAL HANDLING:
  - "well-tolerated" STANDALONE: Check Madrigal three-part
    test — are SAEs disclosed ANYWHERE in the S-1? If yes,
    are they disclosed near the "well-tolerated" claim?
  - "safe": Distinguish affirmative ("ARD-101 is safe") from
    contextual ("safety data", "safety profile of the class")
  - "effective": Distinguish drug-specific ("ARD-101 is
    effective") from market-descriptive ("effective treatments
    exist for obesity")


───────────────────────────────────────────────────────────────
S-1 TEXT FOUND [FOR THE S-1 UNDER REVIEW]:
───────────────────────────────────────────────────────────────

  "WELL-TOLERATED" — 16 instances total:

    7 CAUTIONARY (Risk Factors or conditional language):
      [PLACEHOLDER — list each instance with section/page and
      the conditional framing that makes it cautionary.
      E.g., "Even if ARD-101 is well-tolerated, we may not..."
      in Risk Factors.]
      → AUTO GREEN (appropriate cautionary use)

    0 SUPPORTED (with nearby AE data):
      [None of the affirmative uses had quantitative AE data
      within 500 chars.]

    9 STANDALONE (affirmative without supporting data):
      [PLACEHOLDER — list each of the 9 instances with:
      - Exact quote (full sentence minimum)
      - Section name
      - Page number
      - What appears nearby (or doesn't)

      E.g.:
      INSTANCE 1 (PROSPECTUS SUMMARY, p. ~3):
      "ARD-101 has been generally well tolerated in clinical
      trials to date."
      NEARBY CONTEXT: No AE rates, no SAE counts, no endpoint
      data within 500 chars.

      INSTANCE 2 (BUSINESS, p. ~45):
      "Treatment with ARD-101 was well tolerated with..."
      NEARBY CONTEXT: [describe]

      ... through INSTANCE 9]

      → ALL 9 FLAGGED for escalation

  "SAFE" — 2 affirmative uses (excluding "safe harbor",
  "safety" as noun):

    [PLACEHOLDER — exact quotes with section/page.

    E.g.:
    INSTANCE 1 (BUSINESS, p. ~50):
    "[exact quote using 'safe' to describe drug]"

    INSTANCE 2 (PROSPECTUS SUMMARY, p. ~5):
    "[exact quote]"]

    → BOTH FLAGGED for escalation (Tier 1 — always challenged)

  "EFFECTIVE" — 105 total uses:
    [PLACEHOLDER — contextual analysis breakdown:
    - N instances describing the market/competitors → excluded
    - N instances in legal boilerplate ("effective date") →
      excluded
    - N instances describing the company's own drug → FLAGGED
    List the drug-specific instances with section/page.]

  PATTERN FLAG: 9 STANDALONE "well-tolerated" instances > 5
  threshold → matches Altamira "numerous places throughout"
  pattern.


───────────────────────────────────────────────────────────────
ESCALATION TRIGGERED: YES
───────────────────────────────────────────────────────────────

  Reasons:
  1. 9 STANDALONE "well-tolerated" instances without supporting
     AE/SAE data (Altamira + Madrigal + OS Therapies pattern)
  2. 2 affirmative "safe" uses (Tier 1 — always challenged)
  3. Pattern flag: "well-tolerated" in "numerous places
     throughout" (Altamira exact language)


<!-- ANCHOR: ESCALATION_PROMPT_CHECK7 -->
═══════════════════════════════════════════════════════════════
ESCALATION PROMPT DESIGN — CHECK 7
═══════════════════════════════════════════════════════════════

This is the MOST COMPLEX escalation prompt because it involves
the most comparison pairs (5), the most granular analysis (each
instance analyzed separately), and the most specific SEC
guidance (the Altamira permitted/challenged framework + the
Madrigal three-part test).

───────────────────────────────────────────────────────────────
STEP 1: INSTANCE-BY-INSTANCE ANALYSIS
───────────────────────────────────────────────────────────────

SYSTEM CONTEXT:
  You are reviewing an S-1 registration statement for compliance
  with SEC standards on safety and efficacy language. The SEC
  has consistently held that "safety and efficacy determinations
  are solely within the authority of the FDA." You will analyze
  each flagged instance against a detailed framework derived
  from five SEC comment letters.

SLOT 1 — ALL FLAGGED S-1 PASSAGES:
  [Each of the 9 standalone "well-tolerated" instances +
  2 "safe" instances + any flagged "effective" instances.
  For each: exact quote, section, page, nearby context.]

SLOT 2 — THE SEC FRAMEWORK (derived from all 5 comment letters):

  ANCHOR — ALTAMIRA (the comprehensive framework):
  "Please remove all statements throughout your registration
  statement that state or imply your conclusions regarding the
  safety or efficacy of your product candidates and technologies,
  as these determinations are solely within the authority of the
  FDA and comparable regulatory bodies. With respect to safety,
  we will not object to statements that your product candidates
  are well-tolerated, if true, or that no serious adverse events
  deemed to be study related were reported. You may also present
  a balanced summary of objective pre-clinical and clinical data,
  including whether clinical trials met primary and secondary
  endpoints, without including your conclusions related to
  efficacy."

  GRAYBUG ("favorable safety and tolerability"):
  "Please revise your disclosure here and throughout your
  prospectus to remove your characterization of GB-102 as safe."

  MADRIGAL (three-part test):
  "(a) In future filings, please refrain from making such
  assessments related to product candidates that have not been
  approved. (b) Please disclose all serious adverse events...
  and disclose the number of such events. (c) Explain how you
  have determined that the candidate is well tolerated when trial
  participants experienced serious adverse events."

  SCOPUS ("acceptable safety profile"):
  "Safety is a determination that is solely within the authority
  of the FDA."

  OS THERAPIES (conclusion framing):
  "investors should be able to assess how the drug candidate
  performed relative to the established endpoints... and also
  assess your conclusion that 'the data presented from the
  Phase Ib trial demonstrated that ADXS31-164 was well
  tolerated.'"

  [CHALLENGED S-1 TEXT for each — inserted from PLACEHOLDER
  slots when fetched]

SLOT 3 — STRUCTURED ANALYSIS QUESTIONS:

  For EACH flagged instance, answer ALL of the following:

  (a) PHRASE TIER: Is this a Tier 1 (always challenged), Tier 2
      (challenged unless supported), or Tier 3 (context-
      dependent) phrase?

  (b) CONTEXT: What section does it appear in? Is the framing:
      - Affirmative ("ARD-101 is well tolerated") → HIGHER RISK
      - Conditional ("if well tolerated") → LOWER RISK
      - Cautionary ("even if well tolerated, risks remain") →
        LOWEST RISK

  (c) DATA SUPPORT (Tier 2 only): Within 500 chars, does the
      S-1 provide:
      - AE incidence rates? (Yes/No + quote)
      - SAE counts? (Yes/No + quote)
      - Specific endpoint results? (Yes/No + quote)
      If Yes to all → PASSES Madrigal three-part test.
      If No to any → FAILS Madrigal three-part test.

  (d) CONCLUSION vs. DATA PRESENTATION (OS Therapies test):
      Does the passage:
      - Present data and let investors conclude? → PERMITTED
        ("AEs occurred in X% of patients; no SAEs reported")
      - Draw a conclusion from the data? → CHALLENGED
        ("data demonstrated that drug was well tolerated")

  (e) CLOSEST COMPARISON PAIR: Which comment letter is most
      analogous?
      - Altamira (phrases "throughout" the document)
      - Graybug ("favorable safety")
      - Madrigal ("safe and well tolerated" + SAE issue)
      - Scopus ("acceptable safety profile")
      - OS Therapies (conclusion framing of "well tolerated")

  (f) INDIVIDUAL RECOMMENDATION:
      - GREEN: Cautionary use, or fully supported per Madrigal
        three-part test
      - YELLOW: Supported but incomplete (e.g., AE rates
        provided but SAEs not disclosed nearby)
      - RED: Tier 1 phrase, or unsupported Tier 2 phrase, or
        conclusion framing without data

REQUIRED OUTPUT FORMAT (Step 1):

  {
    "instances_analyzed": [
      {
        "instance_id": 1,
        "phrase": "well-tolerated",
        "exact_quote": "[full sentence]",
        "section": "[section name]",
        "page_approx": "[page]",
        "phrase_tier": 1 | 2 | 3,
        "context_type": "AFFIRMATIVE" | "CONDITIONAL"
          | "CAUTIONARY",
        "data_support": {
          "ae_rates_nearby": true | false,
          "sae_counts_nearby": true | false,
          "endpoint_data_nearby": true | false,
          "madrigal_test_passed": true | false
        },
        "conclusion_vs_data": "CONCLUSION" | "DATA_PRESENTATION",
        "closest_comparison_pair": "ALTAMIRA" | "GRAYBUG"
          | "MADRIGAL" | "SCOPUS" | "OS_THERAPIES",
        "individual_recommendation": "GREEN" | "YELLOW" | "RED",
        "reasoning": "[2-3 sentences]"
      }
    ],
    "summary": {
      "total_flagged": 0,
      "tier1_count": 0,
      "tier2_unsupported_count": 0,
      "tier2_supported_count": 0,
      "red_count": 0,
      "yellow_count": 0,
      "green_count": 0,
      "pattern_flag": true | false,
      "pattern_description": "[if flagged: 'N instances of
        [phrase] throughout document matches Altamira pattern']"
    },
    "step1_assessment": "CLEAR" | "CONCERN" | "SIGNIFICANT_CONCERN"
  }


───────────────────────────────────────────────────────────────
STEP 2: MADRIGAL THREE-PART TEST (global)
───────────────────────────────────────────────────────────────

  This step runs a GLOBAL check across the entire S-1, not
  per-instance:

  (a) Does the S-1 disclose ALL SAEs for each clinical program?
      Search entire S-1 for SAE disclosures. If "well-tolerated"
      appears but SAEs are not disclosed → MADRIGAL PART (b)
      FAILURE.

  (b) If SAEs occurred AND the S-1 claims "well tolerated,"
      does the S-1 explain the basis? Per Madrigal part (c),
      the company must explain how it reconciles SAEs with the
      "well tolerated" characterization.

  (c) Are SAEs disclosed NEAR the "well-tolerated" claims, or
      only in a separate section? If "well tolerated" in
      Business section but SAEs only in Risk Factors → segregated
      disclosure (analogous to Check 5 FDA communication balance).

  OUTPUT:
  {
    "sae_disclosure": {
      "saes_disclosed_anywhere": true | false,
      "sae_count": "[N SAEs disclosed]" | "not disclosed",
      "sae_section": "[where SAEs are disclosed]",
      "saes_near_well_tolerated_claims": true | false,
      "madrigal_part_b_satisfied": true | false,
      "madrigal_part_c_satisfied": true | false
    },
    "global_madrigal_result": "PASS" | "PARTIAL" | "FAIL"
  }


───────────────────────────────────────────────────────────────
STEP 3: WEB SEARCH AUGMENTATION
───────────────────────────────────────────────────────────────

  SEARCH QUERIES:
  1. "SEC comment letter well-tolerated biotech 2024 2025"
  2. "SEC comment letter safe effective S-1 2024 2025"
  3. "SEC comment letter favorable safety profile 2024"

  PURPOSE: Check for:
  - Recent comment letters that clarify the "well-tolerated"
    standard (any letters accepting it with data support?)
  - Any hardening or softening of the SEC's position since
    Madrigal (Nov 2023)
  - Whether the pattern of challenging "well-tolerated" has
    continued into 2024-2025

  OUTPUT: Same format as Check 2 Step 2.


───────────────────────────────────────────────────────────────
STEP 4: FINAL STATUS DETERMINATION
───────────────────────────────────────────────────────────────

  DECISION TREE:

  IF step1_assessment = "CLEAR":
    → 🟢 GREEN

  IF step1_assessment = "CONCERN":
    IF tier1_count = 0 AND tier2_unsupported_count <= 3
       AND global_madrigal_result = "PASS":
      → 🟡 YELLOW
      → Narrative: "[N] 'well-tolerated' instances without
        optimal data support nearby. SAEs are disclosed
        [elsewhere/nearby]. Madrigal three-part test [partially/
        fully] satisfied. Less severe than Altamira pattern but
        warrants attorney review of data support proximity."

    IF tier1_count = 0 AND tier2_unsupported_count > 3:
      → 🟡 YELLOW (trending RED)
      → Narrative: "[N] unsupported 'well-tolerated' instances
        approaching Altamira 'numerous places throughout' pattern.
        Recommend revising to include AE data near each claim."

  IF step1_assessment = "SIGNIFICANT_CONCERN":
    IF tier1_count > 0:
      → 🔴 RED
      → Narrative: "[N] Tier 1 phrases ('safe', 'effective',
        'favorable safety profile') that the SEC has consistently
        required to be removed. Additionally, [N] unsupported
        'well-tolerated' instances match Altamira pattern.
        Revision required per Altamira, Graybug, Madrigal,
        Scopus precedent."

    IF tier1_count = 0 AND pattern_flag = true
       AND global_madrigal_result = "FAIL":
      → 🔴 RED
      → Narrative: "[N] standalone 'well-tolerated' instances
        throughout the document without supporting AE/SAE data.
        Matches Altamira 'numerous places throughout' pattern.
        Madrigal three-part test failed — SAEs not disclosed
        near claims. Revision required."

    IF tier1_count = 0 AND pattern_flag = true
       AND global_madrigal_result = "PARTIAL":
      → 🟡 YELLOW (borderline RED)
      → Narrative: "Pattern of unsupported 'well-tolerated'
        claims matches Altamira, but SAEs are disclosed elsewhere
        in the S-1. Recommend relocating SAE data near each
        'well-tolerated' claim to satisfy Madrigal three-part
        test."

  OUTPUT: Same JSON format as Check 2 Step 3.


───────────────────────────────────────────────────────────────
FOR THE CURRENT S-1 (AARD): ESCALATION RESULT
───────────────────────────────────────────────────────────────

  Flagged instances:
  - 9 STANDALONE "well-tolerated" (Tier 2, unsupported)
  - 2 affirmative "safe" (Tier 1)

  Madrigal three-part test: [PLACEHOLDER — need to verify
  whether AARD S-1 discloses SAEs, their count, and explains
  the basis for "well-tolerated" characterization]

  Pattern flag: YES — 9 standalone instances > 5 threshold.
  Matches Altamira "numerous places throughout."

  Step 1 assessment: SIGNIFICANT_CONCERN
  - tier1_count = 2 (affirmative "safe")
  - tier2_unsupported_count = 9
  - pattern_flag = true

  Status After Escalation: 🔴 RED

  Key Finding: 9 standalone "well-tolerated" uses without
  supporting AE/SAE data matches the Altamira pattern ("numerous
  places throughout the registration statement"). 2 affirmative
  "safe" uses directly conflict with the SEC's bright-line
  standard. Madrigal three-part test [satisfied/failed]. Raises
  questions under Rule 408 and SEC comment letter precedent.
  Warrants attorney review; revision likely required.


═══════════════════════════════════════════════════════════════
PLACEHOLDER TRACKER — S-1 TEXT STILL NEEDED (CHECKS 6-7)
═══════════════════════════════════════════════════════════════

CHECK 6:
  □ Taysha S-1: Pipeline table/graphic description showing
    "Phase 1/2", "Pivotal", "IND-enabling" columns
    SOURCE: https://www.sec.gov/Archives/edgar/data/1806310/
    000119312520247565/d938924ds1a.htm

  □ AARD S-1: Pipeline graphic description (image-embedded)

CHECK 7:
  □ Altamira F-1: Full paragraphs from pages 1, 11, 55-57, 79,
    84, 88, 89 containing "safe and effective", "safe and well
    tolerated", "favorable safety profile"
    SOURCE: [need Altamira EDGAR URL for F-1]

  □ Graybug S-1: Full paragraph from page 21 containing
    "favorable safety and tolerability"
    SOURCE: [need Graybug EDGAR URL]

  □ Madrigal 10-K: Full paragraph from page 10 containing
    "safe and well tolerated" re: Resmetirom
    SOURCE: [need Madrigal EDGAR URL for 2022 10-K]

  □ Scopus Form 1-A: Full paragraph containing "acceptable
    safety profile" re: MRI-1867
    SOURCE: [need Scopus EDGAR URL]

  □ OS Therapies S-1: Full paragraph containing "demonstrated
    that ADXS31-164 was well tolerated"
    SOURCE: [need OS Therapies EDGAR URL]

  □ AARD S-1: All 9 standalone "well-tolerated" instances +
    2 "safe" instances with exact quotes, sections, pages
