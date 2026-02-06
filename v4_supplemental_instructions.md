# SUPPLEMENTAL INSTRUCTIONS FOR CLAUDE CODE
# Everything from v3 spec that must be carried into v4

Read this AFTER reading s1_checker_skill_spec_v4_instructions.md.
These are additional requirements that v4 instructions did not 
repeat but that MUST be implemented. Think of v4 as the architecture 
and this file as the UX/presentation/completeness layer.

---

## 1. USER-FACING OPENING EXPLANATION

v4 focuses on the decision tree architecture but doesn't specify 
what the USER sees when the tool starts. This is critical — the 
user needs to understand the entire process before anything runs.

**When the skill is triggered, BEFORE any code executes, present:**

### Section A: What This Tool Is

"This tool was built by **Jesus Alcocer** for **Norm.ai** assessment 
purposes. It checks whether a biotech company's S-1 registration 
statement adequately discloses clinical trial information by comparing 
the S-1 text to the public record on ClinicalTrials.gov."

### Section B: What is a "Skill"?

"A skill is a structured prompt that orchestrates code and LLM 
analysis together. Think of it as a playbook: at each step, the 
tool either (a) runs a Python script for mechanical work (download 
a filing, count phrases, extract data) or (b) uses LLM reasoning 
for analytical judgment (is this characterization balanced? does 
this pattern match a precedent?).

**The critical design principle: you always know which is which.** 
Code outputs are independently verifiable. LLM reasoning is shown 
with its inputs so you can evaluate it against the standard cited."

### Section C: Visual Process Flow

Present as an HTML/React artifact if possible, otherwise ASCII:

```
USER ENTERS TICKER
    ↓
[CODE] Download S-1 from EDGAR → User confirms filing
    ↓
[CODE] Parse S-1, identify drug candidates → User selects candidate
    ↓
[CODE + LLM] Pass 1: 7 cross-cutting S-1 checks (S-1 text only)
    ↓
[CODE] Download trial data from ClinicalTrials.gov
    ↓
[CODE + LLM] Pass 2: 4 trial-level comparison checks (S-1 vs CTgov)
    ↓
[LLM] Guardrail sweep: overall pattern assessment (only if issues found)
    ↓
Final report with all findings, sources, and reasoning
```

Color-code: blue for CODE steps, orange for LLM steps, purple for both.

### Section D: Legal Framework Summary

Present the three-layer legal framework as a visual hierarchy:

**Layer 1: Baseline Rules**
- Securities Act § 11 (15 U.S.C. § 77k) — strict liability for S-1 signers
- Rule 408 (17 C.F.R. § 230.408) — must disclose whatever makes other statements not misleading
- Rule 10b-5 (17 C.F.R. § 240.10b-5) — anti-fraud

**Layer 2: Supreme Court Standards** (escalation checks — only triggered when Layer 1 finds issues)
- Omnicare v. Laborers, 575 U.S. 175 (2015) — opinion statement liability
- Matrixx v. Siracusano, 563 U.S. 27 (2011) — no statistical significance threshold for materiality
- TSC Industries v. Northway, 426 U.S. 438 (1976) — materiality definition

**Layer 3: Enforcement Precedents** (what actually happened to companies)
- SEC v. Clovis Oncology — non-standard metrics, $20M penalty
- United States v. Harkonen — endpoint promotion, criminal conviction
- SEC v. AVEO — selective FDA disclosure, fraud charges
- Tongue v. Sanofi — FDA feedback disclosure duty

**How the SEC enforces**: Through comment letters (written feedback 
during S-1 review), not a single industry guide.

### Section E: Complete Checklist Preview

Present this table so the user knows everything that will be checked:

| # | Check | What We're Looking For | How | Source |
|---|-------|----------------------|-----|--------|
| 1 | Basic Disclosure | Drug identity, indication, stage, no-products statement | Code extracts → LLM assesses completeness | SEC comment letters |
| 2 | Phase Labels | Combined phase labels explained | Code regex → LLM context check | SEC comment letters |
| 3 | Preclinical Framing | Animal data labeled; MoA as hypothesis not fact | Code grep → LLM assessment | SEC comment letters |
| 4 | Comparative Claims | Comparisons supported by head-to-head data | Code scan → LLM comparison | SEC comment letters |
| 5 | FDA Communications | Balanced disclosure of interactions | Code scan → LLM symmetry check | AVEO, Tongue v. Sanofi |
| 6 | Pipeline Accuracy | Pipeline graphic matches text | Code compare (if HTML) / manual note (if image) | SEC comment letters |
| 7 | Red Flag Phrases | Safety/efficacy language qualified or supported | Code count + classify → LLM for standalone instances | SEC comment letters |
| — | *— S-1 checks complete. Now comparing to ClinicalTrials.gov —* | | |
| 8 | Trial Design | S-1 design elements match registry | Code builds comparison table | SEC comment letters |
| 9 | Endpoints & Statistics | Results accurate; endpoint hierarchy clear; pre-specified vs post-hoc | Code extracts → LLM precedent comparison | Harkonen, Clovis, SEC letters |
| 10 | Safety Data | Safety claims match AE data | Code builds comparison table → LLM assessment | SEC comment letters |
| 11 | Data Maturity | Preliminary data labeled; no conclusory language for unfinished data | Code status check → LLM language assessment | Rigel, SEC letters |
| — | *— Individual checks complete. Escalation layer (only if issues found) —* | | |
| 12 | Rule 408 Pattern | Are omissions systematically one-sided? | Code tabulates direction → LLM pattern assessment | 17 C.F.R. § 230.408 |
| 13 | Omnicare Test | Do opinion statements omit known contrary facts? | LLM three-part test with precedent language | 575 U.S. 175 (2015) |
| 14 | Matrixx Check | Could findings be dismissed on significance grounds? | LLM defense-blocker note | 563 U.S. 27 (2011) |

### Section F: Testing Note

"**Note**: To conserve resources, this version analyzes one drug 
candidate at a time. The architecture supports running all candidates 
automatically."

### Section G: Enter a Ticker

"Enter any pharma/biotech ticker to begin."

---

## 2. MISSING OPERATIONALIZED CHECKS

v4 instructions operationalize Checks 1-5, 7-10 but OMIT two checks. 
Add these:

### CHECK 6: PIPELINE ACCURACY

```python
def check_pipeline_accuracy(s1_full_html, candidate_passages):
    """
    STEP 1 (CODE): Detect pipeline format.
    Search HTML for <table> elements near "pipeline" keyword.
    → HTML_TABLE (can parse) or IMAGE (cannot parse)
    
    IF IMAGE:
        Output: "Pipeline is embedded as an image and cannot be 
        verified programmatically. Manual review recommended to 
        confirm pipeline graphic does not overstate development 
        progress or use misleading phase bars."
        Mark: 🟡 YELLOW (cannot verify)
        → Done.
    
    IF HTML_TABLE:
    STEP 2 (CODE): Extract phase claims per candidate from table.
    Compare to phase claims in text passages.
    For each candidate:
        table_phases vs text_phases → MATCH or MISMATCH
    
    STEP 3 (CODE): Check for overstated progress.
    IF table shows Phase 2 but text only describes Phase 1 data → RED
    IF table shows "IND-enabling" but no IND filed → YELLOW
    
    OUTPUT: Pipeline comparison table or image limitation note.
    """
```

### CHECK 11: DATA MATURITY (Interim/Topline)

```python
def check_data_maturity(s1_passages_for_trial, ctgov_json):
    """
    STEP 1 (CODE): Determine trial status from CTgov.
    status = protocolSection.statusModule.overallStatus
    → COMPLETED / ACTIVE_NOT_RECRUITING / RECRUITING / etc.
    
    results_posted = (resultsSection exists)
    
    STEP 2 (CODE): Check S-1 labeling.
    IF status != COMPLETED (trial is ongoing):
        Search S-1 passages for: "interim", "preliminary", 
        "topline", "initial", "data cutoff"
        → LABELED_PRELIMINARY or NOT_LABELED
    
    IF NOT_LABELED and trial is ongoing → YELLOW
    
    STEP 3 (CODE): Check for conclusory language on preliminary data.
    IF trial is ongoing OR results not posted OR S-1 says "preliminary":
        Search same passages for conclusory verbs:
        "demonstrated", "established", "proven", "confirmed", 
        "showed", "validated"
        → Found [n] conclusory terms for preliminary data
    
    STEP 4 (LLM CALL — if conclusory terms found):
    Prompt: "The S-1 presents data from [trial status: ongoing/
    preliminary/unpublished] and uses this language:
    '[exact passage]'
    
    The conclusory term '[verb]' is used for data that is 
    [interim/preliminary/unpublished/from an uncontrolled study].
    
    In In re Rigel Pharmaceuticals, 697 F.3d 869 (9th Cir. 2012), 
    the court held: '[exact holding on partial disclosure of 
    clinical trial results]'.
    
    The SEC has challenged conclusory language for preliminary data 
    in comment letters: '[exact comment letter text]'.
    
    Is the conclusory framing here appropriate given the data 
    maturity, or does it create an impression of finality that 
    the data does not support?"
    
    OUTPUT: Data maturity assessment with labeling check and 
    conclusory language analysis.
    """
```

---

## 3. OUTPUT TABLE FORMAT (EXACT SPECIFICATION)

v4 describes what checks DO but not what the USER SEES. Every check 
must produce output in this exact table format:

### Pass 1 output (per check element):

| Check | Status | Standard (with source) | S-1 Quote (section, page) | Reasoning |
|-------|--------|----------------------|--------------------------|-----------|

Example row:
| Basic Disclosure: Indication | 🟢 | S-1 must describe the disease, prevalence, and unmet need. [SEC comment letter to XYZ Co., URL] | "Prader-Willi Syndrome (PWS) is a rare genetic disorder affecting approximately 1 in 15,000 births..." (Prospectus Summary, p. 3) | Clear description with prevalence context. Satisfies the standard. |

### Pass 2 output (per trial):

**TABLE 1: Disclosure Inventory** — Everything the S-1 says about this trial

| # | S-1 Statement (exact quote) | Section | Page (approx) |
|---|---------------------------|---------|---------------|

**TABLE 2: Design Comparison** — Code-generated side-by-side

| Element | ClinicalTrials.gov | S-1 Says | Status |
|---------|--------------------|----------|--------|

**TABLE 3: Check Results** — Same format as Pass 1

| Check | Status | Standard | S-1 Quote | CTgov Data | Reasoning |
|-------|--------|----------|-----------|------------|-----------|

### Guardrail output:

**Rule 408 table:**
| # | Omission/Gap | Direction | Source Check |
|---|-------------|-----------|-------------|

**Omnicare table:**
| Statement | Impression Created | Known Contrary Facts | Risk Level |
|-----------|-------------------|---------------------|------------|

---

## 4. INTERACTION BEHAVIOR RULES

### Rule: No flags during candidate identification

When presenting drug candidates found in the S-1 (Phase 2 output), 
show ONLY factual information:
- Candidate name
- Passage count
- Indication(s)
- Phase(s)

Do NOT mention "well-tolerated" counts, FDA interactions, NCT number 
absence, or any analytical observations. Those belong in the checks.

### Rule: Auto-flow with pause on findings

- 🟢 GREEN results: Show the table row, do NOT pause, move to next check
- 🟡 YELLOW results: Pause and present:
  ```
  ⚠️ I found an area for attention on [check name].
  [1-2 sentence summary]
  The relevant authority is [citation with URL].
  Would you like more detail, or shall I continue?
  ```
- 🔴 RED results: Pause, do research augmentation, and present:
  ```
  🔴 I found a significant concern on [check name].
  [1-2 sentence summary]
  [Research augmentation output — see below]
  Would you like to discuss this finding, or shall I continue?
  ```

### Rule: Transition summaries between passes

After Pass 1 completes, show:
```
Pass 1 Complete: Cross-cutting S-1 checks done.
🟢 [n] adequate  🟡 [n] attention areas  🔴 [n] significant concerns

Now moving to trial-level comparison...
```

After downloading CTgov data, show the trial table:
| NCT ID | Title | Phase | Status | Results Available |
|--------|-------|-------|--------|-------------------|

---

## 5. RESEARCH AUGMENTATION OUTPUT FORMAT

When a 🔴 RED finding triggers research augmentation (per v4 
architecture), present the expanded finding in this EXACT format:

```
🔴 FINDING: [concise description]

LEGAL STANDARD:
[Full text of the relevant standard — pulled from reference files]

COMPARABLE PRECEDENT:
In [case/letter], the SEC/court addressed similar language.
The [S-1/press release/filing] stated: "[EXACT quote from the 
problematic disclosure in the precedent case]"
The [SEC/court] found: "[EXACT holding/comment]"
The company was required to: [what they had to do/penalty imposed]

THIS S-1:
"[EXACT quote from the S-1 being analyzed]"
(Section: [section name], Page: [approx page number])

TEXT-TO-TEXT COMPARISON:
[How the S-1's language is similar to or different from the 
precedent language — specific textual parallels identified]

RISK LEVEL: 🔴 — [Why this pattern closely matches the precedent]
```

---

## 6. CALIBRATION RULES (MANDATORY)

These MUST be followed in all output. Build them into the SKILL.md 
and every LLM prompt template:

### Rule 1: Risk areas, not legal conclusions
- SAY: "This language raises questions under [authority]"
- NOT: "This fails [test]" or "This violates [standard]"

### Rule 2: No liability determinations
- SAY: "This pattern warrants attorney review under Rule 408"
- NOT: "This is materially deficient" or "§ 11 exposure is HIGH"
- The v2 run said "MATERIALLY DEFICIENT" and "§ 11 EXPOSURE: HIGH." 
  These are LEGAL CONCLUSIONS. Never again.

### Rule 3: Severity = flag strength, not legal outcome
- 🔴 Red = Strong flag: clear gap, authority directly on point, 
  pattern closely matches enforcement precedent. Attorney should review.
- 🟡 Yellow = Moderate flag: gap or concern exists, but context may 
  justify. Attorney should be aware.
- 🟢 Green = Adequate: meets the standard.

### Rule 4: Acknowledge limitations
Every report must include:
- "This tool compares S-1 text to ClinicalTrials.gov only. It does 
  not review published papers, FDA correspondence, or internal data."
- "ClinicalTrials.gov data reflects what the sponsor posted — it 
  could itself be incomplete."
- "This tool identifies risk areas for attorney review. It does not 
  determine liability or materiality in the full legal sense."

### Rule 5: When in doubt, flag for review
If uncertain whether something is a real issue or acceptable practice, 
present as 🟡 YELLOW with explanation of both possibilities. Never 
conclude RED unless the factual pattern clearly matches a precedent.

---

## 7. s1_parser.py ENHANCEMENTS (from v3)

The parser MUST include these features that v4 didn't specify:

### Page number approximation
S-1 HTML has no real pages. Approximate by: 
character_position / 3000 = approximate_page_number

Every extracted passage must output:
- section_name (e.g., "Business", "Risk Factors")
- subsection_name (if identifiable from HTML headings)
- approximate_page_number
- character_position (for reproducibility)

### Section mapping
The parser must identify which standard S-1 section each passage 
belongs to. Standard S-1 sections:
- Prospectus Summary
- Risk Factors
- Use of Proceeds
- Business (including subsections: Overview, Clinical Programs, etc.)
- Management's Discussion and Analysis
- Financial Statements

**Why this is critical**: The asymmetric placement analysis depends 
on knowing WHERE in the S-1 each statement appears. If positive claims 
are in the Prospectus Summary and Business sections while negative 
disclosures are only in Risk Factors, that asymmetry is itself a 
finding (Check 5: FDA Communications, and Layer 2: Rule 408 Pattern).

### Candidate disambiguation
When identifying candidates, distinguish company drugs from competitor 
drugs by proximity to ownership language:
- "our" / "we" / "our lead" / "our proprietary" within 200 chars → COMPANY DRUG
- "competitor" / "approved" / "[other company name]" → COMPETITOR DRUG
- Standalone mention without ownership context → AMBIGUOUS (flag for manual check)

---

## 8. FDAAA 801 RESULTS POSTING CHECK

v4 Check 10 (Safety) partially covers this but it needs to be 
EXPLICIT as its own sub-check because it affects multiple checks:

```python
def check_results_posting_compliance(ctgov_json):
    """
    Under FDAAA 801 (42 U.S.C. § 282(j)), sponsors must post 
    results to ClinicalTrials.gov within 12 months of the primary 
    completion date for applicable clinical trials.
    
    STEP 1 (CODE):
    status = protocolSection.statusModule.overallStatus
    primary_completion = protocolSection.statusModule.completionDateStruct.date
    results_posted = (resultsSection exists)
    
    IF status == "COMPLETED" and NOT results_posted:
        months_since_completion = calculate from primary_completion
        IF months_since_completion > 12:
            FLAG: "Results not posted [n] months after completion. 
            FDAAA 801 requires posting within 12 months. S-1 claims 
            about this trial cannot be independently verified."
            Mark: 🔴 RED
        ELSE:
            NOTE: "Trial completed [n] months ago. Results not yet 
            posted but within the 12-month window."
            Mark: 🟡 YELLOW
    
    This check is INFORMATIONAL — it affects the confidence level 
    of other checks. If results are not posted:
    - Check 9 (Endpoints): Can compare design but not results
    - Check 10 (Safety): Cannot verify safety claims
    - Check 11 (Data Maturity): S-1 data is the only source
    """
```

---

## 9. AGGREGATE REPORT (Phase 7) SPECIFICATION

v4 says "final report" but doesn't specify the structure. Use this:

The report should be a downloadable .docx (use the docx skill) 
containing:

### Report Structure:

1. **Executive Summary** (1 page)
   - Company, ticker, filing date, candidate analyzed
   - Total findings: [n] 🟢, [n] 🟡, [n] 🔴
   - Top 3 findings in order of significance
   - Limitations statement

2. **Legal Framework** (1-2 pages)
   - Brief description of applicable standards
   - List of authorities applied with citations

3. **Pass 1: S-1 Cross-Cutting Findings** (variable length)
   - Full table with all check results
   - Expanded analysis for each 🟡 and 🔴 finding
   - Exact S-1 quotes with section and page

4. **Pass 2: Trial-Level Findings** (variable length, per trial)
   - Disclosure inventory table
   - Design comparison table
   - Endpoint hierarchy analysis
   - Safety comparison table
   - Data maturity assessment
   - Expanded analysis for each 🟡 and 🔴 finding

5. **Guardrail Assessment** (1-2 pages)
   - Rule 408 pattern table with direction analysis
   - Omnicare opinion assessment table (only for flagged items)
   - Matrixx relevance note (if applicable)

6. **Appendix: Sources**
   - All URLs cited (EDGAR filings, comment letters, cases)
   - ClinicalTrials.gov NCT URLs
   - All S-1 passage locations (section, page, character position)

---

## 10. v2 → v4 BEHAVIOR CHANGE TABLE

Include this in the spec so Claude Code understands what CHANGED 
and why. These are known problems from the v2 live test on AARD:

| v2 Did (WRONG) | v4 Must Do (RIGHT) | Why |
|----------------|--------------------|----|
| Surfaced flags during candidate identification ("20 instances of well-tolerated") | Present ONLY factual table: candidate, passages, indication, phases | Flags belong in the checks, not in candidate ID. Premature flags bias the analysis. |
| Said "Module 2", "Module 3" etc. | Use descriptive names: "Basic Disclosure", "Phase Labels" etc. | Lawyers don't think in modules. Names should describe the check. |
| Concluded "MATERIALLY DEFICIENT" | Present findings; let attorney conclude | "Materially deficient" is a legal conclusion. The tool identifies risk areas. |
| Said findings "FAIL" Omnicare | Say findings "raise questions under" Omnicare | "Fails" implies legal determination. Tool flags risk areas. |
| Paraphrased S-1 language | Quote EXACT S-1 language with section and approximate page number | Attorneys need the actual text to assess. Paraphrasing loses nuance. |
| Cited authorities without actual language | Include actual holding/comment language from the authority | "SEC comment letter challenging X" is useless without the actual SEC words. |
| Did not research red findings further | On RED findings, do text-to-text comparison with precedent language | The comparison is the whole point — how similar is THIS language to the language that was punished? |
| Required "go ahead" between every phase | Auto-flow through green; pause on yellow/red to offer detail | Unnecessary friction. The attorney wants findings, not permission prompts. |
| Presented findings as running prose | Present as color-coded tables with standardized columns | Tables are scannable, auditable, and can be included in memos. Prose gets lost. |
| Auto-analyzed all 5 trials without asking | Ask user which trials to analyze (GATE 2 from v2 spec) | Attorney should choose which trials are material. Running all wastes tokens and may analyze immaterial trials. |
| Omnicare test concluded "FAIL" / "PASS" | Omnicare assessment rates "SIGNIFICANT RISK / MODERATE / LOW / NO CONCERN" | Binary pass/fail implies legal determination. Graduated scale shows flag strength. |
| Said "§ 11 EXPOSURE: HIGH" | Do not rate overall exposure. Present findings, let attorney assess. | Exposure rating is attorney work product, not a tool output. |

---

## 11. FILE SYNC REQUIREMENTS

After all building is complete, verify:

- [ ] SKILL.md references "v4" and matches the v4 architecture
- [ ] SKILL.md does NOT use the word "module" anywhere
- [ ] README.md accurately describes the current file structure
- [ ] README.md includes attribution (Jesus Alcocer, Norm.ai)
- [ ] README.md describes Layer 1 / Layer 2 architecture
- [ ] All reference JSON files use consistent ID schemes
- [ ] operationalized_checks.json references legal_framework.json 
      entries by ID
- [ ] comment_letter_excerpts.json entries are referenced by ID 
      in operationalized_checks.json
- [ ] No orphaned references to v2 or v3 concepts
- [ ] No references to "modules" in any file
- [ ] red_flag_phrases.txt exists and is referenced by Check 7
- [ ] All placeholder URLs (filename1.htm etc.) have been replaced 
      with actual verified URLs from research

---

## 12. COWORK RESEARCH GUIDE

There is also a file called cowork_research_guide.md in this repo. 
It contains detailed research instructions for building the reference 
JSON files. Claude Code should use it as a guide for the research 
tasks (finding comment letters, extracting case language, verifying 
URLs). The research guide and these v4 instructions are complementary:
- cowork_research_guide.md = WHERE to find the information
- This file + v4 instructions = HOW to structure and use it
