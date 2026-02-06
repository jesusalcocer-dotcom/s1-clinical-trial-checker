# SPECIFICATION v2: S-1 Clinical Trial Disclosure Checker Skill

## What Changed from v1

v1 had one analytical pass: extract studies → download CTgov → compare.
v2 has two passes and a guardrail layer, reflecting the actual structure
of SEC review:

- **PASS 1 (Program-Level)**: Analyzes the S-1's description of each 
  drug candidate WITHOUT needing external data. Checks whether the S-1 
  gives investors adequate context: identity card, phase nomenclature, 
  preclinical framing, comparative claims, FDA communications, pipeline 
  accuracy, red flag phrases.

- **PASS 2 (Trial-Level)**: For each material trial, downloads source 
  data from ClinicalTrials.gov and compares it to the S-1. Checks 
  design/endpoints/results completeness, statistical presentation, 
  safety data, interim/topline framing.

- **GUARDRAILS**: Applied to ALL findings from both passes. The 
  anti-misleading standard (Rule 408, Omnicare, Matrixx) that asks: 
  does the total picture mislead?

---

## Guiding Principles (unchanged from v1)

1. **TRACEABILITY**: Every finding → S-1 passage + authority citation
2. **PROGRESSIVE DISCLOSURE WITH GATES**: User confirms at checkpoints
3. **EXPLAIN THEN EXECUTE**: Each phase explains what/why before acting
4. **LEGAL RULES ARE REFERENCE, NOT TRAINING**: Claude reads the 
   framework files and applies coded rules; does not reason from 
   general knowledge

---

## Skill Directory Structure

```
s1-clinical-trial-checker/
├── SKILL.md                              # Orchestrator prompt
├── scripts/
│   ├── edgar_fetch.py                    # Ticker → S-1 download
│   ├── s1_parser.py                      # S-1 → structured extraction
│   ├── ctgov_fetch.py                    # NCT → ClinicalTrials.gov JSON
│   └── comparison_builder.py             # S-1 passages + CTgov → comparison
└── reference/
    ├── guardrails.md                     # Module 1: Anti-misleading rules
    ├── program_level_modules.md          # Modules 2,3,7,8,9,11,12
    ├── trial_level_modules.md            # Modules 4,5,6,10
    └── red_flag_phrases.txt              # Machine-readable phrase list
```

The reference/ directory replaces the single analysis_framework.md.
Three files instead of one — because each has a different role:
- guardrails.md is the LENS (applied to everything)
- program_level_modules.md is the PASS 1 rulebook
- trial_level_modules.md is the PASS 2 rulebook

---

## INTERACTION FLOW (what the user sees)

```
USER: "Check SLRN"

GATE 0 ──── Confirm filing
│  "Found ACELYRIN S-1/A filed 2023-04-28. Correct?"
│
GATE 1 ──── Confirm candidates
│  "I identified 3 drug candidates: izokibep, lonigutamab, 
│   SLRN-517. Which to analyze?"
│
PASS 1 ──── Program-level analysis (runs, no gate needed)
│  "Running program-level checks on [candidate]..."
│  Presents findings per candidate
│
GATE 2 ──── Confirm trials for Pass 2
│  "For [candidate], I found these trials with NCT numbers.
│   X of Y have results on ClinicalTrials.gov. 
│   Which to analyze in detail?"
│
PASS 2 ──── Trial-level analysis (runs, no gate needed)
│  "Running trial-level comparison for NCT________..."
│  Presents findings per trial
│
OUTPUT ──── Final report
   Combines Pass 1 + Pass 2 findings
   Applies guardrail sweep
   Presents aggregate assessment
```

---

## PHASE-BY-PHASE SPECIFICATION

### PHASE 1: ACQUIRE S-1

Run: `python scripts/edgar_fetch.py --ticker {TICKER} --action lookup`

**How this works (for Claude Code to implement):**

The EDGAR submissions API returns a JSON with all filings for a company.
The `form` array is sorted by date descending (most recent first).
The script searches for the first entry where `form` contains "S-1" or "F-1"
(catching S-1, S-1/A, F-1, F-1/A). That's the latest registration statement.

**Step-by-step EDGAR logic:**

1. **Ticker → CIK**: Fetch `https://www.sec.gov/files/company_tickers.json`
   Search for ticker match (case-insensitive). Extract CIK number.

2. **CIK → Filing history**: Fetch:
   `https://data.sec.gov/submissions/CIK{cik_padded_to_10_digits}.json`
   
   Example: CIK 2085187 → `https://data.sec.gov/submissions/CIK0002085187.json`
   
   This returns a JSON object. The filings are in `filings.recent` which 
   contains parallel arrays: `form[]`, `filingDate[]`, `accessionNumber[]`, 
   `primaryDocument[]`, etc. All arrays share the same index.

3. **Find the latest S-1 or F-1**: Iterate through the `form[]` array 
   (index 0 = most recent). Find the first entry that contains "S-1" or 
   "F-1" as a substring. This catches:
   - `S-1` (original registration statement, domestic)
   - `S-1/A` (amendment to S-1 — supersedes original)
   - `F-1` (original registration statement, foreign private issuer)
   - `F-1/A` (amendment to F-1)
   
   Capture the **index** of that match.

4. **Extract filing metadata** using that index:
   - `accessionNumber[index]` → e.g., `"0001628280-26-003358"`
   - `filingDate[index]` → e.g., `"2026-01-26"`
   - `form[index]` → e.g., `"S-1/A"`
   - `primaryDocument[index]` → e.g., `"bobsdiscountfurnitureincs-.htm"`

5. **Build the document URL**:
   - Strip dashes from accession number: `"0001628280-26-003358"` → `"000162828026003358"`
   - CIK without leading zeros for the URL path: `"2085187"`
   - URL pattern: `https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primaryDocument}`
   - Example: `https://www.sec.gov/Archives/edgar/data/2085187/000162828026003358/bobsdiscountfurnitureincs-.htm`

**EDGAR API requirements:**
- ALL requests to sec.gov/data.sec.gov MUST include a User-Agent header:
  `User-Agent: S1DisclosureChecker/1.0 (contact@example.com)`
- Rate limit: max 10 requests per second. Add 0.2s delay between requests.

**Present to user:**
```
I found the following company and filing:

Company: {name} (from the JSON root `name` field)
CIK: {cik}
Filing type: {form_type}
Filed: {filing_date}
Accession number: {accession_number}

{If form_type is S-1/A or F-1/A:}
This is an amended filing — it supersedes the original and is 
the version investors and the SEC rely on.

{If form_type is F-1 or F-1/A:}
This is an F-1 (foreign private issuer registration statement), 
which is the equivalent of an S-1 for non-US companies.

Is this the correct filing to analyze?
```

Wait for user confirmation, then download the HTML document.

**Error handling:**
- Ticker not found → "Ticker not found in EDGAR. Check spelling."
- No S-1/F-1 filings → "No S-1 or F-1 filings found. This company 
  may not have an IPO registration statement on file."
- HTTP 403/429 → "EDGAR rate limit hit. Waiting and retrying..."
- If `filings.recent` has no matches but `filings.files[]` exists, 
  there may be older filings in separate JSON files. Fetch those too.

### PHASE 2: IDENTIFY DRUG CANDIDATES

This is NEW. v1 went straight to finding studies. v2 first identifies
the drug candidates, because the program-level analysis is organized
per candidate, not per trial.

Run: `python scripts/s1_parser.py --action find_candidates --file {s1_path}`

The script should:

1. Search for the pipeline table/graphic section (look for "pipeline,"
   "product candidates," "our programs" near tables or lists)

2. Extract candidate names by looking for:
   - Proper nouns that appear near "candidate," "product candidate,"
     "investigational," "our lead," "our pipeline"
   - Drug names that appear in headers/bold text in the Business section
   - INN-style names (lowercase with -mab, -nib, -tide, -gene suffixes)
   - Internal designators (e.g., "SLRN-517", "JTX-2011", "INBRX-109")

3. For each candidate, extract ALL passages across the S-1:
   - Prospectus Summary mentions
   - Business section (the main narrative)
   - Risk Factors that name the candidate
   - MD&A references
   - Use of Proceeds allocation

4. For each candidate, also extract:
   - Any NCT numbers mentioned in connection with it
   - Any phase designations ("Phase 1", "Phase 2", etc.)
   - Any indication mentions
   - Any FDA interaction mentions ("IND," "Breakthrough," "Fast Track,"
     "pre-IND meeting," "End-of-Phase 2," "SPA," "CRL")

Output:
```json
{
  "candidates": [
    {
      "name": "izokibep",
      "also_known_as": ["SLRN-801"],
      "indications": ["hidradenitis suppurativa", "psoriatic arthritis", 
                       "uveitis"],
      "phase_claims": ["Phase 2b/3"],
      "nct_numbers": ["NCT05355805", "NCT05623345", "NCT05683496"],
      "fda_mentions": ["IND cleared"],
      "passages": [
        {"section": "Prospectus Summary", "page_approx": 3, 
         "text": "..."},
        {"section": "Business", "page_approx": 78, "text": "..."},
        ...
      ]
    },
    ...
  ],
  "pipeline_table_text": "raw text of pipeline table if found",
  "general_statements": [
    "passages that apply to the company overall, not one candidate"
  ]
}
```

Present to user:
```
I identified {n} drug candidates discussed in the S-1:

1. {name} — {indications}, described as {phase_claims}
   {n} clinical trials referenced (NCT numbers found: {list})
   
2. {name} — {indications}, described as {phase_claims}
   {n} clinical trials referenced
   
Which candidates would you like me to analyze?
(Enter numbers, or "all")
```

Wait for selection.

---

### PHASE 3: PASS 1 — PROGRAM-LEVEL ANALYSIS

**Before starting, read**: `reference/program_level_modules.md`

**Tell the user:**
```
PASS 1: PROGRAM-LEVEL ANALYSIS

I'm now going to analyze how the S-1 presents each selected drug 
candidate. This pass uses only the S-1 text — I don't need external 
data sources yet.

I'm checking seven things:

1. IDENTITY CARD — Does the S-1 give investors the baseline context 
   they need? (What the drug is, what it treats, where it is in 
   development, whether any products are approved.)

2. PHASE NOMENCLATURE — If the S-1 uses combined phase labels like 
   "Phase 1/2" or "Phase 2/3," does it explain what each phase 
   portion actually involves? The SEC flags this because combined 
   labels can imply faster progress than reality.

3. PRECLINICAL FRAMING — If the S-1 cites animal or lab data, does 
   it control for "translation risk" — the fact that preclinical 
   results often don't predict human outcomes?

4. COMPARATIVE CLAIMS — Does the S-1 claim the drug is "safer," 
   "more effective," "superior," or "differentiated" versus existing 
   treatments? If so, is there head-to-head clinical data supporting 
   the comparison, or is it cross-trial inference (which is unreliable)?

5. FDA COMMUNICATIONS — Does the S-1 characterize FDA interactions 
   in a balanced way, or does it cherry-pick "positive feedback" 
   while omitting concerns or recommendations?

6. PIPELINE ACCURACY — Does the pipeline table/graphic accurately 
   reflect development status, or does it overstate progress?

7. RED FLAG PHRASES — Does the S-1 use language the SEC routinely 
   challenges: "safe," "effective," "clinically validated," 
   "favorable safety profile," "positive FDA feedback"?

For each issue I find, I'll show you: what the S-1 says, what the 
rule requires, and the specific SEC authority.
```

Then, for each selected candidate, execute Modules 2–3, 7–9, 11–12:

#### Module 2: Identity Card Check

**What the script pre-flags**: s1_parser.py should have already 
tagged whether each of the following appears in the candidate's
passages: indication description, modality description, development 
stage, statement about no approved products / no revenue.

**What Claude checks** (reading program_level_modules.md):

For each candidate, verify presence of:

| Element | Look for | If absent |
|---------|----------|-----------|
| Indication + clinical context | Plain-English disease description | FLAG: Investors lack context for why this drug matters |
| Modality | Small molecule / mAb / gene therapy / etc. | FLAG: Investors don't know what the drug IS |
| Development stage | Phase clearly stated, not inflated | FLAG: Investors may assume more progress than exists |
| No approved products statement | "We have no approved products" or equivalent, if applicable | FLAG: SEC has specifically requested this (cite authority) |
| Chronological development history | Preclinical → Phase 1 → Phase 2 → Phase 3 narrative | FLAG if narrative jumps around or implies faster progression |

**Authority for each finding**: Cite the specific SEC comment letter 
URL from program_level_modules.md.

#### Module 3: Phase Nomenclature Trap

**What the script pre-flags**: s1_parser.py flags any instance of 
"Phase 1/2" or "Phase 2/3" or "Phase 2a/2b" or similar combined 
labels.

**What Claude checks**:

IF combined phase label found:
  → Does the S-1 explain what the Phase 1 portion does?
    (e.g., dose escalation, MTD/RP2D determination)
  → Does the S-1 explain what the Phase 2 portion does?
    (e.g., dose expansion, efficacy-oriented endpoints)
  → Is the distinction tied to protocol structure?
  → Does the pipeline graphic reflect phases distinctly?
  
IF any of these are missing: FLAG with the SEC comment letter 
authority that specifically addresses this.

**Template for what "good" looks like** (from the framework):
"We are conducting a Phase 1/2a trial. The Phase 1 portion is 
dose escalation designed to determine MTD/RP2D; the Phase 2a 
portion is a dose-expansion cohort designed to evaluate 
preliminary activity and additional safety/PK at the RP2D."

#### Module 7: Preclinical Framing

**What Claude checks** in candidate passages:

IF S-1 presents preclinical data (animal models, in vitro):
  → Is the species/model identified?
  → Are endpoints stated?
  → Is there a translation risk caveat?
    ("Preclinical results may not be predictive of human outcomes"
     or equivalent)
  → Are preclinical results presented as if they demonstrate 
    clinical efficacy? (This is the red line)

IF MoA is described:
  → Is it framed as hypothesis/design intent ("designed to," 
    "intended to") or as established fact?
  → If framed as fact, is there clinical evidence supporting it?

#### Module 8: Comparative Claims

**What the script pre-flags**: Scan candidate passages for:
- "safer" / "more effective" / "superior" / "better"
- "differentiated" / "best-in-class" / "first-in-class"
- "improved over" / "advantage over" / "compared favorably"
- Any drug name + comparison language within 200 chars

**What Claude checks** for each flagged instance:

  → Is there head-to-head clinical data cited?
  → Or is this cross-trial inference? (Different trials, 
    different populations, different endpoints)
  → Does the S-1 acknowledge the limitations of the comparison?

IF cross-trial comparison without acknowledgment: FLAG.
IF "safer" or "more effective" for unapproved candidate: FLAG 
(safety/efficacy determinations are FDA's authority).

#### Module 9: FDA Communications

**What the script pre-flags**: Scan for FDA-related language:
- "positive feedback" / "constructive feedback" / "alignment"
- "FDA agreed" / "FDA indicated" / "FDA acknowledged"
- "Breakthrough Therapy" / "Fast Track" / "Orphan Drug" / 
  "Priority Review" / "Accelerated Approval"
- "pre-IND" / "End-of-Phase 2" / "SPA" / "CRL"

**What Claude checks**:

IF "positive feedback" language found:
  → Does the S-1 balance it with any FDA concerns or 
    recommendations?
  → Does the language imply approval is assured or likely?
  → FLAG if one-sided. Cite AVEO enforcement action + 
    Tongue v. Sanofi.

IF FDA designation mentioned:
  → Does the S-1 clarify it does not guarantee approval?
  → Does the S-1 disclose material FDA communications in 
    connection with the designation?

#### Module 11: Pipeline QC

**What Claude checks**:

  → Does pipeline table show phases that match the text?
  → Are any candidates shown in phases where IND hasn't been filed?
  → Do arrows/bars overextend to imply progress not yet achieved?
  → Are platforms listed as product candidates?
  → Is table legible and internally consistent?

Note: This check is limited by what can be extracted from the 
HTML. Pipeline graphics embedded as images cannot be parsed by 
the script — Claude should note this limitation if the pipeline 
is an image rather than an HTML table.

#### Module 12: Red Flag Phrase Scan (per candidate)

**What the script does**: For each selected candidate's passages, 
scan against the phrase list in `reference/red_flag_phrases.txt`.

The phrase list:
```
safe
effective  
clinically validated
clinically proven
proven efficacy
proven safety
favorable clinical activity
promising tolerability
favorable safety profile
acceptable safety profile
well-tolerated [without quantitative support nearby]
safer than
more effective than
superior to
best-in-class
fast-to-market
accelerated commercialization
positive FDA feedback
FDA endorsement
```

**What Claude does** with each hit:

Don't auto-flag every instance. Check context:
  → Is "safe" used in a risk factor? (acceptable — describing risk)
  → Is "effective" preceded by "may not be"? (acceptable — cautionary)
  → Is "well-tolerated" followed by AE rates? (acceptable — supported)
  → Is "well-tolerated" standalone with no data? (FLAG)

Only FLAG instances where the phrase is used affirmatively about 
the candidate without adequate qualification or data support.

#### Pass 1 Output (per candidate)

```
PASS 1 FINDINGS: {candidate name}

Module 2 (Identity Card): {COMPLETE / GAPS FOUND}
  [list any gaps with S-1 quote and authority]

Module 3 (Phase Nomenclature): {OK / FLAG}
  [if flagged, show the combined label and what explanation 
   is missing]

Module 7 (Preclinical): {OK / FLAG}
  [if flagged, show claim and missing caveat]

Module 8 (Comparative Claims): {NONE / OK / FLAG}
  [if flagged, show claim and missing basis]

Module 9 (FDA Communications): {NONE / OK / FLAG}
  [if flagged, show one-sided characterization]

Module 11 (Pipeline): {OK / FLAG / UNABLE TO ASSESS (image)}
  [if flagged, show inconsistency]

Module 12 (Red Flags): {NONE / {n} INSTANCES FLAGGED}
  [list each with S-1 quote, section, and why flagged]
```

---

### PHASE 4: SELECT TRIALS FOR PASS 2 & DOWNLOAD SOURCE DATA

After Pass 1 completes for all selected candidates, present:

```
Pass 1 complete. Found {n} issues across {m} candidates.

Now I can run the detailed trial-level analysis. This compares 
the S-1's description of each trial to the source data on 
ClinicalTrials.gov.

Here are the trials I can check:

Candidate: {name}
  1. NCT________ — {title} — Results POSTED on CTgov
  2. NCT________ — {title} — Results NOT POSTED 
     (design-only check possible)
  3. NCT________ — {title} — Results POSTED on CTgov

Candidate: {name}
  ...

Which trials would you like me to analyze in detail?
(Enter numbers, or "all")
```

Wait for selection.

**How the ClinicalTrials.gov download works (for Claude Code to implement):**

Each study has a page at: `https://clinicaltrials.gov/study/{nctId}`
(Example: `https://clinicaltrials.gov/study/NCT01007279`)

That page has a "Download" button. When clicked, it offers:
- File Format: JSON (select this)
- Data Fields: All available (select this)

This download corresponds to the ClinicalTrials.gov API v2 endpoint:

```
GET https://clinicaltrials.gov/api/v2/studies/{nctId}
```

**No authentication required. No API key needed.**

Example: `https://clinicaltrials.gov/api/v2/studies/NCT01007279`

This returns the FULL study record as a JSON object with all available 
data fields — identical to clicking Download → JSON → All available 
on the website.

**For each selected trial, run:**
`python scripts/ctgov_fetch.py --nct {nct_number}`

The script should:
1. Call `https://clinicaltrials.gov/api/v2/studies/{nctId}`
2. Save the raw JSON response to the working directory as 
   `ctgov_{nctId}.json`
3. Check whether `resultsSection` exists and is non-empty:
   - If yes → results are posted (full comparison possible)
   - If no → results not yet posted (design-only check)
4. Extract and structure key fields for the comparison 
   (see CTgov JSON Field Paths below)
5. Save the structured extraction as `ctgov_{nctId}_structured.json`

**Rate limiting**: 1 request per second max to ClinicalTrials.gov.

**Error handling**:
- 404 → "Study {nctId} not found on ClinicalTrials.gov. 
  Verify the NCT number."
- 500/503 → Retry once after 3 seconds, then report error.
- Timeout → Retry once, then report error.

Present results to user:
```
Downloaded study records from ClinicalTrials.gov:

✓ NCT________ — {brief_title}
  Status: {overall_status} (e.g., COMPLETED)
  Results: POSTED — full comparison possible
  Sponsor: {sponsor}
  
✗ NCT________ — {brief_title}
  Status: {overall_status} (e.g., RECRUITING)
  Results: NOT YET POSTED — design-only check possible

Shall I proceed with the trial-level analysis?
```

---

### PHASE 5: PASS 2 — TRIAL-LEVEL ANALYSIS

**Before starting, read**: `reference/trial_level_modules.md`

**Tell the user:**
```
PASS 2: TRIAL-LEVEL ANALYSIS

I'm now comparing the S-1's description of each selected trial 
against the source data from ClinicalTrials.gov — the federally 
mandated public record.

I'm checking four things:

1. TRIAL WORKSHEET — Does the S-1 disclose the trial's design, 
   population, dosing, endpoints, and results? For each data point 
   in the public record, did the S-1 include it?

2. STATISTICS — If the S-1 presents statistical results, are they 
   accurate? Are pre-specified and post-hoc analyses clearly 
   distinguished? If the trial wasn't powered for significance, 
   does the S-1 avoid implying confirmatory conclusions?

3. SAFETY — Does the S-1 replace safety adjectives with actual 
   data? Are SAEs disclosed with types and counts? Are TEAEs 
   defined? Is "well-tolerated" supported by numbers?

4. INTERIM/TOPLINE — If the data is interim or topline, does the 
   S-1 say so? Does it identify what remains (database lock, 
   verification)? Does it avoid conclusory adjectives for 
   preliminary data?
```

For each selected trial, run comparison_builder.py to produce 
the side-by-side comparison, then execute Modules 4, 5, 6, 10:

#### Module 4: Trial Worksheet

**What the script builds**: comparison_builder.py creates the 
side-by-side table:

```
DESIGN COMPARISON
| Element        | CTgov                | S-1 Says            | Status  |
|----------------|----------------------|---------------------|---------|
| Phase          | PHASE2, PHASE3       | "Phase 2b/3"        | MATCH   |
| Allocation     | RANDOMIZED           | not stated           | ABSENT  |
| Masking        | QUADRUPLE            | "double-blind"       | PARTIAL |
| Control        | PLACEBO_COMPARATOR   | "placebo-controlled" | MATCH   |
| Enrollment     | 234 (ACTUAL)         | "approximately 230"  | APPROX  |
| ...            | ...                  | ...                  | ...     |
```

**What Claude checks**:

For each ABSENT item, assess:
  → Is this a design element the SEC has specifically asked for?
    (Check Module 4 authority list)
  → Would a reasonable investor want to know this to understand 
    the trial?

For EFFICACY:
  → For each primary endpoint in CTgov: is it discussed in S-1?
  → For each secondary endpoint in CTgov: is it discussed in S-1?
  → Are endpoints that FAILED discussed, or only successful ones?
  → IF primary endpoint failed but S-1 leads with secondary:
    FLAG — cite Harkonen precedent

For SAFETY: (overlaps with Module 6, but the presence check here 
is mechanical: did the S-1 include the data point?)

**Authority citations**: Each ABSENT finding cites the specific 
comment letter URL where the SEC asked for that element.

#### Module 5: Statistics Check

**What the script pre-computes**:

For each outcome measure in CTgov that has statistical analysis:
- Extract: p-value, CI, statistical method, analysis population
- Match to the S-1's stated values (if present)
- Flag: any numerical mismatch (p-value, CI, effect size)

**What Claude checks**:

5.1 PRE-SPECIFIED VS POST-HOC
  → Does CTgov list the outcome as primary/secondary?
  → Does the S-1 present it as if it were primary when CTgov 
    shows it's secondary or exploratory?
  → Are any results from subgroup analyses? If so, does the 
    S-1 label them as such?
  → IF subgroup analysis presented as headline result:
    FLAG — cite Harkonen (conviction for exactly this)

5.2 POWERING
  → Was the trial powered for the endpoint being discussed?
    (CTgov enrollment vs. typical powering for the endpoint type
     provides a rough check; Claude notes if this is unclear)
  → IF S-1 implies significance from underpowered trial:
    FLAG — cite SEC comment letters requiring powering disclosure

5.3 STATISTICAL ACCURACY
  → Do p-values match between S-1 and CTgov?
  → Do confidence intervals match?
  → IF S-1 says "statistically significant" without providing 
    p-value: FLAG

5.4 DESCRIPTIVE VS INFERENTIAL
  → IF Phase 1 or small Phase 2a (not powered):
    Does S-1 present outcomes descriptively or inferentially?
    Inferential presentation (p-values, "significant") of 
    underpowered data: FLAG

#### Module 6: Safety Check

**What the script builds**:

```
SAFETY COMPARISON
| Metric                    | CTgov Arm 1    | CTgov Arm 2   | S-1       |
|---------------------------|----------------|---------------|-----------|
| Any AE (n/N, %)          | 45/78 (57.7%)  | 38/76 (50.0%) | "..."     |
| Any SAE (n/N, %)         | 8/78 (10.3%)   | 3/76 (3.9%)   | NOT DISC. |
| Deaths                   | 0              | 0             | NOT DISC. |
| Discontinued due to AE   | 6/78 (7.7%)    | 2/76 (2.6%)   | NOT DISC. |

SERIOUS ADVERSE EVENTS (from CTgov):
| Event          | Arm 1 (n/N)   | Arm 2 (n/N)   | In S-1? |
|----------------|---------------|---------------|---------|
| Pneumonia      | 3/78          | 1/76          | No      |
| Cellulitis     | 2/78          | 0/76          | No      |
| ...            | ...           | ...           | ...     |

COMMON AEs ABOVE THRESHOLD (from CTgov):
| Event          | Arm 1 (n/N, %)| Arm 2 (n/N, %)| In S-1? |
|----------------|---------------|---------------|---------|
| Headache       | 12/78 (15.4%) | 8/76 (10.5%)  | No      |
| Nausea         | 10/78 (12.8%) | 7/76 (9.2%)   | Yes     |
| ...            | ...           | ...           | ...     |
```

**What Claude checks**:

6.1 ADJECTIVE VS DATA
  → IF S-1 uses "well-tolerated," "acceptable safety profile,"
    "favorable," or similar:
    Is it followed by actual AE/SAE/discontinuation data?
    IF NOT: FLAG — cite FibroGen comment letter, SEC comment 
    that safety determinations are FDA's authority

6.2 SAE COMPLETENESS
  → Are SAEs disclosed with types and counts per arm?
  → IF SAEs occurred but S-1 does not disclose them: FLAG
  → IF S-1 says "no drug-related SAEs" but CTgov shows SAEs 
    that investigators classified differently: FLAG and note 
    the distinction (sponsor assessment vs investigator assessment)

6.3 DIFFERENTIAL
  → IF treatment arm SAE rate substantially exceeds control:
    Does the S-1 acknowledge this differential?
    FLAG if not.

6.4 TERMINOLOGY
  → IF S-1 uses "TEAE" or "SAE" without defining them: FLAG
  → IF S-1 conflates TEAE with SAE: FLAG

#### Module 10: Interim/Topline Check

**What the script pre-computes**:
- CTgov overall_status: is the study COMPLETED or ACTIVE/RECRUITING?
- CTgov results posting date vs S-1 filing date
- Whether CTgov results say "interim" anywhere

**What Claude checks**:

IF S-1 describes data from an ongoing trial:
  → Does S-1 state data cutoff date?
  → Does S-1 identify data as interim/preliminary?
  → Does S-1 identify what remains (database lock, monitoring)?
  → Does S-1 use conclusory adjectives ("positive," "successful") 
    for interim data? IF SO: FLAG

IF S-1 describes "topline" results:
  → Does S-1 note that full analysis may differ?
  → Is there caution that the dataset is not final?

#### Pass 2 Output (per trial)

```
PASS 2 FINDINGS: {NCT number} — {drug}, {indication}

SOURCE SUMMARY: {2-3 sentences on what CTgov shows}

S-1 SUMMARY: {2-3 sentences on how the S-1 describes this trial}

Module 4 (Trial Worksheet):
  Design elements: {n} present, {n} absent
  Endpoints: {n} of {total} primary disclosed, 
             {n} of {total} secondary disclosed
  [List each ABSENT item with severity and authority]

Module 5 (Statistics):
  [List each finding]

Module 6 (Safety):
  Safety data completeness: {complete / partial / minimal}
  [List each finding]

Module 10 (Interim/Topline):
  {Applicable / Not applicable}
  [If applicable, list findings]
```

---

### PHASE 6: GUARDRAIL SWEEP

**Read**: `reference/guardrails.md`

After both passes are complete, apply the guardrails to ALL findings.

**Tell the user:**
```
GUARDRAIL ASSESSMENT

I've completed both passes. Now I'm applying the overarching 
legal standards to assess the findings as a whole.

The core question is from Securities Act Rule 408: looking at 
the S-1's clinical trial disclosures as a whole, would a 
reasonable investor come away with a misleadingly optimistic 
view of the company's clinical programs?

I'm also applying:
- Omnicare: Do opinion statements ("we believe...") omit 
  material contrary facts?
- Matrixx: Are findings being dismissed because they're "not 
  statistically significant"? (The Supreme Court rejected a 
  bright-line significance test for materiality.)
```

**What Claude does**:

1. RULE 408 SWEEP
   Look across ALL findings from Pass 1 and Pass 2:
   → Is there a pattern of consistently favorable framing?
   → Are unfavorable results systematically omitted or 
     de-emphasized?
   → Would the total mix mislead a reasonable investor?
   
   IF pattern found: This is the highest-severity finding.
   A pattern of one-sided disclosure is more material than 
   any individual omission.

2. OMNICARE SWEEP
   Collect every characterization flagged in Pass 1 (Module 12 
   red flags) and Pass 2 (safety adjectives, efficacy claims).
   For each:
   → What impression does it create?
   → What facts from the source data conflict?
   → Are the conflicting facts disclosed in the S-1?
   
   Group by type: safety characterizations, efficacy 
   characterizations, regulatory characterizations.

3. MATRIXX CHECK
   → Are any findings dismissable on statistical significance 
     grounds alone?
   → If so, note that Matrixx holds materiality is contextual,
     not a statistical test.

---

### PHASE 7: AGGREGATE REPORT

The final output document. Structure:

```markdown
# S-1 CLINICAL TRIAL DISCLOSURE ANALYSIS REPORT

## FILING INFORMATION
Company: {name}
Ticker: {ticker}  
Filing: {form_type}, filed {date}, Accession No. {accession}
Analysis date: {today}

## HOW TO READ THIS REPORT

This report checks whether the clinical trial disclosures in 
{company}'s S-1 registration statement are complete, accurate, 
and not misleading.

The analysis was conducted in two passes:
- **Pass 1** examined how the S-1 presents each drug candidate 
  using only the S-1 text
- **Pass 2** compared the S-1's trial descriptions against 
  source data from ClinicalTrials.gov

Findings are rated by severity:
- **CRITICAL**: A reasonable investor would likely consider this 
  important. Creates meaningful § 11 exposure risk.
- **SIGNIFICANT**: Warrants attention. May contribute to a 
  misleading impression especially in combination with other 
  findings.
- **MINOR**: A gap in disclosure that, standing alone, is 
  unlikely to be material, but should be corrected as best 
  practice.

Every finding cites:
- The exact S-1 passage (or notes its absence)
- The specific rule, case, or SEC comment letter that applies
- For Pass 2 findings: the specific data from ClinicalTrials.gov

## CANDIDATES ANALYZED

| # | Candidate | Indications | Phase | Trials Checked |
|---|-----------|-------------|-------|----------------|
| 1 | ... | ... | ... | {n} of {total} |

---

## PASS 1: PROGRAM-LEVEL FINDINGS

### {Candidate 1 Name}

{Module-by-module findings as specified above}

### {Candidate 2 Name}

{Module-by-module findings}

---

## PASS 2: TRIAL-LEVEL FINDINGS

### {NCT number} — {drug}, {indication}

{Module-by-module findings as specified above}

### {NCT number} — {drug}, {indication}

{Module-by-module findings}

---

## GUARDRAIL ASSESSMENT

### Rule 408 — Overall Misleading Impression
{Assessment: Is there a systematic pattern?}

### Omnicare — Opinion Statements
{List of characterizations with contrary facts}

### Matrixx — Statistical Significance ≠ Materiality
{Any findings where this applies}

---

## SUMMARY

### Disclosure Adequacy: {ADEQUATE / DEFICIENT / MATERIALLY DEFICIENT}

### § 11 Exposure Assessment: {LOW / MEDIUM / HIGH / CRITICAL}

### Top Findings by Priority

1. **{title}**: {one sentence}
   S-1: "{quote}" | Source: {data point} | Authority: {cite}

2. **{title}**: {one sentence}
   S-1: "{quote}" | Source: {data point} | Authority: {cite}

3. **{title}**: {one sentence}
   S-1: "{quote}" | Source: {data point} | Authority: {cite}

### Limitations
- Compares S-1 to ClinicalTrials.gov only; published papers, 
  FDA briefing documents, and advisory committee materials may 
  contain additional information.
- ClinicalTrials.gov results reflect what the sponsor posted; 
  additional data may exist.
- Pipeline graphics embedded as images could not be parsed.
- Materiality is a legal judgment requiring attorney assessment 
  of the total mix of information.
- This tool identifies potential issues for professional review. 
  It does not render legal opinions.
```

---

## REFERENCE FILE SPECIFICATIONS

### reference/guardrails.md

Contains Module 1 with:
- Rule 408 (17 C.F.R. § 230.408) — full text + operational rule
- Rule 10b-5 (17 C.F.R. § 240.10b-5) — full text + operational rule
- Omnicare, 575 U.S. 175 (2015) — holding + three-part test
- Matrixx Initiatives, 563 U.S. 27 (2011) — holding + operational rule
- How to apply each as a "sweep" across findings

### reference/program_level_modules.md

Contains Modules 2, 3, 7, 8, 9, 11, 12 with:
- Each module's checklist items stated as IF/THEN rules
- Each authority cited with the FULL URL to the SEC comment letter
  or case, not a paraphrase
- The "what good looks like" templates where applicable
  (especially Module 3 phase nomenclature fix)

**SEC Comment Letter URLs to hardcode** (from the user's legal tree):

```
Module 2 (Identity Card):
  https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm
  (Staff asked company to state it is clinical-stage with no approved products)

Module 3 (Phase Nomenclature):
  https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm
  (Staff challenged "Phase 1/2" and "Phase 2/3" labels)

Module 7 (Preclinical):
  https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm
  (Staff required removing safety/efficacy inferences from animal data)

Module 8 (Comparative Claims):
  https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm
  (Staff required removal of "safer"/"more effective" claims)
  https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm
  (Staff required removing comparisons without head-to-head support)

Module 9 (FDA Communications):
  https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm
  (Staff challenged "positive FDA feedback" language)
  https://www.sec.gov/enforcement-litigation/litigation-releases/lr-24062
  (AVEO enforcement — omission of FDA recommendation)

Module 11 (Pipeline):
  https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm
  (Staff challenged pipeline phase signaling without IND)
  https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm
  (Staff required pipeline tables to show phases distinctly)

Module 12 (Red Flags):
  https://www.sec.gov/Archives/edgar/data/1157601/000119312523295310/filename1.htm
  (Staff: safety determinations are FDA's authority)
  https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm
  (Staff required removing statements implying safety/efficacy)
```

### reference/trial_level_modules.md

Contains Modules 4, 5, 6, 10 with:
- Each module's checklist stated as IF/THEN rules
- Each authority cited with URL
- The CTgov JSON field paths for each data element
  (so Claude knows where to look in the comparison)

**SEC Comment Letter URLs to hardcode**:

```
Module 4 (Trial Worksheet):
  https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm
  (Staff asked for enrollment numbers, design, endpoints, protocols)
  https://www.sec.gov/Archives/edgar/data/1778016/000095012319008796/filename1.htm
  (Staff required definitions for response categories)
  https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm
  (Staff required disclosure that primary endpoint not met)

Module 5 (Statistics):
  https://www.sec.gov/Archives/edgar/data/1841873/000119312521279491/filename1.htm
  (Staff required clarifying whether observed effects were significant
   and whether study was powered)
  https://www.sec.gov/Archives/edgar/data/1841873/000119312521279491/filename1.htm
  (Staff required revising graphic to distinguish post-hoc from all data)
  United States v. Harkonen — Justia:
  https://law.justia.com/cases/federal/appellate-courts/ca9/11-10209/11-10209-2013-03-04.html
  (Wire fraud conviction for misleading subgroup analysis framing)

Module 6 (Safety):
  https://www.sec.gov/Archives/edgar/data/1157601/000119312523295310/filename1.htm
  (Staff: safety determinations are FDA's authority; disclose all SAEs)
  https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm
  (Staff required SAE descriptions and counts)
  https://www.sec.gov/Archives/edgar/data/1778016/000095012319008796/filename1.htm
  (Staff required grade definitions and drug-related SAEs)
  https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm
  (Staff required objective data instead of "favorable safety profile")
  21 C.F.R. § 312.32 (SAE reporting framework):
  https://www.ecfr.gov/current/title-21/chapter-I/subchapter-D/part-312/subpart-B/section-312.32

Module 10 (Interim/Topline):
  https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm
  (Staff cautioned against "positive" characterizations of limited data)
  In re Rigel Pharmaceuticals — Caselaw:
  https://caselaw.findlaw.com/court/us-9th-circuit/1611287.html
  (When partial disclosures can be misleading)
```

### reference/red_flag_phrases.txt

Plain text file, one phrase per line, used by the script for 
pattern matching:

```
safe
effective
clinically validated
clinically proven
proven efficacy
proven safety
favorable clinical activity
promising tolerability
favorable safety profile
acceptable safety profile
well-tolerated
safer than
more effective than
superior to
best-in-class
first-in-class
fast-to-market
accelerated commercialization
positive FDA feedback
clinically meaningful
```

---

## SCRIPT SPECIFICATIONS

### edgar_fetch.py

**Purpose**: Given a ticker, find and download the latest S-1 or F-1 
(including amendments) from EDGAR.

**Dependencies**: `requests`

**EDGAR API requirements**:
- ALL requests MUST include: `User-Agent: S1DisclosureChecker/1.0 (contact@example.com)`
- Rate limit: max 10 requests/sec → add 0.2s sleep between requests

**Action: lookup** (`--ticker {TICKER} --action lookup`)

```python
# STEP 1: Ticker → CIK
# Fetch https://www.sec.gov/files/company_tickers.json
# This returns: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "..."}, ...}
# Search values for ticker match (case-insensitive)
# Extract cik_str, pad to 10 digits with leading zeros

# STEP 2: CIK → Filing history  
# Fetch https://data.sec.gov/submissions/CIK{padded_cik}.json
# Example: CIK 2085187 → CIK0002085187.json
#
# Response structure:
# {
#   "cik": "0002085187",
#   "name": "Bob's Discount Furniture, Inc.",
#   "tickers": ["BOBS"],
#   "filings": {
#     "recent": {
#       "form": ["424B4", "3", ..., "S-1/A", "S-1", ...],
#       "filingDate": ["2026-02-05", ..., "2026-01-26", "2026-01-09", ...],
#       "accessionNumber": ["0001628280-26-005868", ..., "0001628280-26-003358", ...],
#       "primaryDocument": ["bobsdiscountfurnitureinc42.htm", ..., "bobsdiscountfurnitureincs-.htm", ...]
#     },
#     "files": []  ← if present, older filings in separate JSON files
#   }
# }

# STEP 3: Find latest S-1 or F-1
# Iterate through filings.recent.form[] (index 0 = most recent)
# Find FIRST entry where form contains "S-1" or "F-1" as substring
# This catches: S-1, S-1/A, F-1, F-1/A
# Capture the INDEX

# STEP 4: Extract metadata at that index
# accession = filings.recent.accessionNumber[index]
# filing_date = filings.recent.filingDate[index]
# form_type = filings.recent.form[index]
# primary_doc = filings.recent.primaryDocument[index]

# STEP 5: Build URL
# Strip dashes from accession: "0001628280-26-003358" → "000162828026003358"
# CIK for URL path = cik without leading zeros (or with, both work)
# URL = https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primary_doc}
```

Output (JSON to stdout):
```json
{
  "company_name": "Bob's Discount Furniture, Inc.",
  "cik": "0002085187",
  "tickers": ["BOBS"],
  "form_type": "S-1/A",
  "filing_date": "2026-01-26",
  "accession_number": "0001628280-26-003358",
  "primary_document": "bobsdiscountfurnitureincs-.htm",
  "document_url": "https://www.sec.gov/Archives/edgar/data/2085187/000162828026003358/bobsdiscountfurnitureincs-.htm"
}
```

**Action: download** (`--ticker {TICKER} --action download --url {document_url}`)

1. Fetch the HTML document from the URL
2. Save to working directory as `s1_{ticker}_{filing_date}.html`
3. Report file size and path

**Edge cases**:
- If `filings.recent` has no S-1/F-1 matches, check `filings.files[]` 
  for additional JSON files containing older filings
- Some very old filings may have `.txt` primaryDocument instead of `.htm`
- DRS (Draft Registration Statement) and DRS/A are confidential drafts — 
  NOT the same as S-1. Skip these.

---

### s1_parser.py

**Purpose**: Parse S-1 HTML to extract drug candidates, study references,
passages, and flag patterns.

**Dependencies**: `beautifulsoup4`, `lxml`, `re`

**Action: find_candidates** (`--action find_candidates --file {s1_path}`)

1. Read S-1 HTML, parse with BeautifulSoup + lxml
2. Strip: `<style>`, `<script>`, hidden elements
3. Preserve section structure by detecting headers:
   - `<b>`, `<strong>`, heading tags (`<h1>`-`<h6>`)
   - Text matching known S-1 sections: "TABLE OF CONTENTS", 
     "PROSPECTUS SUMMARY", "RISK FACTORS", "USE OF PROCEEDS", 
     "BUSINESS", "MANAGEMENT'S DISCUSSION AND ANALYSIS"
   - `<a name="...">` anchors from table of contents
4. Map every paragraph to its section

5. **Find NCT numbers**: Regex `NCT\d{8}`
   - For each match: extract NCT number, section, surrounding context
     (paragraph containing it + 2 paragraphs before/after)

6. **Find drug candidate names**: 
   - Look for proper nouns near "candidate", "product candidate",
     "investigational", "our lead", "our pipeline"
   - Drug name patterns: INN suffixes (-mab, -nib, -tide, -gene, 
     -parin, -stat, etc.), internal designators (XX-1234, XXX-123)
   - Associate each candidate with its NCT numbers

7. **For each candidate, extract ALL passages** that reference it
   across the entire S-1 (search by name, by NCT number, by indication)

8. **Flag patterns** per candidate:
   - Combined phase labels: regex for "Phase [12]/[23]" variations
   - Red flag phrases: scan against `reference/red_flag_phrases.txt`
   - Comparative language: "safer", "more effective", "superior", etc.
   - FDA language: "positive feedback", "FDA agreed", designations

9. **Approximate page numbers**: 
   S-1 HTML has no real pages. Approximate by character position 
   / ~3000 chars per page. Label as "approx. page X".

Output: JSON with full candidate structure (as specified in Phase 2)

**Action: extract_passages** (`--action extract_passages --file {s1_path} --nct {nct_number}`)

For a specific NCT number, extract ALL S-1 passages referencing that 
trial. Used by comparison_builder.py in Pass 2.

Output: JSON array of passages with section and page_approx.

---

### ctgov_fetch.py

**Purpose**: Download the full study record from ClinicalTrials.gov 
as JSON, equivalent to clicking the Download button on the study page 
with JSON format and "All available" data fields selected.

**Dependencies**: `requests`

**API endpoint**: 
```
GET https://clinicaltrials.gov/api/v2/studies/{nctId}
```

No authentication required. No API key needed.

This is the same data you get when you go to 
`https://clinicaltrials.gov/study/{nctId}` and click 
Download → JSON → All available → Download.

**Process** (`--nct {nct_number}`):

1. Fetch `https://clinicaltrials.gov/api/v2/studies/{nctId}`
   - Add header: `Accept: application/json`
   - Rate limit: 1 request per second

2. Save raw JSON response as `ctgov_{nctId}.json`

3. Check results availability:
   - `resultsSection` exists and is non-empty → `has_results: true`
   - `resultsSection` absent or empty → `has_results: false`

4. Extract and structure key fields into `ctgov_{nctId}_structured.json`:

**CTgov API v2 JSON field paths** (these are the exact paths in the 
JSON response — Claude Code must use these):

```
ROOT IDENTIFICATION:
  protocolSection.identificationModule.nctId
  protocolSection.identificationModule.briefTitle
  protocolSection.identificationModule.officialTitle
  protocolSection.statusModule.overallStatus

DESIGN:
  protocolSection.designModule.studyType
  protocolSection.designModule.phases[]
  protocolSection.designModule.designInfo.allocation
  protocolSection.designModule.designInfo.interventionModel
  protocolSection.designModule.designInfo.maskingInfo.masking
  protocolSection.designModule.designInfo.maskingInfo.whoMasked[]
  protocolSection.designModule.enrollmentInfo.count
  protocolSection.designModule.enrollmentInfo.type  (ACTUAL vs ESTIMATED)

ARMS & INTERVENTIONS:
  protocolSection.armsInterventionsModule.armGroups[]
    → each has: label, type, description, interventionNames[]
  protocolSection.armsInterventionsModule.interventions[]
    → each has: type, name, description, armGroupLabels[]

ENDPOINTS (protocol-defined):
  protocolSection.outcomesModule.primaryOutcomes[]
    → each has: measure, description, timeFrame
  protocolSection.outcomesModule.secondaryOutcomes[]
    → each has: measure, description, timeFrame

ELIGIBILITY:
  protocolSection.eligibilityModule.eligibilityCriteria
  protocolSection.eligibilityModule.sex
  protocolSection.eligibilityModule.minimumAge
  protocolSection.eligibilityModule.maximumAge
  protocolSection.eligibilityModule.healthyVolunteers

SPONSOR:
  protocolSection.sponsorCollaboratorsModule.leadSponsor.name
  protocolSection.sponsorCollaboratorsModule.leadSponsor.class

RESULTS (only populated if results are posted):

  Participant Flow:
    resultsSection.participantFlowModule.groups[]
    resultsSection.participantFlowModule.periods[]
      → each period has: milestones[] (STARTED, COMPLETED, etc.)
      → each period has: dropWithdraws[] (reason, counts per group)

  Baseline Characteristics:
    resultsSection.baselineCharacteristicsModule.groups[]
    resultsSection.baselineCharacteristicsModule.denoms[]
    resultsSection.baselineCharacteristicsModule.measures[]

  Outcome Measures (ACTUAL RESULTS):
    resultsSection.outcomeMeasuresModule.outcomeMeasures[]
      → each has:
        .type  (PRIMARY, SECONDARY, OTHER, POST_HOC)
        .title
        .description
        .populationDescription
        .reportingStatus
        .groups[]
        .denoms[]
        .classes[]
          → each class has .categories[].measurements[]
            → each measurement has: groupId, value, spread, 
              lowerLimit, upperLimit
        .analyses[]
          → each analysis has:
            .groupIds[]
            .groupDescription
            .nonInferiorityType
            .pValue
            .pValueComment
            .statisticalMethod
            .statisticalComment
            .ciPctValue  (e.g., "95")
            .ciNumSides
            .ciLowerLimit
            .ciUpperLimit
            .estimateComment

  Adverse Events:
    resultsSection.adverseEventsModule.frequencyThreshold
    resultsSection.adverseEventsModule.timeFrame
    resultsSection.adverseEventsModule.description
    resultsSection.adverseEventsModule.eventGroups[]
      → each has: id, title, description,
        deathsNumAffected, deathsNumAtRisk,
        seriousNumAffected, seriousNumAtRisk,
        otherNumAffected, otherNumAtRisk
    resultsSection.adverseEventsModule.seriousEvents[]
      → each has: term, organSystem, assessmentType, 
        stats[] (each: groupId, numEvents, numAffected, numAtRisk)
    resultsSection.adverseEventsModule.otherEvents[]
      → same structure as seriousEvents
```

Output: Both the raw JSON and the structured extraction.

---

### comparison_builder.py — SPECIFICATION (unchanged from v2 body above)

Takes S-1 passages (from s1_parser.py) and CTgov structured JSON 
(from ctgov_fetch.py) for the same trial, and produces a side-by-side 
comparison document in markdown format.

See the detailed specification in the Phase 5 section of this document
for the exact comparison table formats (DESIGN, EFFICACY, SAFETY, 
CHARACTERIZATIONS).

---

## BUILD ORDER FOR CLAUDE CODE

1. Create directory structure
2. Write edgar_fetch.py — test with SLRN
3. Write s1_parser.py (find_candidates) — test on SLRN S-1
4. Write ctgov_fetch.py — test with NCT numbers from SLRN
5. Write comparison_builder.py — test with SLRN data
6. Write reference/red_flag_phrases.txt
7. Write reference/guardrails.md (Module 1 from legal tree)
8. Write reference/program_level_modules.md (Modules 2,3,7,8,9,11,12)
9. Write reference/trial_level_modules.md (Modules 4,5,6,10)
10. Write SKILL.md (orchestrator)
11. End-to-end test with SLRN
12. Package as ZIP

---

## TEST CASE: ACELYRIN (SLRN)

Expected behavior:
- edgar_fetch.py finds CIK 0001962918, S-1/A ~April 2023
- s1_parser.py identifies candidates: izokibep, lonigutamab, SLRN-517
- Pass 1 flags: check for comparative claims (izokibep vs adalimumab),
  phase nomenclature for any combined-phase trials, red flag phrases
- ctgov_fetch.py downloads JSONs for NCT numbers
- Pass 2 compares trial descriptions to CTgov data
- Report generated with findings, authorities, and severity ratings
