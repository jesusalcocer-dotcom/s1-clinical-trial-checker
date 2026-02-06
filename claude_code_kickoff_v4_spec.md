# CLAUDE CODE KICKOFF: V4 SPEC AND DOCS ONLY
# Copy-paste this entire block into Claude Code after navigating to the repo

Read these three files in this repo IN ORDER:

1. s1_checker_skill_spec_v4_instructions.md — the v4 architecture 
   (operationalized decision tree, Layer 1/Layer 2, pseudocode for 
   each check, escalation rules, sec-api.io integration)

2. v4_supplemental_instructions.md — everything from v3 that v4 must 
   carry forward (user-facing opening explanation, two missing checks, 
   exact output table formats, interaction behavior rules, calibration 
   rules, parser enhancements, report structure, v2→v4 behavior change 
   table, file sync checklist)

3. cowork_research_guide.md — research methodology for building 
   reference files (where to find comment letters, case law, how to 
   extract actual language, verification standards)

IMPORTANT: We are NOT implementing code yet. This session is SPEC 
AND DOCS ONLY. After you produce these documents, I will review and 
verify them. Implementation comes after verification.

## WHAT TO BUILD (in this order):

### Step 1: s1_checker_skill_spec_v4.md

FIRST: Review all existing files in the repo. Read:
- The reference/ directory (all JSON files, all .md files, all .txt files)
- The scripts/ directory (understand what's already built)
- The git log (understand what work was done in previous sessions)
- Any existing SKILL.md, README.md, and prior spec versions

THEN: Write the CLEAN, FINAL v4 specification by synthesizing the v4 
instructions, the supplemental instructions, and the EXISTING RESEARCH 
into one authoritative document. This is the single source of truth 
for the entire system.

It must include ALL of the following:

A. Attribution (Jesus Alcocer, Norm.ai)
B. "What is a Skill" explanation for non-technical users
C. Visual process flow (the 8-step diagram)
D. Code vs LLM table (what is mechanical, what is analytical)
E. Legal framework in plain English (three layers, with cases, 
   statutes, enforcement precedents, comment letter enforcement)
F. The Layer 1 → Layer 2 decision tree architecture diagram
G. ALL 11 operationalized checks as pseudocode with:
   - Exact inputs (what text to extract, what patterns to grep)
   - Concrete thresholds (when GREEN/YELLOW/RED)
   - LLM prompt templates with slots for {{S1_TEXT}}, 
     {{PRECEDENT_LANGUAGE}}, {{CTGOV_DATA}}
   - When LLM is called vs when code handles it alone
   Note: v4 instructions have checks 1-5, 7-10. Supplemental 
   has checks 6 (Pipeline) and 11 (Data Maturity). Include ALL 11.
H. Layer 2 escalation checks (Omnicare, Rule 408, Matrixx) with:
   - Trigger conditions (when do they fire)
   - LLM prompt templates with exact case language slots
   - Graduated output scale (not binary pass/fail)
I. Complete checklist preview table (14 items)
J. Interaction flow: what the user sees at every step
   - Opening explanation → ticker → confirm filing → select 
     candidate → Pass 1 with auto-flow → transition → CTgov 
     download → Pass 2 with auto-flow → guardrails → report
   - Table output format for every check (exact column structure)
   - Pause behavior (green=continue, yellow=offer detail, 
     red=research augmentation then offer detail)
K. Research augmentation protocol and output format
L. Calibration rules (all 5, with SAY/NOT examples)
M. s1_parser.py enhancements (page approximation, section mapping, 
   candidate disambiguation)
N. FDAAA 801 results posting sub-check
O. Aggregate report structure (.docx, 6 sections)
P. sec-api.io integration (API key, budget allocation, fallback)
Q. Reference file structure — describe the ACTUAL structure of 
   existing reference files (from prior research sessions), note 
   what updates are needed to support v4 operationalized checks 
   (e.g., adding comparison pairs, prompt template slots, missing 
   research). Include a "Reference File Gap Analysis" section.
R. v2→v4 behavior change table
S. Build order for implementation phase (for later)
T. Test case expectations (AARD, SLRN)

Do NOT just concatenate the two instruction files. Synthesize them 
into a coherent, well-organized spec that reads as one document. 
Resolve any conflicts between v4 and supplemental in favor of v4 
architecture (operationalized checks > vague standards).

Commit when done: "Add v4 specification"

### Step 2: Update README.md

Rewrite README.md to accurately describe the v4 system:

- What this tool does (1 paragraph)
- Who built it (Jesus Alcocer for Norm.ai assessment)
- Architecture overview (Layer 1 concrete checks → Layer 2 
  escalation, code vs LLM split)
- Legal framework summary (brief — point to spec for detail)
- File structure with descriptions of every file
- How to use it (it's a Claude skill — load via SKILL.md)
- Current status: "Specification complete. Implementation pending."
- Link to spec: "See s1_checker_skill_spec_v4.md for full details"

Commit: "Update README for v4"

### Step 3: Review and update SKILL.md

Read the current SKILL.md. Update it to:
- Reference v4 (not v2 or v3)
- Use the Layer 1 → Layer 2 architecture
- Remove any "module" language
- Add the calibration rules
- Add the interaction flow (opening explanation, auto-flow, 
  pause on findings)
- Reference the correct reference file names from v4

If the current SKILL.md is too far from v4 to patch, rewrite it.
But note: the SKILL.md is the ORCHESTRATOR PROMPT — it tells the 
LLM what to do at runtime. It should be concise and operational, 
pointing to the spec for rationale and to reference files for 
legal content. It is NOT a copy of the spec.

Commit: "Update SKILL.md for v4"

### Step 4: Verify consistency

Check that:
- SKILL.md references v4 spec
- README.md references v4 spec and SKILL.md
- No file uses the word "module" (use check names instead)
- No file says "MATERIALLY DEFICIENT" or "FAILS" or "EXPOSURE: HIGH"
- All reference file names mentioned in SKILL.md match what actually 
  exists in reference/
- The spec's description of reference file structure matches the 
  actual files that exist from prior research
- The spec clearly documents any gaps between existing reference 
  files and what v4 needs (the "Reference File Gap Analysis")
- Attribution appears in spec, README, and SKILL.md

Report any inconsistencies found.

Commit: "Verify v4 doc consistency" (if fixes needed)

## EXISTING RESEARCH

Claude Code already ran the research guide (cowork_research_guide.md) 
in a previous session. Reference files and research outputs already 
exist in this repo. Before writing the spec:

1. Read the reference/ directory — look at every file there
2. Read any JSON files that were built (legal_framework.json, 
   comment_letter_excerpts.json, guardrails.json, check_descriptions.json, 
   or whatever naming was used)
3. Read any research notes or output files from previous sessions
4. Check the git log to see what branches were merged and what 
   work was completed

The v4 spec MUST incorporate and reference this existing research:
- If reference files exist, the spec should describe their ACTUAL 
  structure (not a hypothetical schema)
- If case law was researched and actual quotes extracted, the spec 
  should reference those specific quotes
- If comment letter excerpts were found, the spec should reference 
  them by ID and include the actual URLs that were verified
- If any research was incomplete or URLs didn't verify, the spec 
  should note what gaps remain

Do NOT ignore existing work. Do NOT propose schemas that conflict 
with files that already exist. Build on what's there.

If the existing reference files need restructuring to match v4's 
operationalized architecture (e.g., adding comparison pairs, adding 
LLM prompt template slots), note what changes are needed in a 
"Reference File Updates Needed" section of the spec — but do NOT 
make those changes in this session.

## WHAT NOT TO DO

- Do NOT write or modify Python scripts (edgar_fetch.py, 
  s1_parser.py, ctgov_fetch.py, comparison_builder.py)
- Do NOT restructure or rewrite the reference JSON files — just 
  review them and note in the spec what updates are needed
- Do NOT run any analysis or test cases
- Do NOT delete the v4_instructions, supplemental, or research 
  guide files — they stay in the repo as development history

## AFTER THIS SESSION

After I review and approve the spec, README, and SKILL.md, we 
will do implementation in a subsequent session:
1. Reference file updates (restructure existing research to match 
   v4 operationalized architecture — add comparison pairs, prompt 
   templates, fill any research gaps)
2. Python scripts (parser enhancements, comparison builder updates)
3. End-to-end test with AARD
4. End-to-end test with SLRN
