# LEGAL BRIEF: S-1 Clinical Trial Disclosure Review
# Framework for Assessing Disclosure Adequacy

---

<!-- ANCHOR: STATEMENT_OF_LAW -->
## I. STATEMENT OF LAW

Every person who signs an S-1 registration statement is strictly
liable for material misstatements or omissions. No proof of
scienter is required.

**Governing provisions:**

- Securities Act § 11 (15 U.S.C. § 77k): Strict liability for
  material misstatements or omissions in registration statements.
  Any person who signed the S-1, any director, any expert whose
  opinion is cited, and the underwriter are all potentially liable.

- Rule 408 (17 C.F.R. § 230.408): In addition to the information
  expressly required by Regulation S-K, the S-1 must include "such
  further material information, if any, as may be necessary to make
  the required statements, in light of the circumstances under which
  they are made, not misleading."

- Regulation S-K, Items 101(c) and 303: Require description of
  products, business, and material trends — which for a clinical-
  stage biotech company means the clinical trial program.

**How we derive the specific standards:**

There is no current SEC industry guide specifically for biotech
S-1s. Instead, the specific disclosure requirements are derived
from what the SEC actually enforces. The primary source is SEC
**comment letters** — written feedback sent to registrants during
S-1 review, identifying specific disclosures the SEC considers
deficient and requiring amendment.

This framework is built from 22 verified verbatim SEC comment
letter excerpts, 3 enforcement actions, and 5 case law authorities,
all specific to clinical trial disclosure in biotech filings. Each
authority is cited with the company name, filing type, and date,
and the SEC's exact language is reproduced.

The analysis proceeds in three steps:

  STEP 1 — Are the drug candidates described correctly?
           (Cross-cutting S-1 language checks)

  STEP 2 — Are the clinical studies described correctly?
           (Per-study comparison against ClinicalTrials.gov)

  STEP 3 — Does the overall pattern mislead?
           (Escalation assessment across all findings)


---

<!-- ANCHOR: STEP_1 -->
## II. STEP 1: ARE THE DRUG CANDIDATES DESCRIBED CORRECTLY?

This step reads the S-1 text about each drug candidate — across
all sections — and checks whether the language complies with SEC
comment letter standards. No external data source is compared yet;
this is purely an assessment of what the S-1 says.


### A. BASIC COMPLETENESS (Checks 1, 2, 6)

**Legal basis:** Rule 408 — if the S-1 discusses a clinical
program, the description must include enough information for an
investor to understand what the drug is, what stage it is in, and
what it treats. Omitting basic elements makes the disclosure
misleading by incompleteness.

#### Check 1: Basic Disclosure Elements

**Question:** For each drug candidate, does the S-1 disclose the
drug name, modality, indication, and development stage?

**Test:** Presence check — code scans for each element. No
judgment call needed.

**Source:** No specific comment letter. This is a threshold check
— if a company fails to identify what its drug *is*, there is a
larger problem. But the SEC does require these elements for trial-
specific disclosure (see Immunocore and Maze letters, Check 8).

**Result:** ✓ = present, ✗ = absent → YELLOW.

---

#### Check 2: Phase Label Accuracy

**Question:** If the S-1 uses combined phase labels ("Phase 1/2",
"Phase 2/3"), does it explain what each portion involves?

**The SEC's concern:** Combined labels "may be read to imply a
shorter clinical trial process or further progress than has
actually been made, and may skew a potential investor's
understanding." The SEC requires either (a) removing the combined
label and using distinct phases, or (b) explaining the FDA basis
for a combined-phase design.

**Test:**
1. Scan for combined labels (regex: "Phase X/Y")
2. If found, check whether explanation text appears nearby: "dose
   escalation", "expansion", "transition criteria", "Part A/B"
3. If combined label without explanation → ESCALATE to LLM with
   comparison against SEC comment letter text

**Sources:**

> **Sensei Biotherapeutics** (S-1, Dec. 9, 2020): "Please remove
> all references to 'Phase 1/2' and 'Phase 2/3' clinical trials
> throughout the prospectus and instead reference either phase 1,
> 2, or 3 distinctly or tell us the basis for your belief that
> [you] have been approved to conduct a Phase 1/2 trial... Our
> concern is that the references as currently disclosed may be read
> to imply a shorter clinical trial process or further progress
> than has actually been made."

> **Nuvalent** (S-1, Jun. 25, 2021): "Please remove all references
> to 'Phase 1/2' clinical trials throughout the prospectus and
> instead reference either phase 1, 2, or 3 distinctly or tell us
> the basis for your belief that [you] have been approved to
> conduct a Phase 1/2 trial."

> **Taysha Gene Therapies** (S-1, Sep. 1, 2020): "Include separate
> columns for Phase 1 and Phase 2 trials or tell us the basis for
> your belief that you will be able to conduct Phase 1/2 trials for
> all your product candidates."

**Note:** Sub-phase labels ("Phase 2a", "Phase 2b") are standard
FDA terminology and have NOT been challenged by the SEC.

**Result:** ✓ = no combined labels or adequately explained,
≈ = combined label with partial explanation → YELLOW,
✗ = combined label without explanation → RED.

---

#### Check 6: Pipeline Table Accuracy

**Question:** If the S-1 includes a pipeline table or graphic, do
the phase designations match the text descriptions?

**The SEC's concern:** Pipeline tables use marketing terminology
("Pivotal") instead of regulatory phases ("Phase 3"), or show
combined labels without justification, or add extra columns
("IND-enabling") that create a visual impression of more progress.

**Test:**
1. If HTML pipeline table → extract and compare to text
2. If image-embedded pipeline → YELLOW (manual review needed)
3. Check for marketing labels: "Pivotal" → should be "Phase 3"

**Source:**

> **Taysha Gene Therapies** (S-1, Sep. 1, 2020): The SEC required
> the company to "replace 'Pivotal' with 'Phase 3'" and merge
> "preclinical" and "IND-enabling" into a single column.

**Result:** ✓ = consistent, ≈ = image not parseable → YELLOW,
✗ = mismatch to text → RED.


---

### B. SAFETY AND EFFICACY LANGUAGE (Checks 3, 4, 7)

**Legal basis:** The SEC has consistently held that "safety and
efficacy determinations are solely within the authority of the
FDA." This is the single most frequently invoked standard in
biotech comment letters. It produces three specific prohibitions:
(i) no claiming or implying a drug is safe or effective before FDA
approval, (ii) no using preclinical data to imply clinical
efficacy, and (iii) no comparing favorably to competitors without
head-to-head data.

#### Check 7: Red Flag Phrases

**Question:** Does the S-1 use words or phrases that the SEC has
consistently required to be removed or revised?

**The SEC's standard:** Stated identically across dozens of comment
letters: "Please remove all statements throughout your registration
statement that state or imply your conclusions regarding the safety
or efficacy of your product candidates and technologies, as these
determinations are solely within the authority of the FDA."

**The bright-line rules:**

ALWAYS CHALLENGED (must be removed regardless of context):
- "safe", "effective", "safe and effective"
- "safe and well tolerated"
- "proven safety/efficacy", "established safety/efficacy"
- "favorable safety profile", "acceptable safety profile"
- "demonstrated efficacy"

PERMITTED IF SUPPORTED:
- "well-tolerated" — permitted IF true, supported by specific
  AE/SAE data nearby, and basis is explained (the Madrigal
  three-part test, below)
- "no SAEs reported" / "no treatment-related SAEs" — permitted
  if factually true
- Balanced presentation of objective data without conclusions

**The Madrigal three-part test** (for "well-tolerated"):
1. Is the characterization true?
2. Are SAEs disclosed alongside the claim?
3. If SAEs occurred, is the basis for "well tolerated" explained?

**Test:**
1. Scan for all red flag phrases in candidate passages
2. Classify each hit: CAUTIONARY (risk factors / conditional
   language) → auto GREEN; SUPPORTED (with nearby data) → auto
   GREEN; STANDALONE (affirmative, no data) → FLAGGED
3. Pattern check: >5 standalone instances of same phrase →
   PATTERN flag (matches Altamira "numerous places throughout")
4. If flagged → ESCALATE to LLM with comparison against all five
   comment letter texts

**Sources:**

> **Altamira Therapeutics** (F-1, Feb. 24, 2023) — THE ANCHOR:
> "We note statements in numerous places throughout the registration
> statement stating or suggesting that your OligoPhore and SemaPhore
> peptide polyplex platform technology is 'safe and effective.' ...
> Similarly, your discussions of various clinical trials include
> statements that your product candidates are 'safe and well
> tolerated' or have a 'favorable safety profile,' such as on pages
> 55-57 and 84, 88, and 89. Please remove all statements throughout
> your registration statement that state or imply your conclusions
> regarding the safety or efficacy of your product candidates and
> technologies, as these determinations are solely within the
> authority of the FDA and comparable regulatory bodies. With
> respect to safety, we will not object to statements that your
> product candidates are well-tolerated, if true, or that no
> serious adverse events deemed to be study related were reported.
> You may also present a balanced summary of objective pre-clinical
> and clinical data, including whether clinical trials met primary
> and secondary endpoints, without including your conclusions
> related to efficacy."

> **Graybug Vision** (S-1, Aug. 27, 2020): "Please revise your
> disclosure here and throughout your prospectus to remove your
> characterization of GB-102 as safe, as a determination of whether
> a product candidate is safe is solely within the authority of the
> U.S. Food and Drug Administration."

> **Madrigal Pharmaceuticals** (10-K, Nov. 21, 2023) — THREE-PART
> TEST: "(a) Determinations related to safety are within the sole
> authority of the FDA. In future filings, please refrain from
> making such assessments related to product candidates that have
> not been approved. (b) Additionally, please disclose all serious
> adverse events related to Resmetirom and disclose the number of
> such events. (c) Explain how you have determined that the
> candidate is well tolerated when trial participants experienced
> serious adverse events."

> **Scopus BioPharma** (Form 1-A, Jun. 24, 2020): "Safety is a
> determination that is solely within the authority of the FDA or
> similar foreign regulators." (Challenged even when attributed
> to NIH researchers — attribution to third parties does not cure.)

> **OS Therapies** (S-1, Mar. 27, 2023): "investors should be able
> to assess how the drug candidate performed relative to the
> established endpoints... and also assess your conclusion that
> 'the data presented from the Phase Ib trial demonstrated that
> ADXS31-164 was well tolerated.'" (Challenged because
> "demonstrated that [drug] was well tolerated" draws a conclusion
> rather than presenting data.)

**Result:** ✓ = no standalone red flag phrases,
≈ = some standalone phrases but partially supported → YELLOW,
✗ = Tier 1 phrases or pattern flag → RED.

---

#### Check 3: Preclinical Framing

**Question:** Does the S-1 present preclinical (animal/in vitro)
data as evidence of clinical (human) safety or efficacy?

**The SEC's concern:** The same "solely within the authority of
the FDA" standard, applied specifically to the preclinical-to-
clinical translation gap. Even hedged language ("may provide") is
challenged because the animal-to-human leap is the fundamental
problem, not the company's confidence level.

**Test:**
1. Scan for preclinical indicators: "animal model", "in vivo",
   "in vitro", "preclinical", "mouse", "rat", "non-human"
2. Check for translation-risk caveat nearby: "may not predict",
   "no assurance", "preclinical results may not be indicative"
3. Check verbs: factual ("inhibits", "has shown") vs. hypothetical
   ("designed to", "intended to")
4. If preclinical claim without caveat → ESCALATE

**Sources:**

> **Curanex Pharmaceuticals** (S-1, Jul. 17, 2024): "You state
> that your lead product candidate, Phyto-N, has demonstrated
> promising efficacy in animal models and has a long history of
> safe use in traditional medicine. Safety and efficacy
> determinations are solely within the authority of the FDA...
> Please revise or remove statements/inferences throughout your
> prospectus that your product candidate is safe and/or effective."

> **Virpax Pharmaceuticals** (S-1, Sep. 4, 2020): "We note your
> disclosure that early animal studies indicate that Probudur may
> provide pain control for up to 96 hours... Please revise these
> and similar statements throughout your registration statement
> that state or imply that your product candidates are safe or
> effective." (Note: even hedged "indicate... may provide" was
> challenged.)

> **Curanex** (second comment): "You state that Phyto-N boasts
> superior anti-inflammatory properties and unlike recently FDA
> approved Rezdiffra, Phyto-N mitigates inflammation occurrence
> without causing adverse reaction... Please discuss your basis
> for such claims." (Preclinical company comparing to FDA-approved
> drug.)

**Result:** ✓ = preclinical claims have translation caveats,
≈ = mixed → YELLOW,
✗ = preclinical efficacy/safety claims without caveat → RED.

---

#### Check 4: Comparative Claims

**Question:** Does the S-1 compare its drug favorably to
competitors without head-to-head clinical data?

**The SEC's concern:** Claims like "best-in-class", "superior",
"safer", "more effective" suggest the drug is effective and likely
to be approved. The SEC requires either head-to-head clinical data
or removal. Critically, qualifying language ("we believe", "we
expect") does NOT cure the problem — the SEC has explicitly said so.

**Test:**
1. Scan for: "best-in-class", "first-in-class", "superior",
   "differentiated", "safer", "more effective", "outperform"
2. Check whether head-to-head trial citation appears nearby
3. If comparative claim without head-to-head data → ESCALATE

**Sources:**

> **Nuvalent** (S-1, Jun. 25, 2021): "The term 'best-in-class'
> suggests that the product candidates are effective and likely to
> be approved... Given the early stage of development of NVL-520
> and NVL-655, it is not appropriate to suggest that this product
> is likely to be effective or receive regulatory approval. Please
> delete these references."

> **Relay Therapeutics** (S-1, Jun. 18, 2020): "These terms suggest
> that the product candidates are effective and likely to be
> approved. Please delete these references... If your use of these
> terms was intended to convey your belief that the products are
> based on a novel technology or approach... you may discuss how
> your technology differs from technology used by competitors."

> **Zenas BioPharma** (S-1, May 15, 2024) — THE "WE BELIEVE"
> HOLDING: "Qualifying language that statements of safety and
> efficacy are expressions of the company's beliefs or expectations
> **do not address this concern.**" (The SEC explicitly rejecting
> the "we believe" defense.)

> **Khosla/Valo Health** (S-4, Jul. 28, 2021): "Please remove the
> comparison to S1P1R functional antagonists unless these
> antagonists were included in a head-to-head clinical trial."
> (Even mechanistic comparisons need head-to-head data if they
> imply clinical advantage.)

**Result:** ✓ = no unsupported comparative claims,
≈ = "differentiated" or factual distinction → YELLOW,
✗ = "best-in-class"/"safer"/"superior" without data → RED.


---

### C. FDA COMMUNICATIONS & DATA MATURITY (Checks 5, 11)

**Legal basis:** Beyond the specific language prohibitions above,
the SEC requires balanced disclosure of FDA interactions and honest
labeling of data maturity. Selective disclosure of positive FDA
feedback while omitting negative feedback has resulted in fraud
charges.

#### Check 5: FDA Communications Balance

**Question:** Does the S-1 disclose FDA interactions symmetrically
— both positive AND negative? Does it imply approval is more likely
or the path is easier than it actually is?

**The SEC's concern:** A company can create a misleadingly positive
impression by telling half the FDA story — the positive half.

**Test:**
1. Scan all FDA-related passages
2. Classify by section (Summary, Business, Risk Factors) and
   tone (positive, negative, neutral)
3. If positive > 0 and negative = 0 → RED (one-sided)
4. If positive in Business but negative only in Risk Factors →
   YELLOW (asymmetric placement)
5. If balanced → GREEN

**Sources:**

*Enforcement:*
> **SEC v. AVEO Pharmaceuticals** (LR-24062, 2018): Fraud charges
> for selectively disclosing positive FDA feedback while omitting
> that FDA recommended an additional clinical trial.

*Case law:*
> **Tongue v. Sanofi**, 816 F.3d 199 (2d Cir. 2016): Material
> FDA feedback — especially negative — must be disclosed.

*Comment letters:*
> **Aerovate Therapeutics** (S-1, Jun. 2, 2021): "Please revise to
> provide context for such statement and balance your disclosure by
> stating that the process of clinical development is inherently
> uncertain and there can be no guarantee that you will obtain
> marketing approval... These statements could imply that the FDA
> has approved, or will more easily approve, your product
> candidate."

> **Annovis Bio** (S-1, Jun. 21, 2019): "We note your disclosure
> that you expect to obtain FDA approval in 2024... there can be
> no certainty as to when or if you will receive FDA approval."

**Result:** ✓ = balanced disclosure,
≈ = asymmetric placement → YELLOW,
✗ = one-sided positive → RED.

---

#### Check 11: Data Maturity

**Question:** If the S-1 presents preliminary, interim, or topline
data, does it clearly label it as such? Does it use conclusory
verbs ("demonstrated", "established", "proven") for data that is
not final?

**The SEC's concern:** Conclusory language applied to preliminary
data overstates the strength of the evidence. Primary endpoint
failures must be disclosed. Limited sample sizes must be
acknowledged.

**Test:**
1. Check ClinicalTrials.gov: Is the trial complete? Are results
   posted?
2. Scan S-1 for conclusory verbs applied to data from unfinished
   or unreported trials
3. Check whether data is labeled as preliminary
4. If conclusory language + unfinished trial → ESCALATE

**Sources:**

> **Stealth BioTherapeutics** (F-1, Nov. 21, 2018): "Please
> expand your discussion of LHON in the summary and throughout
> your registration statement to disclose that the Phase 2
> clinical trial did not meet its primary endpoint... clarify
> in your risk factor... that the phase 2 clinical trial failed
> to meet the primary endpoint."

> **Sensei Biotherapeutics** (S-1, Dec. 9, 2020): "We note your
> statements throughout the prospectus that SNS-301 has been
> 'well-tolerated and has shown promising anti-tumor activity'
> and you characterize the results received to date as positive.
> However, given that only nine patients have been evaluated to
> date, please revise your disclosure in the Summary to present a
> balanced view of the ongoing clinical trial and the meaning of
> the results."

**Result:** ✓ = data properly labeled,
≈ = some conclusory verbs but data is labeled → YELLOW,
✗ = conclusory language on unfinished trial → RED.


---

<!-- ANCHOR: STEP_2 -->
## III. STEP 2: ARE THE CLINICAL STUDIES DESCRIBED CORRECTLY?

Step 1 examined the S-1's *language*. Step 2 examines the S-1's
*facts* by comparing what the S-1 says about each clinical trial
to the federal registry record on ClinicalTrials.gov.

ClinicalTrials.gov is a public, legally mandated record.
Registrants must report trial design, enrollment, endpoints, and
(under FDAAA 801) results within 12 months of primary completion.
Where the S-1 and ClinicalTrials.gov disagree, one is wrong.

Step 2 runs **per trial** for each drug candidate — covering all
trials the company has registered.


### A. WHAT THE S-1 MUST INCLUDE (and the legal support)

The SEC has told companies exactly what trial-level information
investors need. The required disclosure elements for each clinical
trial are:

| Element | Legal Support |
|---------|--------------|
| Number of patients enrolled and treated | Immunocore (Dec. 14, 2020): "the number of patients (e.g., number of patients enrolled and treated and the criteria for participation in the study)" |
| Criteria for participation | Immunocore: "the criteria for participation in the study" |
| Duration of treatment | Immunocore: "duration of treatment" |
| Dosage information | Immunocore: "dosage information" |
| Primary and secondary endpoints | Maze Therapeutics (Jul. 25, 2024): "describe any primary and secondary endpoints and whether they were achieved" |
| Whether endpoints were achieved | Maze: "whether they were achieved" |
| Whether results were statistically significant | OS Therapies (Mar. 27, 2023): "whether the reported results were or were not statistically significant" |
| Description of SAEs and their count | Maze: "describe them and quantify the number of each type of event" |
| Primary endpoint failure (if applicable) | Stealth BioTherapeutics (Nov. 21, 2018): "disclose that the Phase 2 clinical trial did not meet its primary endpoint" |
| Statistical powering disclosures | Coya Therapeutics (Nov. 4, 2022): "clarify, if true, that the preclinical trials... were not powered for statistical significance" |

These elements are verified against ClinicalTrials.gov in Checks
8–11 and FDAAA 801.


### B. THE CHECKS

#### Check 8: Trial Design Match

**Question:** Does the S-1's description of each trial match the
ClinicalTrials.gov record — phase, randomization, blinding,
control, enrollment, endpoints?

**Test:** Element-by-element comparison:
- Phase: S-1 phase claim vs. CTgov `designModule.phases`
- Masking: S-1 blinding description vs. CTgov `designInfo.maskingInfo`
- Allocation: S-1 randomization claim vs. CTgov `designInfo.allocation`
- Enrollment: S-1 patient numbers vs. CTgov `enrollmentInfo.count`
- Primary endpoint: CTgov `primaryOutcomes` vs. S-1 passages
- Results posted: CTgov `hasResults` → if NO and trial completed
  >12 months → FDAAA 801 flag

**Output per element:** ✓ MATCH, ✗ MISMATCH, ≈ ABSENT, ⚠ FDAAA 801

**Sources:** Immunocore, Maze, Stealth letters (quoted above).

---

#### Check 9: Endpoint Hierarchy — "The Harkonen Check"

**Question:** Does the S-1 give appropriate prominence to the
primary endpoint? Does it lead with secondary or exploratory
results while burying the primary — especially if the primary
failed?

**Why this is the most dangerous check:** This is the disclosure
pattern that resulted in a criminal conviction.

**Test:**
1. Extract primary and secondary endpoints from ClinicalTrials.gov
2. Find the S-1's "headline finding" — the first efficacy result
   in priority sections (Summary, Business)
3. Check whether headline matches a primary or secondary endpoint
4. IF headline is from SECONDARY endpoint AND primary is NOT in
   headline → ESCALATE

**THE HARKONEN PATTERN CHECK:**
```
IF headline = SECONDARY endpoint
   AND primary NOT in headline:
     IF primary NOT discussed anywhere → RED
     IF primary discussed elsewhere  → YELLOW
```

**Sources:**

*Enforcement (criminal):*
> **United States v. Harkonen (InterMune)**, 510 Fed. App'x 633
> (9th Cir. 2013): Trial primary endpoint (overall survival)
> failed (p=0.52). CEO's press release led with a post-hoc
> subgroup that appeared significant (p=0.004). Primary failure
> mentioned but buried. Result: criminal wire fraud conviction.

*Enforcement (civil):*
> **SEC v. Clovis Oncology**, LR-24273 (2018): Company reported
> 60% objective response rate using unconfirmed responses —
> confirmed ORR was only 28%. Result: $20M penalty.

*Comment letters:*
> **OS Therapies** (S-1, Mar. 27, 2023): "investors should be
> able to assess how the drug candidate performed relative to the
> established endpoints, including whether the reported results
> were or were not statistically significant."

> **Coya Therapeutics** (S-1, Nov. 4, 2022): "Please revise your
> disclosure on page 72 to clarify, if true, that the preclinical
> trials... were not powered for statistical significance."

---

#### Check 10: Safety Data Match

**Question:** Do the S-1's safety characterizations match the
actual adverse event data on ClinicalTrials.gov?

**Test:**
1. Extract AE data from CTgov results (if posted): SAE count, AE
   frequency tables
2. Find S-1 safety characterizations for the same trial
3. Compare: does the CTgov data support or contradict the S-1's
   characterization?
4. If CTgov results NOT posted → UNVERIFIABLE (cannot confirm
   S-1's claims independently)

**Sources:** Altamira, Madrigal, Scopus, OS Therapies letters
(same as Check 7 — the red flag phrase standards apply here with
the additional dimension of comparison to actual data).

---

#### Check 11: Data Maturity (study-specific)

**Question:** Does the S-1 appropriately label data as preliminary,
interim, or topline? Does it apply conclusory verbs to non-final
data?

**Test:** (operates in conjunction with Check 8 — uses trial status
from CTgov)
1. If trial is complete but results not posted → data is unverified
2. If S-1 uses "demonstrated", "established", "proven" for data
   from a trial with no posted results → flag
3. If S-1 labels data as "preliminary" / "subject to change" → OK

**Sources:** Stealth BioTherapeutics, Sensei letters (quoted above).

---

#### FDAAA 801 Compliance

**Question:** If the trial has reached primary completion, has the
company posted results within the 12-month statutory deadline?

**Legal basis:** 42 U.S.C. § 282(j)(3)(C) (FDAAA § 801) requires
posting of results on ClinicalTrials.gov within 12 months of
primary completion date. Non-compliance is not itself an S-1
violation, but it is a material fact: a company that has failed
to comply with a federal reporting obligation is subject to civil
monetary penalties of up to $10,000/day (42 U.S.C. § 282(j)(5)(C)).
If the S-1 does not disclose this non-compliance, Rule 408 may
require it as "further material information."

**Test:**
1. Extract primary completion date from CTgov
2. Check whether results are posted
3. If >12 months since completion and no results → flag
4. Check whether S-1 discloses this gap

**Result:** ✓ = results posted or <12 months, ✗ = >12 months and
no results → RED.


---

<!-- ANCHOR: STEP_3 -->
## IV. STEP 3: DOES THE OVERALL PATTERN MISLEAD?

Steps 1 and 2 examine individual statements and individual data
points. Step 3 steps back and asks whether the totality of findings
creates a misleading picture, even if no single finding is
dispositive on its own.

This step is triggered only when Step 1 and/or Step 2 have
produced YELLOW or RED findings. If everything is GREEN, Step 3
does not run.


### A. THE OMNICARE TEST (opinion statements)

**Legal basis:** *Omnicare, Inc. v. Laborers District Council*,
575 U.S. 175 (2015). The Supreme Court held that opinion
statements in registration statements can create Section 11
liability even if the speaker genuinely holds the opinion:

**Test 1 — Embedded Fact:** Does the opinion embed a factual
claim that is objectively false? Example: "We believe our drug is
well-tolerated" embeds the claim that the speaker has a reasonable
basis for this belief. If the speaker knows of SAEs that undermine
the claim, the embedded fact is false.

**Test 2 — Omitted Contrary Facts:** Does the opinion omit
material facts that the speaker knew and that cut against the
impression the opinion creates? Example: "We believe our clinical
data supports further development" omits that the primary endpoint
failed.

**Limiting principle** (also from Omnicare): Not every cheerful
opinion is actionable. The test is whether the opinion would
mislead a reasonable investor about the facts the speaker knows.

**When it triggers:** Runs ONLY on opinions flagged in Checks 7,
9, or 10 — red flag phrases, endpoint hierarchy issues, safety
characterizations contradicted by data. Each flagged opinion is
tested against the specific contrary facts found in Steps 1 and 2.

**How it works:**
For each flagged opinion, the LLM receives:
1. The exact S-1 opinion statement (with section, page)
2. The specific contrary facts found (CTgov data, missing primary
   endpoint, SAEs, etc.)
3. The Omnicare three-part test language

The LLM is asked:
- Does this opinion embed a factual claim? Is it supported?
- What facts cut against this opinion? Are they disclosed?
- Limiting principle: normal optimism or misleading impression?

**Output:** SIGNIFICANT RISK / MODERATE RISK / LOW RISK / NO CONCERN

**Calibration note:** The output says "raises questions under
Omnicare" — never "fails Omnicare" or "violates Omnicare." This
tool identifies risk; it does not render legal conclusions.


### B. RULE 408 PATTERN ANALYSIS (systematic one-sidedness)

**Legal basis:** Rule 408 (17 C.F.R. § 230.408) requires that
the S-1 not be misleading. Individual omissions may each be
borderline — not clearly material on their own. But if every
omission, gap, or characterization choice systematically favors
the company, the cumulative pattern itself makes the S-1
misleading.

**Test:**
1. List ALL findings from Steps 1 and 2
2. Classify each finding's direction:
   - FAVORS COMPANY: omission or characterization makes the drug
     look better than the data supports
   - NEUTRAL: gap doesn't clearly favor either direction
   - DISFAVORS COMPANY: (rare — overcautious disclosure)
3. Calculate: one-sided percentage = favors_company / total
   - <50% → GREEN
   - 50–75% → YELLOW
   - ≥75% → RED (systematic pattern)
4. If YELLOW or RED → ESCALATE to LLM:
   "Taken as a whole, do the omissions create a misleadingly
   optimistic picture of the clinical program?"


### C. MATRIXX DEFENSE-BLOCKER

**Legal basis:** *Matrixx Initiatives v. Siracusano*, 563 U.S. 27
(2011). The Supreme Court held there is no bright-line statistical-
significance threshold for materiality. Information can be material
to investors even if it is not statistically significant.

**How it applies:** This is not an independent check. It prevents
dismissal of findings from Steps 1 and 2 on the grounds that "the
trial wasn't powered" or "the result wasn't significant." If a
finding is otherwise material (a safety signal, an unreported
endpoint failure), Matrixx blocks the defense that it can be
ignored because it didn't reach p<0.05.


---

<!-- ANCHOR: ESCALATION_PROCEDURES -->
## V. SUMMARY: THE REVIEW MAP

```
STEP 1 — CROSS-CUTTING S-1 LANGUAGE
├── A. Basic Completeness
│   ├── Check 1  Basic Disclosure ....... [presence check]
│   ├── Check 2  Phase Labels ........... [Sensei, Nuvalent, Taysha]
│   └── Check 6  Pipeline Accuracy ...... [Taysha]
│
├── B. Safety & Efficacy Language
│   ├── Check 7  Red Flag Phrases ....... [Altamira, Graybug, Madrigal,
│   │                                      Scopus, OS Therapies]
│   ├── Check 3  Preclinical Framing .... [Curanex (×2), Virpax]
│   └── Check 4  Comparative Claims ..... [Nuvalent, Relay, Zenas,
│                                          Khosla/Valo]
│
└── C. FDA Communications & Maturity
    ├── Check 5  FDA Balance ............ [AVEO enforcement, Tongue v.
    │                                      Sanofi, Aerovate, Annovis]
    └── Check 11 Data Maturity .......... [Stealth, Sensei]

STEP 2 — PER-STUDY COMPARISON (ClinicalTrials.gov)
├── Check 8   Trial Design Match ........ [Immunocore, Maze, Stealth]
├── Check 9   Endpoint Hierarchy ........ [Harkonen (criminal), Clovis
│                                          ($20M), Coya, OS Therapies]
├── Check 10  Safety Data Match ......... [Altamira, Madrigal, Scopus]
├── Check 11  Data Maturity (per study) . [Stealth, Sensei]
└── FDAAA 801 Results Posting ........... [42 U.S.C. § 282(j)]

STEP 3 — ESCALATION (triggered by YELLOW/RED from Steps 1-2)
├── Omnicare Test ....................... [575 U.S. 175 (2015)]
├── Rule 408 Pattern Analysis ........... [17 C.F.R. § 230.408]
└── Matrixx Defense-Blocker ............. [563 U.S. 27 (2011)]
```

**Total authorities cited:**
- 22 SEC comment letter excerpts (15 unique companies)
- 3 enforcement actions (AVEO, Harkonen/InterMune, Clovis)
- 5 case law authorities (Omnicare, Matrixx, Tongue v. Sanofi,
  Harkonen, Clovis)
- 2 statutes (Securities Act § 11, FDAAA § 801)
- 2 regulations (Rule 408, Regulation S-K)
