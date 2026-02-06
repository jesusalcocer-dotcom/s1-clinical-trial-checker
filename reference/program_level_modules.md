# Program-Level Modules (Pass 1)

These modules analyze the S-1's presentation of each drug candidate
using only the S-1 text. No external data required.

---

## Module 2: Identity Card Check

**Purpose**: Verify the S-1 gives investors baseline context for each
drug candidate.

### Checklist (IF/THEN Rules)

**2.1 Indication + Clinical Context**
IF the candidate's passages do NOT contain a plain-English disease description:
  → FLAG: "Investors lack context for why this drug matters."
  → The S-1 should explain the disease, its prevalence, and unmet need.

**2.2 Modality**
IF the candidate's passages do NOT identify the drug modality
(small molecule, monoclonal antibody, antibody-drug conjugate, gene therapy,
cell therapy, peptide, etc.):
  → FLAG: "Investors don't know what the drug IS."

**2.3 Development Stage**
IF the candidate's development stage is not clearly stated:
  → FLAG: "Investors may assume more progress than exists."
IF the phase designation appears inflated relative to actual trial data:
  → FLAG and cross-reference with Module 3.

**2.4 No Approved Products Statement**
IF the company has no approved products AND the S-1 does not contain
"we have no approved products" or equivalent language:
  → FLAG: "SEC has specifically requested this disclosure."
  → Check: also look for "we have not generated any revenue from product sales"
    or "clinical-stage" as functional equivalents.

**2.5 Chronological Development History**
IF the S-1 narrative jumps between phases without a clear timeline:
  → FLAG: "Narrative may imply faster progression than occurred."
  → A clear preclinical → Phase 1 → Phase 2 → Phase 3 narrative helps
    investors understand the development trajectory.

### Authority

SEC comment letter requiring clinical-stage company identity card elements:
https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm

---

## Module 3: Phase Nomenclature Trap

**Purpose**: Flag combined phase labels that can mislead investors about
development progress.

### Checklist (IF/THEN Rules)

**3.1 Combined Label Detection**
IF the S-1 uses any of: "Phase 1/2", "Phase 2/3", "Phase 1/2a",
"Phase 2a/2b", "Phase 2b/3":

  **3.1a** Does the S-1 explain what the Phase 1 portion does?
    (e.g., dose escalation, MTD/RP2D determination)
    IF NOT → FLAG: "Combined label without Phase 1 explanation."

  **3.1b** Does the S-1 explain what the Phase 2 portion does?
    (e.g., dose expansion, efficacy-oriented endpoints)
    IF NOT → FLAG: "Combined label without Phase 2 explanation."

  **3.1c** Is the distinction tied to protocol structure
    (separate parts, different endpoints, different populations)?
    IF NOT → FLAG: "Combined label without structural explanation."

  **3.1d** Does the pipeline graphic reflect phases distinctly?
    IF pipeline is an image → NOTE: "Cannot verify pipeline graphic."
    IF pipeline is a table and shows combined bar → FLAG.

**3.2 What "Good" Looks Like**

Template for adequate combined phase disclosure:

> "We are conducting a Phase 1/2a trial. The Phase 1 portion is a
> dose-escalation study designed to determine the maximum tolerated dose
> and recommended Phase 2 dose (RP2D). The Phase 2a portion is a
> dose-expansion cohort designed to evaluate preliminary antitumor
> activity and additional safety and pharmacokinetic data at the RP2D."

### Authority

SEC comment letter challenging "Phase 1/2" and "Phase 2/3" labels:
https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm

---

## Module 7: Preclinical Framing

**Purpose**: Ensure preclinical data is presented with appropriate
translation risk caveats.

### Checklist (IF/THEN Rules)

**7.1 Preclinical Data Identification**
IF S-1 presents animal model results, in vitro data, or ex vivo data:

  **7.1a** Is the species/model identified?
    IF NOT → FLAG: "Preclinical data without species identification."

  **7.1b** Are endpoints stated?
    IF NOT → FLAG: "Preclinical results without endpoint disclosure."

  **7.1c** Is there a translation risk caveat?
    Look for: "may not be predictive of human outcomes",
    "preclinical results do not guarantee", "animal models may not
    reflect human disease", or equivalent.
    IF NOT → FLAG: "Preclinical data without translation risk caveat."

  **7.1d** Are preclinical results presented as demonstrating clinical efficacy?
    IF YES → FLAG (HIGH): "Preclinical data cannot demonstrate clinical efficacy.
    This is the core prohibition."

**7.2 Mechanism of Action Framing**
IF MoA is described:

  Is it framed as hypothesis/design intent ("designed to," "intended to",
  "believed to") or as established fact?
  IF framed as fact → Is there clinical evidence cited?
    IF NO clinical evidence → FLAG: "MoA stated as fact without clinical support."

### Authority

SEC comment letter requiring removal of safety/efficacy inferences from animal data:
https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm

---

## Module 8: Comparative Claims

**Purpose**: Flag comparative statements that lack adequate evidential basis.

### Checklist (IF/THEN Rules)

**8.1 Comparative Language Detection**
IF the S-1 contains any of: "safer", "more effective", "superior to",
"better than", "differentiated", "best-in-class", "first-in-class",
"improved over", "advantage over", "compared favorably":

  **8.1a** Is there head-to-head clinical data cited?
    (Same trial, same population, randomized comparison)
    IF YES → ACCEPTABLE if data supports the claim.
    IF NO → Continue to 8.1b.

  **8.1b** Is this cross-trial inference?
    (Different trials, different populations, different endpoints,
    different timepoints)
    IF YES → Does the S-1 acknowledge the limitations?
      IF NOT → FLAG: "Cross-trial comparison without acknowledged limitations."

  **8.1c** IF "safer" or "more effective" used for an unapproved candidate:
    → FLAG (HIGH): "Safety and efficacy determinations are FDA's authority.
    An unapproved drug cannot be described as 'safe' or 'effective.'"

**8.2 "Differentiated" Claims**
IF "differentiated" is used:
  → What is the basis? Mechanism, clinical data, or speculation?
  → IF mechanism only → FLAG: "Differentiation claim based on mechanism
    without clinical evidence."

### Authority

SEC comment letter requiring removal of "safer"/"more effective" claims:
https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm

SEC comment letter requiring removal of comparisons without head-to-head support:
https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm

---

## Module 9: FDA Communications

**Purpose**: Ensure FDA interactions are characterized in a balanced way.

### Checklist (IF/THEN Rules)

**9.1 Positive Feedback Language**
IF S-1 uses "positive feedback", "constructive feedback", "alignment",
"FDA agreed", "FDA indicated", "FDA acknowledged":

  **9.1a** Does the S-1 balance it with any FDA concerns or recommendations?
    IF NOT → FLAG: "One-sided characterization of FDA interaction."

  **9.1b** Does the language imply approval is assured or likely?
    IF YES → FLAG (HIGH): "FDA feedback does not indicate approval likelihood."

**9.2 FDA Designation Disclosure**
IF S-1 mentions Breakthrough Therapy, Fast Track, Orphan Drug, Priority Review,
or Accelerated Approval:

  **9.2a** Does the S-1 clarify the designation does not guarantee approval?
    IF NOT → FLAG: "FDA designation without approval caveat."

  **9.2b** Does the S-1 disclose material FDA communications in connection
  with the designation?
    IF NOT → FLAG: "Incomplete designation disclosure."

**9.3 Omission of FDA Concerns**
IF the comparison reveals FDA interactions that the S-1 characterizes
one-sidedly:
  → FLAG and cite the AVEO enforcement action for the principle that
    selective disclosure of FDA communications is actionable.

### Authority

SEC comment letter challenging "positive FDA feedback" language:
https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm

AVEO enforcement action (omission of FDA recommendation):
https://www.sec.gov/enforcement-litigation/litigation-releases/lr-24062

---

## Module 11: Pipeline QC

**Purpose**: Verify pipeline table/graphic accuracy.

### Checklist (IF/THEN Rules)

**11.1 Phase Consistency**
IF pipeline table shows phases for candidates:
  → Do phases match the text descriptions?
  IF mismatch → FLAG: "Pipeline table phase does not match narrative."

**11.2 IND Status**
IF pipeline shows a candidate in clinical phases (Phase 1+):
  → Has an IND been filed/cleared for that candidate?
  IF no IND mentioned → FLAG: "Pipeline shows clinical phase without IND disclosure."

**11.3 Progress Overstatement**
IF pipeline uses arrows or bars:
  → Do they extend beyond the candidate's actual progress?
  IF YES → FLAG: "Pipeline graphic overstates development progress."

**11.4 Platform vs Product**
IF pipeline lists platforms or technologies as product candidates:
  → FLAG: "Platforms are not product candidates."

**11.5 Image Limitation**
IF pipeline is embedded as an image (JPG, PNG, etc.):
  → NOTE: "Pipeline is an image — cannot parse or verify programmatically.
    Manual review recommended."

### Authority

SEC comment letter challenging pipeline phase signaling without IND:
https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm

SEC comment letter requiring pipeline tables to show phases distinctly:
https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm

---

## Module 12: Red Flag Phrase Scan

**Purpose**: Identify language the SEC routinely challenges.

### Phrase List

Uses `reference/red_flag_phrases.txt` (machine-readable, one per line).

### Checklist (IF/THEN Rules)

For each phrase match in the candidate's passages:

**12.1 Context Check** — Do NOT auto-flag every instance. Check context:

  IF "safe" appears in a risk factor describing risk → ACCEPTABLE
  IF "effective" is preceded by "may not be" → ACCEPTABLE (cautionary)
  IF "well-tolerated" is followed by AE rates within 200 characters → ACCEPTABLE
  IF "well-tolerated" appears standalone without quantitative support → FLAG
  IF "clinically meaningful" is followed by specific data → ACCEPTABLE
  IF "clinically meaningful" appears without supporting data → FLAG

**12.2 Affirmative Use Test**
Only FLAG instances where the phrase is used AFFIRMATIVELY about the
candidate WITHOUT adequate qualification or data support.

**12.3 What to Report**
For each flagged instance:
  - The exact S-1 passage (with section and approximate page)
  - Why it was flagged (affirmative use without support)
  - The applicable authority

### Authority

SEC comment letter: safety determinations are FDA's authority:
https://www.sec.gov/Archives/edgar/data/1157601/000119312523295310/filename1.htm

SEC comment letter requiring removal of statements implying safety/efficacy:
https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm
