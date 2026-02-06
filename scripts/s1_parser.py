#!/usr/bin/env python3
"""
s1_parser.py — Parse S-1 HTML to extract drug candidates, study references,
passages, and flag patterns.

Usage:
    python scripts/s1_parser.py --action find_candidates --file s1_SLRN_2023-05-03.html
    python scripts/s1_parser.py --action extract_passages --file s1_SLRN_2023-05-03.html --nct NCT05355805
"""

import argparse
import json
import os
import re
import sys

from bs4 import BeautifulSoup, Comment

# ── Constants ─────────────────────────────────────────────────────────

KNOWN_SECTIONS = [
    "TABLE OF CONTENTS",
    "PROSPECTUS SUMMARY",
    "RISK FACTORS",
    "USE OF PROCEEDS",
    "DILUTION",
    "CAPITALIZATION",
    "BUSINESS",
    "MANAGEMENT'S DISCUSSION AND ANALYSIS",
    "MANAGEMENT",
    "EXECUTIVE COMPENSATION",
    "CERTAIN RELATIONSHIPS",
    "PRINCIPAL STOCKHOLDERS",
    "DESCRIPTION OF CAPITAL STOCK",
    "SHARES ELIGIBLE FOR FUTURE SALE",
    "MATERIAL U.S. FEDERAL INCOME TAX",
    "UNDERWRITING",
    "LEGAL MATTERS",
    "EXPERTS",
    "WHERE YOU CAN FIND MORE INFORMATION",
    "INDEX TO FINANCIAL STATEMENTS",
]

# INN suffixes for drug name detection (only specific pharmaceutical stems
# to avoid matching common English words)
INN_SUFFIXES = (
    "mab", "nib", "tinib", "ciclib", "lisib", "rafenib", "ertinib",
    "zomib", "parib", "bep", "tide", "gliptin", "parin",
    "lukast", "sartan", "pril", "olol", "afil", "glumide",
    "platin", "vudine", "navir", "tegravir", "previr",
    "cillin", "micin", "mycin",
)

# Common English words that happen to end with INN-like suffixes
INN_BLOCKLIST = {
    "increase", "decrease", "release", "disease", "purchase", "phase",
    "base", "case", "erase", "lease", "cease", "please", "grease",
    "crease", "concept", "accept", "receipt", "precept", "except",
    "intercept", "april", "gene", "cell", "prime", "combine",
    "determine", "examine", "undermine", "discipline", "medicine",
    "decline", "baseline", "outline", "define", "online", "vaccine",
    "routine", "doctrine", "pristine", "genuine", "famine",
    "sometime", "lifetime", "maritime", "overtime", "halftime",
    "peptide", "provide", "outside", "inside", "beside", "decide",
    "divide", "guide", "pride", "ride", "side", "slide", "stride",
    "tide", "wide", "worldwide", "nucleotide", "alongside",
    "override", "countryside", "suicide", "homicide", "coincide",
    "preside", "reside", "subside", "bromide", "chloride",
    "cyanide", "fluoride", "oxide", "sulfide",
    "member", "timber", "fiber", "chamber", "number", "remember",
    "october", "november", "december", "september",
}

# Internal designator pattern: 2-5 uppercase letters + hyphen + 3-5 digits
DESIGNATOR_RE = re.compile(r"\b[A-Z]{2,5}-\d{3,5}\b")

NCT_RE = re.compile(r"NCT\d{8}")

# Phase label patterns
PHASE_COMBINED_RE = re.compile(
    r"Phase\s+(\d[ab]?)\s*/\s*(\d[ab]?)", re.IGNORECASE
)
PHASE_ANY_RE = re.compile(
    r"Phase\s+(\d[ab]?(?:/\d[ab]?)?)", re.IGNORECASE
)

# Comparative language
COMPARATIVE_PATTERNS = [
    r"\bsafer\b", r"\bmore effective\b", r"\bsuperior\s+to\b",
    r"\bbetter\s+than\b", r"\bdifferentiated\b", r"\bbest-in-class\b",
    r"\bfirst-in-class\b", r"\bimproved\s+over\b",
    r"\badvantage\s+over\b", r"\bcompared\s+favorably\b",
]
COMPARATIVE_RE = re.compile("|".join(COMPARATIVE_PATTERNS), re.IGNORECASE)

# FDA language
FDA_PATTERNS = [
    r"\bpositive\s+feedback\b", r"\bconstructive\s+feedback\b",
    r"\balignment\b", r"\bFDA\s+agreed\b", r"\bFDA\s+indicated\b",
    r"\bFDA\s+acknowledged\b", r"\bBreakthrough\s+Therapy\b",
    r"\bFast\s+Track\b", r"\bOrphan\s+Drug\b", r"\bPriority\s+Review\b",
    r"\bAccelerated\s+Approval\b", r"\bpre-IND\b",
    r"\bEnd-of-Phase\s+2\b", r"\bSPA\b", r"\bCRL\b",
    r"\bIND\s+clear\w*\b", r"\bIND\s+approv\w*\b",
    r"\bIND\s+accept\w*\b", r"\bIND\s+fil\w*\b",
]
FDA_RE = re.compile("|".join(FDA_PATTERNS), re.IGNORECASE)

CHARS_PER_PAGE = 3000  # approximate

# Section classification for asymmetric placement analysis.
# Helps detect when positive language is in Business/Summary while
# caveats are buried in Risk Factors.
SECTION_CLASSES = {
    "PROSPECTUS SUMMARY": "summary",
    "RISK FACTORS": "risk_factors",
    "USE OF PROCEEDS": "other",
    "DILUTION": "other",
    "CAPITALIZATION": "other",
    "BUSINESS": "business",
    "MANAGEMENT'S DISCUSSION AND ANALYSIS": "mda",
    "MANAGEMENT": "other",
    "EXECUTIVE COMPENSATION": "other",
    "CERTAIN RELATIONSHIPS": "other",
    "PRINCIPAL STOCKHOLDERS": "other",
    "DESCRIPTION OF CAPITAL STOCK": "other",
    "SHARES ELIGIBLE FOR FUTURE SALE": "other",
    "MATERIAL U.S. FEDERAL INCOME TAX": "other",
    "UNDERWRITING": "other",
    "LEGAL MATTERS": "other",
    "EXPERTS": "other",
    "WHERE YOU CAN FIND MORE INFORMATION": "other",
    "INDEX TO FINANCIAL STATEMENTS": "financial",
    "TABLE OF CONTENTS": "other",
    "FULL DOCUMENT": "unknown",
}


def _classify_section(section_name: str) -> str:
    """Classify a section name into a high-level category.

    Returns one of: summary, risk_factors, business, mda, financial, other, unknown.
    Used for asymmetric placement analysis (Check 5: FDA Communications).
    """
    return SECTION_CLASSES.get(section_name, "unknown")


# ── HTML Parsing ──────────────────────────────────────────────────────

def _load_html(filepath: str) -> BeautifulSoup:
    """Load and parse S-1 HTML."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    # Strip non-content elements
    for tag in soup.find_all(["style", "script"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    return soup


def _extract_sections(soup: BeautifulSoup) -> list[dict]:
    """Break the document into sections based on anchor/bold headers.

    Returns list of {"name": str, "text": str, "char_offset": int}.
    """
    # Strategy: find all <a name="..."> inside <b>/<strong> tags,
    # or standalone <b>/<strong> with text matching known sections.
    sections = []
    full_text = soup.get_text(separator="\n", strip=True)

    # Find named anchors that are section headers
    anchors = soup.find_all("a", attrs={"name": True})
    section_markers = []  # (char_position_in_full_text, section_name)

    for anchor in anchors:
        parent = anchor.parent
        if not parent:
            continue
        # Check if parent is <b> or <strong>
        tag_name = parent.name if parent.name else ""
        if tag_name in ("b", "strong") or anchor.find_parent(["b", "strong"]):
            text = parent.get_text(strip=True)
        else:
            text = anchor.get_text(strip=True)
        if not text:
            continue

        # Normalize and check if it matches a known section
        text_upper = text.upper().strip()
        matched_section = None
        for known in KNOWN_SECTIONS:
            if known in text_upper or text_upper in known:
                matched_section = known
                break

        if matched_section:
            # Find position in full text
            pos = full_text.find(text.strip())
            if pos >= 0:
                section_markers.append((pos, matched_section))

    # Also search for bold text matching known sections (no anchor)
    for bold in soup.find_all(["b", "strong"]):
        text = bold.get_text(strip=True).upper()
        for known in KNOWN_SECTIONS:
            if known in text or text in known:
                pos = full_text.find(bold.get_text(strip=True))
                if pos >= 0:
                    # Avoid duplicates
                    if not any(abs(p - pos) < 100 for p, _ in section_markers):
                        section_markers.append((pos, known))
                break

    # Sort by position and de-duplicate
    section_markers.sort(key=lambda x: x[0])
    seen_names = set()
    deduped = []
    for pos, name in section_markers:
        key = name
        if key not in seen_names:
            deduped.append((pos, name))
            seen_names.add(key)
    section_markers = deduped

    # Build sections with text slices
    for i, (pos, name) in enumerate(section_markers):
        end = section_markers[i + 1][0] if i + 1 < len(section_markers) else len(full_text)
        sections.append({
            "name": name,
            "text": full_text[pos:end],
            "char_offset": pos,
        })

    # If no sections found, treat entire document as one section
    if not sections:
        sections.append({
            "name": "FULL DOCUMENT",
            "text": full_text,
            "char_offset": 0,
        })

    return sections


def _approx_page(char_offset: int) -> int:
    """Approximate page number from character offset."""
    return max(1, char_offset // CHARS_PER_PAGE + 1)


# ── Candidate Detection ──────────────────────────────────────────────

def _find_candidate_names(full_text: str) -> list[dict]:
    """Detect drug candidate names from text patterns.

    Returns list of {"name": str, "type": "inn"|"designator"}.
    """
    candidates = []
    seen = set()

    # 1. Internal designators (XX-1234 pattern)
    for m in DESIGNATOR_RE.finditer(full_text):
        name = m.group()
        if name not in seen:
            # Filter out common non-drug designators
            skip_prefixes = ("SEC-", "ASC-", "IRS-", "No-", "EX-",
                             "FY-", "DTC-")
            if not any(name.startswith(p) for p in skip_prefixes):
                seen.add(name)
                candidates.append({"name": name, "type": "designator"})

    # 2. INN-style names: look for words ending in INN suffixes that
    #    appear near candidate-indicating context and are not common words
    words = set(re.findall(r"\b[a-z]{5,}\b", full_text.lower()))
    candidate_context_re = re.compile(
        r"(?:candidate|product\s+candidate|investigational|our\s+lead"
        r"|our\s+pipeline|clinical\s+trial|development\s+candidate"
        r"|drug\s+candidate|therapeutic|antibody|inhibitor"
        r"|treatment\s+of|patients?\s+with)",
        re.IGNORECASE,
    )
    for word in words:
        if word in INN_BLOCKLIST:
            continue
        if any(word.endswith(suf) for suf in INN_SUFFIXES):
            if word not in seen:
                # Verify it appears near candidate context (within 300 chars)
                pattern = re.compile(
                    rf"\b{re.escape(word)}\b", re.IGNORECASE
                )
                for m in pattern.finditer(full_text):
                    start = max(0, m.start() - 300)
                    end = min(len(full_text), m.end() + 300)
                    context = full_text[start:end]
                    if candidate_context_re.search(context):
                        seen.add(word)
                        candidates.append({"name": word, "type": "inn"})
                        break

    return candidates


def _extract_passages_for_name(
    name: str, sections: list[dict], max_context: int = 800
) -> list[dict]:
    """Find all passages mentioning a name across sections."""
    passages = []
    pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
    for section in sections:
        text = section["text"]
        for m in pattern.finditer(text):
            # Extract surrounding context (paragraph-level)
            start = max(0, m.start() - max_context // 2)
            end = min(len(text), m.end() + max_context // 2)
            # Snap to sentence/paragraph boundaries
            snippet = text[start:end].strip()
            char_offset = section["char_offset"] + m.start()
            passages.append({
                "section": section["name"],
                "page_approx": _approx_page(char_offset),
                "text": snippet,
                "char_offset": char_offset,
            })
    # De-duplicate overlapping passages
    return _deduplicate_passages(passages)


def _deduplicate_passages(passages: list[dict]) -> list[dict]:
    """Remove passages that substantially overlap."""
    if not passages:
        return passages
    passages.sort(key=lambda p: p["char_offset"])
    result = [passages[0]]
    for p in passages[1:]:
        prev = result[-1]
        # If this passage starts within the previous one's text span, skip
        if p["char_offset"] < prev["char_offset"] + len(prev["text"]) - 100:
            # Keep the longer one
            if len(p["text"]) > len(prev["text"]):
                result[-1] = p
        else:
            result.append(p)
    return result


# ── Flag Detection ────────────────────────────────────────────────────

def _load_red_flag_phrases() -> list[str]:
    """Load red flag phrases from reference file."""
    ref_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "reference", "red_flag_phrases.txt",
    )
    if not os.path.exists(ref_path):
        # Default list if file doesn't exist yet
        return [
            "safe", "effective", "clinically validated", "clinically proven",
            "proven efficacy", "proven safety", "favorable clinical activity",
            "promising tolerability", "favorable safety profile",
            "acceptable safety profile", "well-tolerated", "safer than",
            "more effective than", "superior to", "best-in-class",
            "first-in-class", "fast-to-market", "accelerated commercialization",
            "positive FDA feedback", "clinically meaningful",
        ]
    with open(ref_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def _scan_red_flags(text: str) -> list[dict]:
    """Scan text for red flag phrases. Returns matches with context."""
    phrases = _load_red_flag_phrases()
    hits = []
    for phrase in phrases:
        pattern = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
        for m in pattern.finditer(text):
            start = max(0, m.start() - 150)
            end = min(len(text), m.end() + 150)
            hits.append({
                "phrase": phrase,
                "context": text[start:end].strip(),
                "position": m.start(),
            })
    return hits


def _scan_comparative(text: str) -> list[dict]:
    """Scan for comparative language."""
    hits = []
    for m in COMPARATIVE_RE.finditer(text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        hits.append({
            "phrase": m.group(),
            "context": text[start:end].strip(),
            "position": m.start(),
        })
    return hits


def _scan_fda_language(text: str) -> list[dict]:
    """Scan for FDA communication language."""
    hits = []
    for m in FDA_RE.finditer(text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        hits.append({
            "phrase": m.group(),
            "context": text[start:end].strip(),
            "position": m.start(),
        })
    return hits


def _scan_combined_phases(text: str) -> list[dict]:
    """Scan for combined phase labels."""
    hits = []
    for m in PHASE_COMBINED_RE.finditer(text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        hits.append({
            "label": m.group(),
            "phases": [m.group(1), m.group(2)],
            "context": text[start:end].strip(),
            "position": m.start(),
        })
    return hits


# ── Ownership Scoring ─────────────────────────────────────────────────

OWNERSHIP_RE = re.compile(
    r"(?:our\s+(?:lead|pipeline|product|candidate|program|drug)|"
    r"we\s+are\s+(?:developing|advancing|evaluating|conducting)|"
    r"we\s+initiated|we\s+plan\s+to|we\s+have\s+(?:developed|designed|initiated)|"
    r"our\s+proprietary|our\s+(?:first|second|third)\s+|"
    r"product\s+candidate)",
    re.IGNORECASE,
)

COMPETITOR_RE = re.compile(
    r"(?:approved\s+by\s+(?:the\s+)?FDA|FDA[\s-]+approved|approved\s+for|"
    r"commercially\s+available|currently\s+marketed|marketed\s+by|"
    r"sold\s+under|competing\s+product|competitor|"
    r"is\s+(?:an?\s+)?(?:approved|marketed)|only\s+(?:approved|FDA))",
    re.IGNORECASE,
)


def _score_ownership(name: str, full_text: str) -> float:
    """Score 0-1 how likely this is the company's OWN candidate vs a comparator."""
    pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
    own_hits = 0
    comp_hits = 0
    total = 0
    for m in pattern.finditer(full_text):
        total += 1
        start = max(0, m.start() - 200)
        end = min(len(full_text), m.end() + 200)
        context = full_text[start:end]
        if OWNERSHIP_RE.search(context):
            own_hits += 1
        if COMPETITOR_RE.search(context):
            comp_hits += 1
    if total == 0:
        return 0.0
    return (own_hits - comp_hits) / total


def _normalize_text(text: str) -> str:
    """Normalize non-breaking spaces, newlines in mid-token, and other whitespace."""
    text = text.replace("\xa0", " ").replace("\u00a0", " ")
    # Collapse internal newlines in phase labels like "Phase\n1/2"
    text = re.sub(r"(Phase)\s*\n\s*(\d)", r"\1 \2", text)
    return text


# ── Main Actions ──────────────────────────────────────────────────────

def find_candidates(filepath: str) -> dict:
    """Parse S-1, identify drug candidates, extract passages, flag patterns."""
    soup = _load_html(filepath)
    sections = _extract_sections(soup)
    full_text = soup.get_text(separator="\n", strip=True)
    full_text_norm = _normalize_text(full_text)

    # Find NCT numbers
    nct_numbers = list(set(NCT_RE.findall(full_text_norm)))

    # Find candidate names
    raw_candidates = _find_candidate_names(full_text_norm)

    # Score each candidate for ownership and filter
    scored = []
    for cand in raw_candidates:
        score = _score_ownership(cand["name"], full_text_norm)
        cand["ownership_score"] = score
        scored.append(cand)

    # Separate into company candidates (score > 0) and comparators
    company_candidates = [c for c in scored if c["ownership_score"] > 0]
    comparator_names = [c["name"] for c in scored if c["ownership_score"] <= 0]

    # If no ownership-positive candidates found, fall back to most-mentioned
    if not company_candidates:
        company_candidates = sorted(scored, key=lambda c: -c["ownership_score"])[:5]

    # Build candidate objects — include ALL ownership-positive candidates
    # (user selects which one to investigate further via the skill)
    candidates = []
    for cand in company_candidates:
        name = cand["name"]
        passages = _extract_passages_for_name(name, sections)

        # Aggregate all passage text for this candidate (normalized)
        all_text = _normalize_text(" ".join(p["text"] for p in passages))

        # Find NCT numbers associated with this candidate
        cand_ncts = list(set(NCT_RE.findall(all_text)))

        # Find phase claims (normalized)
        phase_claims = list(set(
            _normalize_text(m.group())
            for m in PHASE_ANY_RE.finditer(all_text)
        ))

        # Find indications
        indication_patterns = [
            re.compile(
                r"for\s+(?:the\s+)?treatment\s+of\s+"
                r"([A-Z][A-Za-z\s\-'()]{3,55}?)(?:\.|,|\band\b|\bor\b|\bwith\b|\bin\b|\(|\bby\b)",
            ),
            re.compile(
                r"in\s+patients?\s+with\s+"
                r"([A-Z][A-Za-z\s\-'()]{3,55}?)(?:\.|,|\bwho\b|\band\b|\bor\b|\bthat\b)",
            ),
            re.compile(
                r"(?:in|for)\s+"
                r"((?:hidradenitis suppurativa|psoriatic arthritis"
                r"|rheumatoid arthritis|ankylosing spondylitis"
                r"|thyroid eye disease|chronic urticaria"
                r"|non-infectious uveitis|axial spondyloarthritis"
                r"|uveitis))",
                re.IGNORECASE,
            ),
        ]
        raw_indications = []
        for pat in indication_patterns:
            for m in pat.finditer(all_text):
                ind = m.group(1).strip().rstrip(".")
                ind = re.sub(r"\s+", " ", ind).strip()
                skip_starts = ("our ", "the ", "this ", "a ", "an ",
                               "such ", "certain ", "other ", "all ",
                               "each ", "these ", "its ")
                if (3 < len(ind) < 55
                        and not ind.lower().startswith(skip_starts)):
                    raw_indications.append(ind)
        seen_ind = set()
        indications = []
        for ind in raw_indications:
            key = ind.lower().strip()
            if key not in seen_ind:
                seen_ind.add(key)
                indications.append(ind)
        indications = indications[:10]

        # Find aliases — require explicit alias patterns like
        # "name (alias)" or "name, also known as alias"
        also_known_as = []
        alias_pats = [
            # "izokibep (SLRN-801)" or "SLRN-801 (izokibep)"
            re.compile(
                rf"\b{re.escape(name)}\b\s*\(([^)]+)\)",
                re.IGNORECASE,
            ),
            re.compile(
                rf"\(({re.escape(name)})\)",
                re.IGNORECASE,
            ),
            # "name, also known as X" / "name, formerly known as X"
            re.compile(
                rf"\b{re.escape(name)}\b[,\s]+(?:also|formerly|previously)\s+known\s+as\s+(\S+)",
                re.IGNORECASE,
            ),
        ]
        for apn in alias_pats:
            for m in apn.finditer(full_text_norm):
                alias_text = m.group(1).strip()
                # Check if the alias is another known candidate name
                for other in raw_candidates:
                    if other["name"] == name:
                        continue
                    if re.search(rf"\b{re.escape(other['name'])}\b",
                                 alias_text, re.IGNORECASE):
                        if other["name"] not in also_known_as:
                            also_known_as.append(other["name"])

        # FDA mentions
        fda_hits = _scan_fda_language(all_text)
        fda_mentions = list(set(h["phrase"] for h in fda_hits))

        # Combined phase flags
        combined_phases = _scan_combined_phases(all_text)

        # Red flag scan
        red_flags = _scan_red_flags(all_text)

        # Comparative claims
        comparatives = _scan_comparative(all_text)

        # Limit passages for JSON output size
        limited_passages = passages[:30]

        candidates.append({
            "name": name,
            "also_known_as": also_known_as,
            "passage_count": len(passages),
            "indications": indications,
            "phase_claims": phase_claims,
            "nct_numbers": cand_ncts,
            "fda_mentions": fda_mentions,
            "is_company_candidate": True,
            "flags": {
                "combined_phase_labels": list(set(
                    _normalize_text(h["label"]) for h in combined_phases
                )),
                "red_flag_phrases": [
                    {"phrase": h["phrase"], "context": h["context"]}
                    for h in red_flags[:20]
                ],
                "comparative_claims": [
                    {"phrase": h["phrase"], "context": h["context"]}
                    for h in comparatives[:10]
                ],
                "fda_language": [
                    {"phrase": h["phrase"], "context": h["context"]}
                    for h in fda_hits[:10]
                ],
            },
            "passages": [
                {
                    "section": p["section"],
                    "section_class": _classify_section(p["section"]),
                    "page_approx": p["page_approx"],
                    "char_offset": p["char_offset"],
                    "text": _normalize_text(p["text"][:500]),
                }
                for p in limited_passages
            ],
        })

    # Sort candidates by passage count (most-mentioned first)
    candidates.sort(key=lambda c: -c["passage_count"])

    # Pipeline table text — look for table near "pipeline" keyword
    pipeline_table_text = ""
    pipeline_is_image = False
    for section in sections:
        sec_text_lower = section["text"][:5000].lower()
        if "pipeline" in sec_text_lower or "our programs" in sec_text_lower:
            pipeline_table_text = section["text"][:2000]
            break

    # Check for pipeline images in HTML — look near "pipeline" text
    for img in soup.find_all("img"):
        # Check surrounding context for "pipeline" keywords
        parent = img.parent
        while parent and parent.name not in ("body", "html", None):
            parent_text = parent.get_text(strip=True).lower()[:500]
            if "pipeline" in parent_text or "our programs" in parent_text:
                pipeline_is_image = True
                break
            parent = parent.parent
        if pipeline_is_image:
            break

    # General statements (company-wide, not tied to one candidate)
    general_statements = []
    general_patterns = [
        r"we have no approved products",
        r"we have not generated any revenue from product sales",
        r"clinical.stage",
        r"we are a .*? biopharmaceutical",
    ]
    for pat in general_patterns:
        for m in re.finditer(pat, full_text, re.IGNORECASE):
            start = max(0, m.start() - 100)
            end = min(len(full_text), m.end() + 200)
            general_statements.append(full_text[start:end].strip())

    result = {
        "candidates": candidates,
        "comparator_drugs_mentioned": comparator_names,
        "nct_numbers_all": nct_numbers,
        "pipeline_table_text": _normalize_text(pipeline_table_text[:2000]),
        "pipeline_is_image": pipeline_is_image,
        "general_statements": [_normalize_text(s) for s in general_statements[:10]],
        "sections_found": [s["name"] for s in sections],
    }
    return result


def extract_passages(filepath: str, nct_number: str) -> list[dict]:
    """Extract all S-1 passages referencing a specific NCT number."""
    soup = _load_html(filepath)
    sections = _extract_sections(soup)
    return _extract_passages_for_name(nct_number, sections)


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="S-1 parser for drug candidate extraction")
    parser.add_argument("--action", required=True,
                        choices=["find_candidates", "extract_passages"])
    parser.add_argument("--file", required=True, help="Path to S-1 HTML file")
    parser.add_argument("--nct", help="NCT number (for extract_passages)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        raise SystemExit(f"File not found: {args.file}")

    if args.action == "find_candidates":
        result = find_candidates(args.file)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "extract_passages":
        if not args.nct:
            raise SystemExit("--nct required for extract_passages")
        passages = extract_passages(args.file, args.nct)
        print(json.dumps(passages, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
