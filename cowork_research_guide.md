# COWORK RESEARCH GUIDE
# S-1 Clinical Trial Disclosure Checker — Reference File Research

## CONTEXT FOR THE RESEARCHER

You are building reference files for a legal compliance tool. The tool 
checks whether biotech company S-1 registration statements (IPO filings) 
adequately disclose clinical trial information. It does this by comparing 
S-1 language to ClinicalTrials.gov data and applying SEC disclosure 
standards.

The reference files are JSON. They contain the legal standards, case law 
holdings, SEC comment letter excerpts, and examples that the tool pulls 
from directly during analysis. **The model does not reason about law from 
general knowledge — it reads these files and applies their content.** So 
these files must be accurate, complete, and well-sourced.

**Quality standard**: Every citation must be verifiable. Every URL must 
resolve. Every quote must be the actual language, not a paraphrase. If a 
source cannot be verified, mark it as UNVERIFIED and note why.

---

## DELIVERABLES OVERVIEW

You will produce 4 JSON files:

| File | What It Contains | Estimated Research Time |
|------|-----------------|----------------------|
| `legal_framework.json` | Statutes, case holdings, enforcement actions, comment letter citations | Heavy — the foundation |
| `check_descriptions.json` | Plain-English check descriptions, good/bad examples, methods | Medium — builds on legal_framework |
| `comment_letter_excerpts.json` | Actual SEC comment letter language, organized by topic | Heavy — requires EDGAR research |
| `guardrails.json` | Omnicare/Rule 408/Matrixx test procedures with calibration | Medium — builds on case research |

**Do them in this order.** Each builds on the previous.

---

# DELIVERABLE 1: legal_framework.json

This is the master legal reference file. Three sections: baseline rules, 
case law, and SEC comment letters.

## TASK 1A: Baseline Rules (Statutes & Regulations)

For each of the following, retrieve the **actual statutory/regulatory 
text** (the operative language, not a summary) and write a plain-English 
explanation:

### 1. Securities Act Section 11 — 15 U.S.C. § 77k

**Where to look**: https://www.law.cornell.edu/uscode/text/15/77k

**What to extract**:
- The exact text of § 11(a) — who is liable and for what
- The exact text of the "due diligence" defense in § 11(b)(3) — 
  what signers must prove to escape liability
- Note: § 11 is STRICT LIABILITY (no intent required) — verify this 
  from the text and confirm with a secondary source

**Output format**:
```json
{
  "id": "section_11",
  "name": "Securities Act Section 11",
  "citation": "15 U.S.C. § 77k",
  "url": "https://www.law.cornell.edu/uscode/text/15/77k",
  "operative_text": "[exact text of § 11(a)]",
  "due_diligence_defense_text": "[exact text of § 11(b)(3)]",
  "plain_english": "[your explanation — 2-3 sentences, no jargon]",
  "key_points": [
    "Strict liability — no need to prove intent or negligence",
    "Applies to every person who signed the registration statement",
    "Covers both affirmative misstatements AND omissions",
    "Due diligence defense requires 'reasonable investigation'"
  ],
  "who_is_liable": ["issuer (absolute liability)", "directors", "signing officers", "underwriters", "experts (for their portions)"],
  "verified": true
}
```

### 2. Rule 408 — 17 C.F.R. § 230.408

**Where to look**: https://www.law.cornell.edu/cfr/text/17/section-230.408

**What to extract**:
- The exact regulatory text
- Focus on the phrase "material information necessary to make the 
  required statements, in the light of the circumstances under which 
  they are made, not misleading"

**Why this matters for us**: Rule 408 is the basis for the "pattern 
of one-sided disclosure" analysis. Even if every individual statement 
in the S-1 is true, Rule 408 says you must add whatever ELSE is needed 
to prevent the total picture from misleading. This is how we catch the 
case where a company discloses good news but omits bad news.

**Output format**: Same structure as above.

### 3. Rule 10b-5 — 17 C.F.R. § 240.10b-5

**Where to look**: https://www.law.cornell.edu/cfr/text/17/section-240.10b-5

**What to extract**: 
- The exact text of subsections (a), (b), and (c)
- (b) is the most relevant: "To make any untrue statement of a material 
  fact or to omit to state a material fact necessary in order to make 
  the statements made, in the light of the circumstances under which 
  they were made, not misleading"

**Output format**: Same structure.

### 4. FDAAA 801 — 42 U.S.C. § 282(j)

**Where to look**: https://www.law.cornell.edu/uscode/text/42/282

**What to extract**:
- The results reporting requirement: sponsors of "applicable clinical 
  trials" must submit results to ClinicalTrials.gov
- The timeline: generally within 12 months of primary completion date
- The penalty for non-compliance (civil monetary penalties)

**Why this matters for us**: When we find a completed trial with no 
results posted on ClinicalTrials.gov, FDAAA 801 is the authority for 
why that matters — it's not just a good practice, it's a federal 
requirement. And when results aren't posted, investors can't 
independently verify the S-1's claims about that trial.

**Output format**: Same structure, add field:
```json
"relevance_to_tool": "When a completed trial has no posted results on CTgov, the tool flags this because: (1) it may indicate non-compliance with FDAAA 801, and (2) investors cannot independently verify S-1 claims about the trial"
```

---

## TASK 1B: Supreme Court & Circuit Court Cases

For each case below, retrieve the **actual holding** (from the opinion 
itself, not a summary), the **key quotes** that we use in our analysis, 
and the **factual context** so we can explain to a non-lawyer why the 
case matters.

### 1. Omnicare, Inc. v. Laborers District Council, 575 U.S. 175 (2015)

**Where to look**: 
- Full opinion: https://supreme.justia.com/cases/federal/us/575/175/
- Also check: https://www.supremecourt.gov/opinions/14pdf/13-435_0971.pdf

**What to extract**:

**A. The three-part test for opinion liability under § 11.**
The Court identified THREE ways an opinion statement can be actionable:

1. **Embedded fact test**: "A reasonable investor may, depending on the 
   circumstances, understand an opinion statement to convey facts about 
   how the speaker has formed the opinion—or, otherwise put, about the 
   speaker's basis for holding that view." Find the EXACT QUOTE.

2. **Omitted contrary facts test**: "[If] the real facts are otherwise, 
   but not combatting the opinion's import." The key language is about 
   omitting facts "about the inquiry the issuer did or did not conduct 
   or the knowledge it did or did not have." Find the EXACT QUOTE.

3. **Inquiry basis test**: The opinion may mislead "not because it 
   states a material fact, but because it implies one—that the speaker 
   actually did some meaningful...inquiry before offering the opinion." 
   Find the EXACT QUOTE.

**B. The factual context.** What was Omnicare? (a pharmacy services 
company). What opinions were at issue? (compliance with legal 
requirements). What did the Court hold?

**C. Key limiting language.** The Court also said "a reasonable investor 
does not expect that every opinion included in a registration statement 
is accurate" and that opinions inherently involve judgment. Find this 
language — it's important for CALIBRATION. Our tool must not over-apply 
Omnicare.

**Output format**:
```json
{
  "id": "omnicare",
  "name": "Omnicare, Inc. v. Laborers District Council",
  "citation": "575 U.S. 175 (2015)",
  "url": "https://supreme.justia.com/cases/federal/us/575/175/",
  "opinion_url": "https://www.supremecourt.gov/opinions/14pdf/13-435_0971.pdf",
  "facts_summary": "[2-3 sentences on what happened]",
  "holding": "[1-2 sentence holding]",
  "three_part_test": {
    "test_1_embedded_fact": {
      "description": "[plain English]",
      "exact_quote": "[verbatim from opinion]",
      "page_in_opinion": "[slip op. page number]",
      "example_in_our_context": "When the S-1 says 'the drug was well-tolerated,' this embeds the factual claim that the company's clinical data supports the characterization. If the data shows a 50% adverse event rate, the embedded fact may be untrue."
    },
    "test_2_omitted_contrary_facts": {
      "description": "[plain English]",
      "exact_quote": "[verbatim from opinion]",
      "page_in_opinion": "[slip op. page number]",
      "example_in_our_context": "The company says 'we believe we have aligned with the FDA' but omits the fact that the FDA denied their Breakthrough Therapy Designation application."
    },
    "test_3_inquiry_basis": {
      "description": "[plain English]",
      "exact_quote": "[verbatim from opinion]",
      "page_in_opinion": "[slip op. page number]",
      "example_in_our_context": "'Demonstrated clinical activity' implies a controlled evaluation was conducted. If the trial was open-label, single-arm, and uncontrolled, the implied basis is stronger than the actual inquiry."
    }
  },
  "limiting_language": {
    "exact_quote": "[the Court's language about not every opinion being accurate]",
    "calibration_implication": "The tool should not treat every opinion in the S-1 as suspect. Only opinions where the three-part test is met — where the company knew specific contrary facts — should be flagged."
  },
  "verified": true
}
```

### 2. Matrixx Initiatives, Inc. v. Siracusano, 563 U.S. 27 (2011)

**Where to look**: https://supreme.justia.com/cases/federal/us/563/27/

**What to extract**:

**A. The holding on statistical significance.** The key quote rejects 
a bright-line test: find the exact language where the Court says 
statistical significance is not required for materiality.

**B. What the Court said materiality IS** (referencing TSC Industries): 
"a substantial likelihood that the disclosure of the omitted fact would 
have been viewed by the reasonable investor as having significantly 
altered the 'total mix' of information made available."

**C. The factual context.** Matrixx was a pharmaceutical company that 
received adverse event reports about its cold remedy (Zicam) potentially 
causing loss of smell (anosmia). The company argued these reports were 
immaterial because they hadn't reached "statistical significance." 
The Court rejected this defense.

**D. Key quote for our context**: Something to the effect that 
"medical researchers...do not limit the data they consider...to 
statistically significant data" and that "medical professionals and 
regulatory agencies do not limit the data they consider to the results 
of randomized clinical trials or to statistically significant evidence."

**Output format**: Similar to Omnicare. Include:
```json
{
  "relevance_to_our_tool": "When biotech S-1s present data from small trials (N=12, N=19), the results may not reach statistical significance. Under Matrixx, this does not make them immaterial. A 50% adverse event rate in 12 patients, or a null primary endpoint in 20 patients, is information a reasonable investor would want to know.",
  "common_company_defense_this_rejects": "The company may argue that small trial results or individual adverse events are 'not statistically significant' and therefore immaterial. Matrixx forecloses this argument."
}
```

### 3. TSC Industries, Inc. v. Northway, Inc., 426 U.S. 438 (1976)

**Where to look**: https://supreme.justia.com/cases/federal/us/426/438/

**What to extract**: The definition of materiality. This is the 
foundational case. The exact quote is something like: "An omitted fact 
is material if there is a substantial likelihood that a reasonable 
shareholder would consider it important in deciding how to vote."

Also find the Court's distinction: "It does not require proof of a 
substantial likelihood that disclosure...would have caused the 
reasonable investor to change his vote [or investment decision]."

This distinction is critical: the test is NOT "would this have changed 
the decision" — it's "would a reasonable investor have wanted to know."

**Output format**: Same structure.

### 4. Tongue v. Sanofi, 816 F.3d 199 (2d Cir. 2016)

**Where to look**: https://casetext.com/case/tongue-v-sanofi-2
Also try: Westlaw/Google Scholar for the opinion

**What to extract**:

**A. Holding on FDA feedback disclosure.** The Second Circuit addressed 
when companies must disclose FDA communications in securities filings.

**B. The factual context.** Sanofi had FDA feedback about its drug 
candidate (I believe related to diabetes drug lixisenatide / Adlyxin). 
What did the FDA say? What did Sanofi not disclose?

**C. The standard.** Under what circumstances does FDA feedback become 
a material fact requiring disclosure?

**NOTE**: This case is particularly important for our "FDA Communications" 
check. We need the actual standard the court applied, not just a general 
description.

### 5. In re Rigel Pharmaceuticals Securities Litigation, 697 F.3d 869 (9th Cir. 2012)

**Where to look**: https://casetext.com/case/in-re-rigel-pharms-inc-sec-litig

**What to extract**: The holding on partial disclosure of clinical trial 
results and the obligation to disclose the full picture. Particularly 
relevant for our "interim/topline" check.

---

## TASK 1C: Enforcement Precedents — Deep Research

For each enforcement action below, we need MORE than what's in the 
litigation release. We need the **actual facts**, the **specific 
language** that was problematic, and the **lesson** stated concretely 
enough that the tool can compare new S-1 language to it.

### 1. SEC v. Clovis Oncology (LR-24273)

**Where to look**: 
- Litigation release: https://www.sec.gov/litigation/litreleases/2018/lr24273.htm
- Complaint: Search for the SEC complaint on EDGAR or SEC.gov
- Press release / news coverage for additional context

**What to extract**:

A. **The specific language that was fraudulent.** Clovis reported a 
   60% ORR. What EXACTLY did they say? In what filing? Get the actual 
   quote if possible.

B. **What the real number was.** Confirmed ORR was 28%. Explain in 
   plain English the difference between confirmed and unconfirmed 
   responses and why it matters.

C. **What the SEC said they should have done.** Disclose that they 
   were using unconfirmed responses, which is not the standard metric 
   the FDA uses.

D. **The penalty.** $20M civil penalty. Also any individual penalties.

E. **The lesson for our tool, stated as a concrete rule:**
   "When the S-1 presents an efficacy metric (ORR, response rate, etc.), 
   check whether the metric definition matches the standard FDA definition. 
   If the S-1 uses a non-standard metric (unconfirmed responses, non-ITT 
   population, per-protocol instead of intent-to-treat), this must be 
   disclosed."

**Output format**:
```json
{
  "id": "clovis",
  "name": "SEC v. Clovis Oncology, Inc.",
  "citation": "SEC Litigation Release No. 24273 (2018)",
  "lit_release_url": "https://www.sec.gov/litigation/litreleases/2018/lr24273.htm",
  "complaint_url": "[URL if found]",
  "facts": {
    "company": "Clovis Oncology",
    "drug": "rociletinib",
    "what_they_said": "[exact quote or close paraphrase from complaint]",
    "what_was_true": "Confirmed ORR was approximately 28%, not 60%",
    "why_it_was_wrong": "Clovis counted unconfirmed tumor responses (tumor shrinkage on a single scan) as 'responses.' The FDA standard (RECIST) requires confirmation on a subsequent scan. Unconfirmed responses frequently do not hold up.",
    "where_it_was_said": "[10-K, 8-K, press release — specify]"
  },
  "penalty": "$20 million civil penalty",
  "individual_consequences": "[any individual liability/penalties]",
  "rule_for_our_tool": "When the S-1 presents efficacy metrics: (1) Does it define the metric? (2) Does the definition match FDA standards? (3) If using a non-standard metric (unconfirmed, per-protocol, subgroup), is this disclosed?",
  "verified": true
}
```

### 2. United States v. Harkonen (InterMune)

**Where to look**:
- 9th Circuit opinion: https://casetext.com/case/united-states-v-harkonen-5
- District court proceedings
- News coverage (this was a major case — WSJ, Bloomberg covered it)

**What to extract**:

A. **The press release language.** InterMune's CEO issued a press 
   release about the GIPF-001 trial (Actimmune for IPF). What EXACTLY 
   did the press release say? Get the actual headline and key sentences.

B. **The trial facts.** 
   - What was the primary endpoint? (Progression-free survival, I believe)
   - What was the primary endpoint result? (p=0.52 — failed)
   - What was the post-hoc subgroup? (Patients with mild-to-moderate IPF)
   - What was the subgroup result? (p=0.004 — appeared significant)
   - Was the subgroup pre-specified? (No — it was post-hoc)

C. **What made it criminal.** The press release led with the subgroup 
   result and did not clearly identify it as post-hoc. The primary 
   endpoint failure was mentioned but buried. The jury found this 
   constituted wire fraud.

D. **The lesson, stated as a concrete rule:**
   "When the S-1 presents efficacy results, check: (1) Is the 
   highlighted result from the primary endpoint or from a secondary/ 
   exploratory/post-hoc analysis? (2) If from a secondary or post-hoc 
   analysis, is the primary endpoint result ALSO prominently disclosed? 
   (3) Is the hierarchy (primary vs secondary vs post-hoc) clearly 
   stated? Leading with a secondary/post-hoc success while burying a 
   primary failure is the Harkonen pattern."

**NOTE**: This is the MOST IMPORTANT enforcement precedent for our tool. 
The AARD test case found exactly this pattern (leading with a secondary 
endpoint while omitting that the primary was safety). We need the Harkonen 
facts nailed down precisely.

### 3. SEC v. AVEO Pharmaceuticals (LR-24062)

**Where to look**: 
- Litigation release: https://www.sec.gov/litigation/litreleases/2018/lr24062.htm
- Search for SEC complaint

**What to extract**:

A. **What FDA communication was omitted.** The FDA recommended an 
   additional clinical trial. AVEO didn't disclose this.

B. **What AVEO DID disclose** about FDA interactions (the positive side).

C. **The asymmetry.** Disclosing positive FDA interactions while 
   omitting the recommendation for an additional trial.

D. **The lesson**: "Selective disclosure of FDA communications is 
   actionable. If the S-1 describes any FDA interaction (alignment, 
   positive feedback, designation), ALL material FDA interactions must 
   be disclosed, including concerns, requests, and negative decisions."

---

## TASK 1D: SEC Comment Letters — The Core Research Task

This is the most labor-intensive task. We have 7 comment letter URLs 
from our spec. For each one, we need to:

1. **Verify the URL resolves** and identify the company
2. **Read the full comment letter**
3. **Extract the specific SEC comments** about clinical trial disclosure
4. **Find the S-1/A response** (the company's amendment) if available
5. **Record the exact SEC language** and what the company was asked to do

Additionally, we need to **find MORE comment letters** on each topic 
to build a stronger reference base. The goal is 3-5 letters per topic.

### How to find SEC comment letters on EDGAR:

EDGAR full-text search: https://efts.sec.gov/LATEST/search-index?q=%22well-tolerated%22&dateRange=custom&startdt=2020-01-01&enddt=2026-01-01&forms=CORRESP

The SEC's comment letters and company responses are filed as form 
type "CORRESP" (correspondence) or "UPLOAD" on EDGAR. You can also 
find them in the filing index pages.

Alternative approach: Go to a company's EDGAR page, look at filings 
around the S-1 date, and find CORRESP filings nearby.

### Topic 1: Safety Characterizations ("well-tolerated," safety adjectives)

**Starting URL**: https://www.sec.gov/Archives/edgar/data/1157601/000119312523295310/filename1.htm

**What to look for in this letter and others**:
- SEC asking company to "remove" or "revise" characterizations like 
  "well-tolerated" or "favorable safety profile"
- SEC stating that "safety and efficacy determinations are within 
  the authority of the FDA"
- SEC asking for specific AE data (types, rates, severity) to 
  replace adjectives

**Search queries to find more letters**:
- EDGAR CORRESP search: "well-tolerated" + "safety" + "revise"
- EDGAR CORRESP search: "favorable safety profile" + "remove"
- EDGAR CORRESP search: "safety determinations" + "FDA's authority"

**Goal**: Find 3-5 comment letters where the SEC challenged safety 
characterizations. For each, record:

```json
{
  "id": "cl_safety_001",
  "topic": "safety_characterizations",
  "company": "[company name]",
  "company_cik": "[CIK]",
  "filing_type": "S-1",
  "letter_date": "[date]",
  "letter_url": "[EDGAR URL]",
  "sec_comment_text": "[EXACT text of the SEC's comment — copy verbatim]",
  "s1_language_challenged": "[EXACT language from the S-1 that the SEC was responding to, if identifiable from the letter]",
  "what_sec_asked_company_to_do": "[e.g., 'Remove the term well-tolerated or replace with specific AE data']",
  "company_response_url": "[URL to the response letter, if found]",
  "company_response_summary": "[What did the company do? Removed language? Added data? Argued back?]",
  "verified": true
}
```

### Topic 2: Phase Nomenclature ("Phase 1/2" combined labels)

**Starting URL**: https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm

**What to look for**:
- SEC asking company to explain what each portion of a combined-phase 
  trial involves
- SEC challenging pipeline graphics that show combined phase bars
- SEC asking for transition criteria between phase portions

**Search queries**:
- EDGAR CORRESP search: "Phase 1/2" + "explain" + "trial design"
- EDGAR CORRESP search: "combined" + "phase" + "clarify"

**Goal**: 3-5 letters. Same output format.

### Topic 3: Preclinical Claims

**Starting URL**: https://www.sec.gov/Archives/edgar/data/2025942/000149315224032474/filename1.htm

**What to look for**:
- SEC asking company to remove inferences of safety or efficacy 
  from animal data
- SEC asking for translation risk caveats
- SEC challenging MoA descriptions that imply established clinical fact

**Search queries**:
- EDGAR CORRESP search: "preclinical" + "animal" + "safety" + "revise"
- EDGAR CORRESP search: "mechanism of action" + "clinical evidence"
- EDGAR CORRESP search: "animal studies" + "predictive"

**Goal**: 3-5 letters.

### Topic 4: Comparative Claims

**Starting URL**: https://www.sec.gov/Archives/edgar/data/1953926/000110465924062094/filename1.htm

**What to look for**:
- SEC asking company to remove comparisons to approved products
- SEC challenging "differentiated," "best-in-class," "superior" language
- SEC asking for head-to-head data to support comparisons

**Search queries**:
- EDGAR CORRESP search: "differentiated" + "comparison" + "head-to-head"
- EDGAR CORRESP search: "superior" + "approved" + "remove"
- EDGAR CORRESP search: "cross-trial" + "comparison" + "limitations"

**Goal**: 3-5 letters.

### Topic 5: FDA Communications

**Starting URL**: https://www.sec.gov/Archives/edgar/data/1829802/000095012320012832/filename1.htm

**What to look for**:
- SEC asking for balanced disclosure of FDA interactions
- SEC challenging "positive feedback" language
- SEC asking company to disclose FDA concerns or negative decisions
- SEC asking what "alignment" specifically means

**Search queries**:
- EDGAR CORRESP search: "FDA" + "positive feedback" + "balanced"
- EDGAR CORRESP search: "FDA" + "alignment" + "concerns"
- EDGAR CORRESP search: "Breakthrough Therapy" + "denial" + "disclose"

**Goal**: 3-5 letters.

### Topic 6: Trial Design Disclosure

**Starting URL**: https://www.sec.gov/Archives/edgar/data/1842295/000095012324006958/filename1.htm

**What to look for**:
- SEC asking for trial design elements (randomization, blinding, 
  comparator, enrollment, endpoints)
- SEC asking for enrollment numbers
- SEC asking for endpoint definitions

**Search queries**:
- EDGAR CORRESP search: "randomization" + "blinding" + "disclose"
- EDGAR CORRESP search: "enrollment" + "number of patients" + "trial design"
- EDGAR CORRESP search: "primary endpoint" + "secondary endpoint" + "disclose"

**Goal**: 3-5 letters.

### Topic 7: Statistical Presentation & Powering

**Starting URL**: https://www.sec.gov/Archives/edgar/data/1841873/000119312521279491/filename1.htm

**What to look for**:
- SEC asking whether trial was powered for the endpoint discussed
- SEC challenging presentation of "statistically significant" results 
  without context
- SEC asking to distinguish pre-specified from post-hoc analyses

**Search queries**:
- EDGAR CORRESP search: "powered" + "statistical significance" + "trial"
- EDGAR CORRESP search: "post-hoc" + "pre-specified" + "disclose"
- EDGAR CORRESP search: "exploratory" + "endpoint" + "label"

**Goal**: 3-5 letters.

---

# DELIVERABLE 2: check_descriptions.json

This file describes each disclosure check in plain English, with 
examples. It builds on the legal_framework.json research.

For each of the 14 checks in our tool (7 S-1 cross-cutting + 4 trial-
level + 3 guardrail), produce:

```json
{
  "id": "[check_id]",
  "display_name": "[plain English name]",
  "plain_english": "[2-3 sentences: what are we checking and why]",
  "why_it_matters": "[1-2 sentences: why would an investor care]",
  "legal_basis": "[references to legal_framework.json entries by id]",
  "elements": [
    {
      "name": "[element name]",
      "standard": "[what the S-1 should contain]",
      "good_example": {
        "text": "[actual language from a well-drafted S-1 that satisfies this standard — FIND A REAL EXAMPLE if possible]",
        "source": "[company name, filing date, or note if fabricated]"
      },
      "bad_example": {
        "text": "[actual language from an S-1 that was challenged in a comment letter — from our comment_letter_excerpts research]",
        "source": "[company name, comment letter reference]"
      },
      "gray_area_example": {
        "text": "[language that is borderline — could go either way depending on context]",
        "explanation": "[why this is a gray area and what additional context matters]"
      },
      "how_system_checks": "[CODE: regex for X / LLM: assesses Y / BOTH: code pre-flags then LLM evaluates context]",
      "source_ids": ["[references to legal_framework.json comment letter ids]"]
    }
  ]
}
```

### Where to find good examples:

Look at S-1s from companies that did NOT receive comment letters 
(or whose comment letters had no clinical trial issues). These are 
likely well-drafted. Large-cap biotech IPOs that went smoothly often 
have good disclosure. Search EDGAR for recent S-1s from companies 
that went effective without extensive SEC comments.

### Where to find bad examples:

These come directly from your comment_letter_excerpts research. 
The comment letter identifies the problematic language.

### The 14 checks:

**Pass 1 (S-1 Cross-Cutting):**
1. Basic Disclosure (identity card)
2. Phase Labels (nomenclature)
3. Preclinical Framing
4. Comparative Claims
5. FDA Communications
6. Pipeline Accuracy
7. Red Flag Phrases

**Pass 2 (Trial-Level):**
8. Trial Design Comparison
9. Endpoints & Statistics
10. Safety Data Comparison
11. Data Maturity (interim/topline)

**Guardrails:**
12. Rule 408 Pattern Analysis
13. Omnicare Opinion Test
14. Matrixx Significance Check

---

# DELIVERABLE 3: comment_letter_excerpts.json

This is a compilation of all the comment letter research from Task 1D, 
organized for easy retrieval by topic. The tool will pull from this file 
when it needs to show the user "here's what the SEC said to another 
company about similar language."

**Structure**:
```json
{
  "excerpts": [
    {
      "id": "excerpt_001",
      "topic": "safety_characterizations",
      "check_ids": ["red_flag_phrases", "safety_comparison"],
      "company": "Company Name",
      "company_cik": "0001234567",
      "filing_type": "S-1",
      "letter_date": "2023-11-15",
      "letter_url": "https://www.sec.gov/Archives/edgar/data/...",
      "sec_comment_verbatim": "[EXACT text of SEC comment, copied verbatim from the letter]",
      "s1_language_challenged": "[EXACT language from the S-1 that triggered the comment, if identifiable]",
      "what_sec_required": "[What the company was asked to do: remove language, add data, revise, etc.]",
      "company_response_url": "[URL]",
      "what_company_did": "[Summary of how company responded]",
      "useful_for_comparison_because": "[Why this excerpt is useful for comparing to new S-1 language — what pattern does it illustrate]"
    }
  ]
}
```

**Goal**: At least 3 excerpts per topic (7 topics × 3 = minimum 21 
excerpts). More is better. 5 per topic is ideal (35 total).

**Quality criteria for excerpts**:
- The SEC comment must be **verbatim** — copy-paste from the letter
- The URL must **resolve** to the actual letter on EDGAR
- The company and filing context must be **identified**
- The "useful_for_comparison" field must explain **specifically** what 
  pattern this illustrates

---

# DELIVERABLE 4: guardrails.json

This file contains the three guardrail tests (Rule 408 pattern, 
Omnicare opinion test, Matrixx significance check) with step-by-step 
test procedures and calibration language.

```json
{
  "rule_408_pattern_test": {
    "legal_basis_id": "rule_408",
    "question": "Looking at ALL findings together, do the omissions and de-emphases consistently favor the company?",
    "procedure": [
      "Step 1: List every omission, gap, and de-emphasis identified in Pass 1 and Pass 2",
      "Step 2: For each, mark direction: FAVORS COMPANY / NEUTRAL / DISFAVORS COMPANY",
      "Step 3: If >75% of omissions favor the company, flag as PATTERN",
      "Step 4: Specifically check: (a) Are favorable results emphasized while unfavorable results are omitted? (b) Are positive characterizations in prominent sections (Summary, Business) while caveats are in Risk Factors? (c) Are design limitations (small N, open-label, single-arm) undisclosed?"
    ],
    "output_table_format": {
      "columns": ["#", "Finding", "Direction", "Pass/Check Source"],
      "example_row": ["1", "Primary endpoint not met (NCT05121441) — not discussed", "Favors company", "Pass 2 / Endpoints"]
    },
    "calibration": {
      "say_this": "The pattern of omissions raises questions under Rule 408 (17 C.F.R. § 230.408), which requires disclosure of information necessary to make other statements not misleading. Attorney review is recommended.",
      "not_this": "This filing is materially deficient under Rule 408.",
      "why": "Rule 408 pattern analysis requires holistic judgment about the 'total mix' of information. The tool can identify the pattern, but the ultimate legal assessment requires consideration of defenses, context, and materiality weighting that only an attorney can perform."
    }
  },

  "omnicare_opinion_test": {
    "legal_basis_id": "omnicare",
    "question": "For each opinion statement flagged in the analysis, does it raise questions under the Omnicare three-part test?",
    "procedure": [
      "Step 1: Identify all opinion statements flagged during analysis (safety characterizations, efficacy claims, regulatory characterizations)",
      "Step 2: For each, apply Test 1 (Embedded Fact): Does this opinion embed a factual claim? If so, is the embedded fact supported by the data?",
      "Step 3: For each, apply Test 2 (Omitted Contrary Facts): Does the company know facts that cut against the impression this opinion creates? List the specific contrary facts.",
      "Step 4: For each, apply Test 3 (Inquiry Basis): Does this opinion imply an inquiry or evaluation that is stronger than what actually occurred?",
      "Step 5: If any test is triggered, flag as RISK AREA with specific explanation"
    ],
    "output_table_format": {
      "columns": ["Statement", "Impression Created", "Test 1 (Embedded Fact)", "Test 2 (Contrary Facts)", "Test 3 (Inquiry Basis)", "Risk Level"],
      "color_coding": {
        "green": "No tests triggered — opinion appears supported",
        "yellow": "One test triggered — moderate risk, context may justify",
        "red": "Two or more tests triggered — significant risk area"
      }
    },
    "calibration": {
      "say_this": "This characterization raises questions under Omnicare, Inc. v. Laborers District Council, 575 U.S. 175 (2015), because [specific test triggered and why]. Attorney review is recommended.",
      "not_this": "This statement fails the Omnicare test. / This statement violates Omnicare.",
      "why": "Omnicare liability depends on what a 'reasonable investor' would understand and what the company 'knew' — determinations that require full factual investigation beyond what the tool can perform. The tool identifies RISK AREAS, not legal conclusions. Many S-1 opinion statements that trigger the three-part test may ultimately be defensible in context."
    },
    "important_limiting_principle": {
      "source": "Omnicare opinion, [page number from research]",
      "quote": "[The Court's language about not every opinion being accurate and opinions inherently involving judgment]",
      "implication": "Not every opinion in the S-1 that could theoretically be tested under Omnicare should be flagged. Only flag opinions where the tool has identified SPECIFIC contrary facts from the ClinicalTrials.gov data or from the S-1 itself that undermine the opinion."
    }
  },

  "matrixx_significance_check": {
    "legal_basis_id": "matrixx",
    "question": "Could any of the findings be dismissed on the grounds that the underlying data did not reach statistical significance?",
    "procedure": [
      "Step 1: Review all findings involving small trials (N<30), adverse events, or efficacy results",
      "Step 2: For each, note whether the S-1 or a potential defense could argue the finding is immaterial because it's 'not statistically significant'",
      "Step 3: If so, note that Matrixx Initiatives, 563 U.S. 27 (2011) rejected the bright-line statistical significance test for materiality",
      "Step 4: Apply the TSC Industries materiality test instead: would a reasonable investor consider this information important?"
    ],
    "calibration": {
      "say_this": "Under Matrixx Initiatives, Inc. v. Siracusano, 563 U.S. 27 (2011), the materiality of [finding] does not depend on statistical significance. A reasonable investor may consider [specific information] important regardless of sample size.",
      "not_this": "This is definitely material despite not being statistically significant."
    }
  }
}
```

---

# RESEARCH EXECUTION ORDER

Do these in sequence — each builds on the previous:

| Step | Task | Deliverable | Depends On |
|------|------|------------|------------|
| 1 | Baseline statutes (Task 1A) | legal_framework.json (partial) | Nothing |
| 2 | Supreme Court cases (Task 1B) | legal_framework.json (partial) | Nothing |
| 3 | Enforcement precedents (Task 1C) | legal_framework.json (partial) | Nothing |
| 4 | Comment letter research (Task 1D) | legal_framework.json (complete) + comment_letter_excerpts.json | Nothing, but slowest task |
| 5 | Check descriptions | check_descriptions.json | Steps 1-4 (needs examples) |
| 6 | Guardrails | guardrails.json | Steps 1-3 (needs case quotes) |

**Steps 1-3 can run in parallel.** Step 4 is the bottleneck.
Step 5 depends on all prior steps. Step 6 depends on steps 1-3.

---

# VERIFICATION CHECKLIST

Before declaring any deliverable complete, verify:

**For every URL**:
- [ ] URL resolves (returns 200, not 404)
- [ ] URL points to the correct document (not a different filing)
- [ ] If SEC.gov URL, test with User-Agent header 
      (SEC blocks requests without User-Agent)

**For every case citation**:
- [ ] Case name is correct (parties, not just one party)
- [ ] Reporter citation is correct (volume, reporter, page)
- [ ] Year is correct
- [ ] Holding matches the actual opinion (not a dissent or dictum)

**For every quote**:
- [ ] Quote is VERBATIM (not paraphrased)
- [ ] Quote is attributed to the correct source (majority opinion, 
      not dissent; SEC comment, not company response)
- [ ] Page/section reference is provided where possible

**For every comment letter excerpt**:
- [ ] Excerpt is from the SEC's comment, not the company's response
- [ ] Company is correctly identified
- [ ] Filing type is correctly identified (S-1 vs 10-K vs other)
- [ ] The S-1 language that triggered the comment is identified 
      where possible

**For every "plain English" explanation**:
- [ ] A non-lawyer could understand it
- [ ] It does not overstate or understate the legal standard
- [ ] It accurately reflects the holding/rule

---

# NOTES ON SOURCES

**Free case law sources (in order of preference)**:
1. Supreme Court website (for SCOTUS cases): https://www.supremecourt.gov/opinions
2. Justia: https://supreme.justia.com (SCOTUS) and https://law.justia.com (circuits)
3. Casetext: https://casetext.com (may require account but has good search)
4. Google Scholar: https://scholar.google.com (select "Case law")
5. CourtListener: https://www.courtlistener.com

**SEC sources**:
1. EDGAR full-text search: https://efts.sec.gov/LATEST/search-index
2. SEC litigation releases: https://www.sec.gov/litigation/litreleases
3. SEC complaints: Usually linked from litigation releases
4. EDGAR filing search: https://www.sec.gov/cgi-bin/browse-edgar

**Statutes & regulations**:
1. Cornell LII: https://www.law.cornell.edu
2. GovInfo: https://www.govinfo.gov

---

# OUTPUT FORMAT

Deliver each file as a single JSON file. Name them exactly:
- `legal_framework.json`
- `check_descriptions.json`  
- `comment_letter_excerpts.json`
- `guardrails.json`

If a field could not be verified, set `"verified": false` and add a 
`"verification_note"` explaining what couldn't be confirmed and why.

If a URL doesn't resolve, set `"url_verified": false` and include 
the URL you tried plus an alternative if found.

**Do NOT fabricate quotes or citations.** If you cannot find the 
exact language, say so. A gap is better than a wrong citation.
