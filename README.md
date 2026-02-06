# S-1 Clinical Trial Disclosure Checker

**Built by Jesus Alcocer for Norm.ai**

A Claude Skill that checks whether biotech S-1 (or F-1) registration
statements adequately disclose clinical trial information by comparing
them against the public record on ClinicalTrials.gov.

## What It Does

Given a stock ticker, the tool:

1. **Downloads** the S-1 filing from SEC EDGAR
2. **Parses** the document to identify drug candidates and clinical
   trial references
3. **Runs 11 concrete checks** comparing S-1 text against SEC
   standards and ClinicalTrials.gov data
4. **Escalates** flagged items through legal precedent analysis
   (Omnicare, Matrixx, Rule 408)
5. **Produces** a structured report identifying risk areas for
   attorney review

## Architecture: Layer 1 / Layer 2

**Layer 1** (always runs): 11 operationalized checks with coded logic,
regex patterns, and targeted LLM assessment.

| # | Check | Pass | Source |
|---|-------|------|--------|
| 1 | Basic Disclosure | Pass 1 (S-1 only) | SEC comment letters |
| 2 | Phase Labels | Pass 1 | SEC comment letters |
| 3 | Preclinical Framing | Pass 1 | SEC comment letters |
| 4 | Comparative Claims | Pass 1 | SEC comment letters |
| 5 | FDA Communications | Pass 1 | AVEO, Tongue v. Sanofi |
| 6 | Pipeline Accuracy | Pass 1 | SEC comment letters |
| 7 | Red Flag Phrases | Pass 1 | SEC comment letters |
| 8 | Trial Design Match | Pass 2 (S-1 vs CTgov) | SEC comment letters |
| 9 | Endpoint Hierarchy | Pass 2 | Harkonen, Clovis |
| 10 | Safety Data Match | Pass 2 | SEC comment letters |
| 11 | Data Maturity | Pass 2 | Rigel, SEC letters |

**Layer 2** (escalation, only when Layer 1 flags issues):

- **Rule 408 Pattern**: Are omissions systematically one-sided?
- **Omnicare Test**: Do opinion statements omit known contrary facts?
- **Matrixx Check**: Defense-blocker for statistical significance arguments

## Legal Framework

Three layers of authority:

1. **Baseline Rules**: Securities Act Section 11, Rule 408, Rule 10b-5,
   FDAAA 801
2. **Supreme Court Standards**: Omnicare v. Laborers (2015), Matrixx v.
   Siracusano (2011), TSC Industries v. Northway (1976)
3. **Enforcement Precedents**: SEC v. Clovis Oncology, United States v.
   Harkonen, SEC v. AVEO Pharmaceuticals, Tongue v. Sanofi, In re Rigel

## Project Structure

```
s1-clinical-trial-checker/
├── SKILL.md                           # Orchestrator prompt (v4)
├── s1_checker_skill_spec_v4.md        # Full technical specification
├── README.md                          # This file
├── scripts/
│   ├── edgar_fetch.py                 # SEC EDGAR S-1 lookup + download
│   ├── s1_parser.py                   # S-1 HTML parsing + candidate ID
│   ├── ctgov_fetch.py                 # ClinicalTrials.gov API client
│   └── comparison_builder.py          # S-1 vs CTgov comparison engine
└── reference/
    ├── operationalized_checks.json    # All 11 checks: logic, patterns, prompts
    ├── legal_framework.json           # Statutes, case law, enforcement actions
    ├── comment_letter_excerpts.json   # Verbatim SEC comment letters by topic
    ├── guardrails.json                # Layer 2 escalation procedures
    ├── guardrails.md                  # Guardrails documentation
    ├── program_level_modules.md       # Pass 1 check details (legacy format)
    ├── trial_level_modules.md         # Pass 2 check details (legacy format)
    ├── check_descriptions.json        # Plain-English check descriptions
    └── red_flag_phrases.txt           # SEC-challenged phrase list
```

## Requirements

- Python >= 3.8
- `pip install requests beautifulsoup4 lxml`

## Usage

This is a Claude Skill. Load the project in Claude Code and provide a
pharma/biotech stock ticker:

```
Check AARD
```

The tool walks through the analysis interactively with gate-based
confirmation at each major step.

## Design Principles

- **Traceability**: Every finding cites exact S-1 text + legal authority
- **Auditability**: You can see what code did vs what LLM assessed
- **Calibration**: "Raises questions under" not "fails" or "violates"
- **Risk areas, not legal conclusions**: Identifies issues for attorney
  review; does not determine liability or materiality

## License

Proprietary. Built by Jesus Alcocer for Norm.ai.
