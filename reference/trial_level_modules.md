# Trial-Level Modules (Pass 2)

These modules compare the S-1's trial descriptions against source data
from ClinicalTrials.gov. Each module specifies what to check and where
to find it in the CTgov JSON.

---

## Module 4: Trial Worksheet

**Purpose**: Verify the S-1 discloses key design elements and results
for each trial.

### CTgov JSON Field Paths

```
Design elements:
  Phase:           protocolSection.designModule.phases[]
  Allocation:      protocolSection.designModule.designInfo.allocation
  Masking:         protocolSection.designModule.designInfo.maskingInfo.masking
  Who masked:      protocolSection.designModule.designInfo.maskingInfo.whoMasked[]
  Model:           protocolSection.designModule.designInfo.interventionModel
  Enrollment:      protocolSection.designModule.enrollmentInfo.count
  Enrollment type: protocolSection.designModule.enrollmentInfo.type

Arms & interventions:
  Arms:            protocolSection.armsInterventionsModule.armGroups[]
    .label, .type, .description, .interventionNames[]
  Interventions:   protocolSection.armsInterventionsModule.interventions[]
    .type, .name, .description

Endpoints:
  Primary:         protocolSection.outcomesModule.primaryOutcomes[]
    .measure, .description, .timeFrame
  Secondary:       protocolSection.outcomesModule.secondaryOutcomes[]
    .measure, .description, .timeFrame

Status:
  Overall:         protocolSection.statusModule.overallStatus
  Start date:      protocolSection.statusModule.startDateStruct.date
  Completion:      protocolSection.statusModule.completionDateStruct.date

Results (if posted):
  Outcome measures: resultsSection.outcomeMeasuresModule.outcomeMeasures[]
    .type, .title, .description, .groups[], .classes[], .analyses[]
```

### Checklist (IF/THEN Rules)

**4.1 Design Element Presence**
For each of the following, check if the S-1 discloses it:

| Element         | CTgov Field                | IF absent in S-1        |
|-----------------|----------------------------|-------------------------|
| Phase           | design.phases              | FLAG                    |
| Randomization   | design.allocation          | FLAG if randomized      |
| Blinding        | design.masking             | FLAG if masked          |
| Control type    | arms.type (PLACEBO_*)      | FLAG                    |
| Enrollment (N)  | design.enrollment_count    | FLAG                    |
| Primary endpoint| primary_outcomes[].measure | FLAG (HIGH)             |
| Key secondary   | secondary_outcomes[]       | FLAG if results cited   |

**4.2 Endpoint Completeness**
For each primary endpoint in CTgov:
  → Is it discussed in the S-1?
  IF NOT → FLAG: "Primary endpoint not disclosed."

For each secondary endpoint cited in S-1 results:
  → Is it actually a secondary endpoint in CTgov, or primary?
  IF S-1 presents a secondary as primary → FLAG (HIGH): "Endpoint promotion."
  → Cite: United States v. Harkonen precedent.

**4.3 Failed Endpoint Disclosure**
IF a primary endpoint shows p > 0.05 in CTgov results:
  → Does the S-1 disclose this?
  IF NOT → FLAG (HIGH): "Undisclosed failed primary endpoint."

IF primary endpoint failed but S-1 leads with secondary endpoint success:
  → FLAG (HIGH): "S-1 leads with secondary success while omitting primary failure."
  → Cite Harkonen precedent.

**4.4 Status Consistency**
IF CTgov shows TERMINATED, WITHDRAWN, or SUSPENDED:
  → Does the S-1 disclose this status?
  IF NOT → FLAG (HIGH): "Undisclosed trial termination/withdrawal."

### Authority

SEC comment letter (enrollment, design, endpoints, protocols):
https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm

SEC comment letter (definitions for response categories):
https://www.sec.gov/Archives/edgar/data/1778016/000095012319008796/filename1.htm

SEC comment letter (disclosure that primary endpoint not met):
https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm

---

## Module 5: Statistics Check

**Purpose**: Verify statistical presentations are accurate and properly
contextualized.

### CTgov JSON Field Paths

```
Outcome analyses:
  resultsSection.outcomeMeasuresModule.outcomeMeasures[].analyses[]
    .groupIds[]           — which arms compared
    .groupDescription     — description of comparison
    .testedNonInferiority — boolean
    .nonInferiorityType
    .pValue               — reported p-value
    .statisticalMethod    — e.g., "ANCOVA", "Cochran-Mantel-Haenszel"
    .paramType            — e.g., "Odds Ratio", "Mean Difference"
    .paramValue           — effect size
    .ciPctValue           — CI percentage (e.g., 95)
    .ciNumSides           — ONE_SIDED or TWO_SIDED
    .ciLowerLimit
    .ciUpperLimit
    .dispersionType       — e.g., "STANDARD_ERROR_OF_MEAN"
    .dispersionValue
    .estimateComment

Outcome type:
  resultsSection.outcomeMeasuresModule.outcomeMeasures[].type
    — "PRIMARY" or "SECONDARY" or "OTHER_PRE_SPECIFIED" or "POST_HOC"
```

### Checklist (IF/THEN Rules)

**5.1 Pre-specified vs Post-hoc**
IF CTgov lists an outcome as "SECONDARY" or "POST_HOC":
  → Does the S-1 present it as if it were primary?
  IF YES → FLAG (HIGH): "Secondary/exploratory endpoint presented as primary."

IF CTgov lists an outcome as "OTHER_PRE_SPECIFIED" or "POST_HOC":
  → Does the S-1 label it as such?
  IF NOT → FLAG: "Post-hoc or exploratory analysis not labeled."

IF subgroup analysis is presented as a headline result:
  → FLAG (HIGH): Cite United States v. Harkonen.

**5.2 Powering**
IF the trial enrollment is small relative to the endpoint type:
  → Note whether the trial was likely powered for the cited endpoint.
  → IF S-1 implies statistical significance from an underpowered trial:
    FLAG: "Inferential presentation of underpowered data."

**5.3 Statistical Accuracy**
For each outcome measure with both S-1 citation and CTgov data:
  → Do p-values match?
  → Do confidence intervals match?
  → Do effect sizes match?
  IF mismatch → FLAG: "Statistical value mismatch between S-1 and source."

IF S-1 says "statistically significant" without providing p-value:
  → FLAG: "Significance claim without p-value."

**5.4 Descriptive vs Inferential**
IF the trial is Phase 1 or small Phase 2a (not powered for efficacy):
  → Does the S-1 present outcomes descriptively or inferentially?
  IF inferential (p-values, "significant", "demonstrated efficacy"):
    → FLAG: "Inferential presentation of exploratory data."

### Authority

SEC comment letter (significance and powering disclosure):
https://www.sec.gov/Archives/edgar/data/1841873/000119312521279491/filename1.htm

United States v. Harkonen (wire fraud for misleading subgroup framing):
https://law.justia.com/cases/federal/appellate-courts/ca9/11-10209/11-10209-2013-03-04.html

---

## Module 6: Safety Check

**Purpose**: Verify safety data is presented with actual data rather
than adjectives, and that serious adverse events are fully disclosed.

### CTgov JSON Field Paths

```
Adverse events overview:
  resultsSection.adverseEventsModule
    .frequencyThreshold    — minimum % for reporting "other" AEs
    .timeFrame             — period of AE collection
    .description

Event groups (arms):
  resultsSection.adverseEventsModule.eventGroups[]
    .id, .title, .description
    .deathsNumAffected, .deathsNumAtRisk
    .seriousNumAffected, .seriousNumAtRisk
    .otherNumAffected, .otherNumAtRisk

Serious adverse events:
  resultsSection.adverseEventsModule.seriousEvents[]
    .term                  — MedDRA preferred term
    .organSystem           — system organ class
    .sourceVocabulary      — e.g., "MedDRA 26.0"
    .assessmentType        — SYSTEMATIC_ASSESSMENT or NON_SYSTEMATIC
    .stats[]               — per group: .groupId, .numEvents, .numAffected, .numAtRisk

Other (non-serious) adverse events:
  resultsSection.adverseEventsModule.otherEvents[]
    (same structure as seriousEvents)
```

### Checklist (IF/THEN Rules)

**6.1 Adjective vs Data**
IF S-1 uses "well-tolerated", "acceptable safety profile", "favorable
safety profile", or similar safety adjective:
  → Is it followed (within 500 characters) by actual AE/SAE/discontinuation data?
  IF NOT → FLAG: "Safety adjective without supporting data."
  → Cite SEC comment letter requiring objective data instead of "favorable safety profile."

**6.2 SAE Completeness**
IF CTgov reports serious adverse events (seriousEvents[] is non-empty):

  **6.2a** Does the S-1 disclose SAEs with types and counts per arm?
    IF NOT → FLAG: "Serious adverse events not disclosed with specificity."

  **6.2b** For each SAE term in CTgov with numEvents > 0:
    → Is this SAE term mentioned in the S-1?
    IF NOT for the majority of SAE terms → FLAG: "SAEs underreported."

  **6.2c** IF S-1 says "no drug-related SAEs" but CTgov shows SAEs:
    → FLAG and note the distinction between sponsor assessment (relatedness)
    and investigator assessment. CTgov reports ALL SAEs regardless of
    relatedness determination.

**6.3 Safety Differential**
IF treatment arm SAE rate (seriousNumAffected/seriousNumAtRisk)
substantially exceeds control arm SAE rate:
  → Does the S-1 acknowledge this differential?
  IF NOT → FLAG: "Safety differential between arms not disclosed."

Compare:
  - Any AE rates (otherNumAffected/otherNumAtRisk)
  - SAE rates (seriousNumAffected/seriousNumAtRisk)
  - Death counts (deathsNumAffected/deathsNumAtRisk)
  - Discontinuation rates due to AE (if available)

**6.4 Terminology**
IF S-1 uses "TEAE" → Is it defined?
  IF NOT → FLAG: "TEAE used without definition."
IF S-1 uses "SAE" → Is it defined or is context clear?
  IF NOT → FLAG: "SAE used without definition."
IF S-1 conflates TEAE with SAE → FLAG: "TEAE/SAE conflation."

**6.5 Death Reporting**
IF CTgov reports any deaths (deathsNumAffected > 0 in any group):
  → Does the S-1 disclose deaths?
  IF NOT → FLAG (HIGH): "Deaths in clinical trial not disclosed."

### Authority

SEC comment letter: safety determinations are FDA's authority:
https://www.sec.gov/Archives/edgar/data/1157601/000119312523295310/filename1.htm

SEC comment letter requiring SAE descriptions and counts:
https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm

SEC comment letter requiring grade definitions and drug-related SAEs:
https://www.sec.gov/Archives/edgar/data/1778016/000095012319008796/filename1.htm

SEC comment letter requiring objective data instead of "favorable safety profile":
https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm

21 C.F.R. § 312.32 (SAE reporting framework):
https://www.ecfr.gov/current/title-21/chapter-I/subchapter-D/part-312/subpart-B/section-312.32

---

## Module 10: Interim/Topline Check

**Purpose**: Ensure interim or topline data is presented with appropriate
caveats about its preliminary nature.

### CTgov JSON Field Paths

```
Study status:
  protocolSection.statusModule.overallStatus
    — RECRUITING, ACTIVE_NOT_RECRUITING, COMPLETED, etc.

Results posting:
  hasResults                   — boolean
  resultsSection exists?       — if study completed but no results, they're pending

Last update:
  protocolSection.statusModule.lastUpdatePostDateStruct.date
```

### Checklist (IF/THEN Rules)

**10.1 Ongoing Trial Data**
IF S-1 describes data from a trial where CTgov status is NOT "COMPLETED":

  **10.1a** Does the S-1 state the data cutoff date?
    IF NOT → FLAG: "Data from ongoing trial without cutoff date."

  **10.1b** Does the S-1 identify the data as interim or preliminary?
    IF NOT → FLAG: "Data from ongoing trial not labeled as interim."

  **10.1c** Does the S-1 identify what remains (database lock, ongoing
  monitoring, additional enrollment)?
    IF NOT → FLAG: "Interim data without disclosure of remaining steps."

  **10.1d** Does the S-1 use conclusory adjectives ("positive," "successful,"
  "demonstrated") for interim data?
    IF YES → FLAG: "Conclusory language for preliminary data."

**10.2 Topline Results**
IF S-1 describes "topline" results:

  **10.2a** Does the S-1 note that full analysis may differ?
    IF NOT → FLAG: "Topline results without caveat about final analysis."

  **10.2b** Is there caution that the dataset is not final?
    IF NOT → FLAG: "Topline presentation without finality caveat."

**10.3 Data Vintage**
IF S-1 filing date is significantly after CTgov last update:
  → Consider whether more recent data may be available that the S-1
    should have incorporated.
  → Note this as context, not necessarily a flag.

### Authority

SEC comment letter cautioning against "positive" characterizations of limited data:
https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm

In re Rigel Pharmaceuticals (when partial disclosures can be misleading):
https://caselaw.findlaw.com/court/us-9th-circuit/1611287.html
