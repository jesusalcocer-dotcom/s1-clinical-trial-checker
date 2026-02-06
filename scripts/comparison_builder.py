#!/usr/bin/env python3
"""
comparison_builder.py — Compare S-1 disclosures against ClinicalTrials.gov records.

Takes a candidate's S-1 parser output + CTgov manifest (all fetched studies)
and produces a structured comparison highlighting discrepancies.

Usage:
    python scripts/comparison_builder.py \
        --s1-json /tmp/s1_full.json \
        --candidate izokibep \
        --ctgov-dir /tmp/ctgov_fetchall/ctgov_izokibep \
        --output /tmp/comparison_izokibep.json
"""

import argparse
import json
import os
import re
import sys


# ── Phase Normalization ──────────────────────────────────────────────

# CTgov uses: EARLY_PHASE1, PHASE1, PHASE2, PHASE3, PHASE4, NA
# S-1 uses free text: "Phase 1", "Phase 1/2", "Phase 2b/3", etc.

CTGOV_PHASE_MAP = {
    "EARLY_PHASE1": {"Phase 1"},
    "PHASE1": {"Phase 1"},
    "PHASE2": {"Phase 2", "Phase 2a", "Phase 2b"},
    "PHASE3": {"Phase 3"},
    "PHASE4": {"Phase 4"},
}


def _normalize_s1_phase(phase_str: str) -> set[str]:
    """Parse S-1 phase string into a set of canonical phase numbers.

    'Phase 2b/3' -> {'Phase 2b', 'Phase 3'}
    'Phase 1/2' -> {'Phase 1', 'Phase 2'}
    'Phase 2' -> {'Phase 2'}
    """
    phases = set()
    # Handle combined labels: "Phase 1/2", "Phase 2b/3"
    combined = re.match(r"Phase\s+(\d[ab]?)\s*/\s*(\d[ab]?)", phase_str, re.IGNORECASE)
    if combined:
        phases.add(f"Phase {combined.group(1)}")
        phases.add(f"Phase {combined.group(2)}")
    else:
        m = re.match(r"Phase\s+(\d[ab]?)", phase_str, re.IGNORECASE)
        if m:
            phases.add(f"Phase {m.group(1)}")
    return phases


def _ctgov_phases_to_canonical(ctgov_phases: list[str]) -> set[str]:
    """Convert CTgov phase enums to canonical labels."""
    result = set()
    for p in ctgov_phases:
        p_upper = p.upper().replace(" ", "")
        if p_upper in CTGOV_PHASE_MAP:
            result.update(CTGOV_PHASE_MAP[p_upper])
    return result


def _base_phase(phase_str: str) -> int:
    """Extract the base phase number (1, 2, 3, 4) for rough comparison."""
    m = re.search(r"(\d)", phase_str)
    return int(m.group(1)) if m else 0


# ── Study Matching ───────────────────────────────────────────────────

def _get_study_indication(study: dict) -> str:
    """Extract the primary indication/condition from a CTgov study.

    Uses the study's conditions list and title to determine the indication.
    Returns the best indication string, or the brief title as fallback.
    """
    # CTgov conditions field is the most reliable
    conditions = study.get("eligibility", {}).get("criteria", "")
    # But the structured data may have conditions at top level — check title
    title = study.get("identification", {}).get("official_title", "")
    brief = study.get("identification", {}).get("brief_title", "")

    # Try conditions from title first (usually most specific)
    combined = f"{title} {brief}".lower()

    # Known condition patterns to extract
    condition_patterns = [
        ("hidradenitis suppurativa", "Hidradenitis Suppurativa"),
        ("psoriatic arthritis", "Psoriatic Arthritis"),
        ("rheumatoid arthritis", "Rheumatoid Arthritis"),
        ("ankylosing spondylitis", "Ankylosing Spondylitis"),
        ("axial spondyloarthritis", "Axial Spondyloarthritis"),
        ("thyroid eye disease", "Thyroid Eye Disease"),
        ("chronic urticaria", "Chronic Urticaria"),
        ("non-infectious uveitis", "Non-infectious Uveitis"),
        ("non-anterior uveitis", "Non-anterior Uveitis"),
        ("uveitis", "Uveitis"),
        ("crohn", "Crohn's Disease"),
        ("ulcerative colitis", "Ulcerative Colitis"),
        ("psoriasis", "Psoriasis"),
        ("lupus", "Lupus"),
        ("multiple sclerosis", "Multiple Sclerosis"),
        ("atopic dermatitis", "Atopic Dermatitis"),
    ]

    for pattern, label in condition_patterns:
        if pattern in combined:
            return label

    return brief


def _match_study_to_s1_indication(
    study_indication: str, s1_indications: list[str]
) -> str | None:
    """Match a CTgov study's indication to one of the S-1's listed indications.

    Returns the matching S-1 indication string, or None.
    """
    study_lower = study_indication.lower()

    # Synonym groups — each group represents the same condition
    # Only use full names (no 2-3 letter abbreviations that cause substring false matches)
    synonym_groups = [
        {"hidradenitis suppurativa"},
        {"psoriatic arthritis"},
        {"rheumatoid arthritis"},
        {"ankylosing spondylitis", "axial spondyloarthritis"},
        {"thyroid eye disease", "graves' ophthalmopathy", "graves' orbitopathy"},
        {"chronic urticaria", "chronic spontaneous urticaria"},
        {"uveitis", "non-infectious uveitis", "non-anterior uveitis"},
        {"crohn's disease"},
        {"ulcerative colitis"},
        {"psoriasis"},
        {"atopic dermatitis", "eczema"},
    ]

    for s1_ind in s1_indications:
        s1_lower = s1_ind.lower().strip()
        # Direct substring match (only meaningful if >5 chars to avoid false hits)
        if len(s1_lower) > 5 and len(study_lower) > 5:
            if s1_lower in study_lower or study_lower in s1_lower:
                return s1_ind
        elif s1_lower == study_lower:
            return s1_ind
        # Synonym group match
        for group in synonym_groups:
            study_in_group = any(syn in study_lower for syn in group)
            s1_in_group = any(syn in s1_lower for syn in group)
            if study_in_group and s1_in_group:
                return s1_ind

    return None


# ── Comparison Logic ─────────────────────────────────────────────────

def _compare_phase(s1_phase_claims: list[str], ctgov_study: dict) -> dict:
    """Compare S-1 phase claims against CTgov study phase.

    Note: s1_phase_claims are the candidate's global phase claims (across all
    indications). A future improvement would filter to only phase claims in
    passages that reference this specific study/indication.
    """
    ctgov_phases_raw = ctgov_study.get("design", {}).get("phases", [])
    ctgov_canonical = _ctgov_phases_to_canonical(ctgov_phases_raw)

    # Collect all S-1 phases into canonical form
    s1_canonical = set()
    for claim in s1_phase_claims:
        s1_canonical.update(_normalize_s1_phase(claim))

    issues = []

    # Get the highest phase CTgov registers
    ctgov_max = max((_base_phase(p) for p in ctgov_canonical), default=0)

    # Only flag phase inflation if the CTgov study's registered phase is
    # not present at all in the S-1's claims (the S-1 may legitimately
    # reference multiple phases for the same drug across indications)
    ctgov_phase_numbers = {_base_phase(p) for p in ctgov_canonical}
    s1_phase_numbers = {_base_phase(p) for p in s1_canonical}

    # Flag if S-1 never mentions the actual phase this study is registered as
    if ctgov_max > 0 and not ctgov_phase_numbers.intersection(s1_phase_numbers):
        issues.append({
            "type": "phase_mismatch",
            "severity": "high",
            "detail": (
                f"ClinicalTrials.gov registers this study as "
                f"{', '.join(ctgov_phases_raw)} but S-1 phase claims "
                f"({', '.join(s1_phase_claims)}) don't include this phase."
            ),
        })

    # Check for combined phase labels
    combined_labels = [c for c in s1_phase_claims
                       if re.search(r"\d\s*/\s*\d", c)]
    if combined_labels and ctgov_max > 0:
        issues.append({
            "type": "combined_phase_label",
            "severity": "low",
            "detail": (
                f"S-1 uses combined phase label(s) {combined_labels}. "
                f"ClinicalTrials.gov registers this study as "
                f"{', '.join(ctgov_phases_raw)}."
            ),
        })

    return {
        "s1_phase_claims": s1_phase_claims,
        "ctgov_phases": ctgov_phases_raw,
        "s1_canonical": sorted(s1_canonical),
        "ctgov_canonical": sorted(ctgov_canonical),
        "issues": issues,
    }


def _compare_status(s1_passages: list[dict], ctgov_study: dict) -> dict:
    """Check CTgov trial status against what the S-1 implies."""
    status = ctgov_study.get("status", {})
    overall = status.get("overall_status", "UNKNOWN")

    issues = []

    # Flag terminated/withdrawn/suspended trials
    negative_statuses = {"TERMINATED", "WITHDRAWN", "SUSPENDED"}
    if overall in negative_statuses:
        # Check if S-1 discloses the negative status
        s1_text = " ".join(p.get("text", "") for p in s1_passages).lower()
        disclosed = any(
            term in s1_text
            for term in ["terminat", "withdraw", "suspend", "discontinu", "halt"]
        )
        if not disclosed:
            issues.append({
                "type": "undisclosed_negative_status",
                "severity": "high",
                "detail": (
                    f"ClinicalTrials.gov shows this trial as {overall}, "
                    f"but no clear disclosure of termination/discontinuation "
                    f"was found in the S-1 passages for this candidate."
                ),
            })
        else:
            issues.append({
                "type": "negative_status_disclosed",
                "severity": "info",
                "detail": (
                    f"ClinicalTrials.gov shows this trial as {overall}. "
                    f"The S-1 appears to reference this status."
                ),
            })

    return {
        "ctgov_status": overall,
        "ctgov_start_date": status.get("start_date", ""),
        "ctgov_completion_date": status.get("completion_date", ""),
        "issues": issues,
    }


def _compare_enrollment(s1_passages: list[dict], ctgov_study: dict) -> dict:
    """Compare enrollment figures."""
    design = ctgov_study.get("design", {})
    ctgov_enrollment = design.get("enrollment_count")
    ctgov_type = design.get("enrollment_type", "")

    # Try to find enrollment numbers in S-1 passages
    s1_text = " ".join(p.get("text", "") for p in s1_passages)
    s1_enrollment_mentions = re.findall(
        r"(?:enroll|randomiz|recruit)\w*\s+(?:approximately\s+)?(\d[\d,]*)\s+(?:patients?|subjects?|participants?|individuals?)",
        s1_text, re.IGNORECASE,
    )
    s1_numbers = []
    for n in s1_enrollment_mentions:
        try:
            s1_numbers.append(int(n.replace(",", "")))
        except ValueError:
            pass

    issues = []
    if ctgov_enrollment and s1_numbers:
        for s1_n in s1_numbers:
            # Allow reasonable variance (enrollment targets vs actuals)
            if ctgov_type == "ACTUAL" and s1_n > ctgov_enrollment * 1.5:
                issues.append({
                    "type": "enrollment_overstatement",
                    "severity": "medium",
                    "detail": (
                        f"S-1 mentions {s1_n} but ClinicalTrials.gov reports "
                        f"ACTUAL enrollment of {ctgov_enrollment}."
                    ),
                })

    return {
        "ctgov_enrollment": ctgov_enrollment,
        "ctgov_enrollment_type": ctgov_type,
        "s1_enrollment_mentions": s1_numbers,
        "issues": issues,
    }


def _compare_design(s1_passages: list[dict], ctgov_study: dict) -> dict:
    """Compare study design details (blinding, randomization, arms)."""
    design = ctgov_study.get("design", {})
    arms = ctgov_study.get("arms_interventions", {}).get("arm_groups", [])

    s1_text = " ".join(p.get("text", "") for p in s1_passages).lower()
    issues = []

    # Check blinding claims
    ctgov_masking = design.get("masking", "").upper()
    if ctgov_masking == "NONE" or ctgov_masking == "":
        if "double-blind" in s1_text or "double blind" in s1_text:
            issues.append({
                "type": "blinding_mismatch",
                "severity": "high",
                "detail": (
                    f"S-1 references 'double-blind' but ClinicalTrials.gov "
                    f"shows masking as '{ctgov_masking or 'NONE/OPEN'}'."
                ),
            })
    if "open-label" in s1_text or "open label" in s1_text:
        if ctgov_masking in ("DOUBLE", "TRIPLE", "QUADRUPLE"):
            issues.append({
                "type": "blinding_mismatch",
                "severity": "medium",
                "detail": (
                    f"S-1 references 'open-label' but ClinicalTrials.gov "
                    f"shows masking as '{ctgov_masking}'."
                ),
            })

    # Check randomization
    ctgov_allocation = design.get("allocation", "").upper()
    if "randomized" in s1_text and ctgov_allocation == "NON_RANDOMIZED":
        issues.append({
            "type": "randomization_mismatch",
            "severity": "medium",
            "detail": "S-1 claims randomized but ClinicalTrials.gov shows NON_RANDOMIZED.",
        })

    return {
        "ctgov_masking": ctgov_masking,
        "ctgov_allocation": ctgov_allocation,
        "ctgov_arms": [
            {"label": a.get("label", ""), "type": a.get("type", "")}
            for a in arms
        ],
        "issues": issues,
    }


def _compare_endpoints(s1_passages: list[dict], ctgov_study: dict) -> dict:
    """Compare primary/secondary endpoints."""
    primary = ctgov_study.get("primary_outcomes", [])
    secondary = ctgov_study.get("secondary_outcomes", [])

    s1_text = " ".join(p.get("text", "") for p in s1_passages).lower()
    issues = []

    # Check if S-1 cites a secondary endpoint as if it were primary
    for so in secondary:
        measure = so.get("measure", "").lower()
        # Extract key terms from the endpoint
        key_terms = [t for t in re.findall(r"\b\w{4,}\b", measure)
                     if t not in ("with", "from", "that", "this", "were", "been")]
        # Check if S-1 references this endpoint as "primary"
        for term in key_terms[:3]:
            # Look for the term near "primary" in S-1
            pattern = re.compile(
                rf"primary\s+(?:endpoint|outcome|measure).*?\b{re.escape(term)}\b"
                rf"|\b{re.escape(term)}\b.*?primary\s+(?:endpoint|outcome|measure)",
                re.IGNORECASE,
            )
            if pattern.search(s1_text):
                issues.append({
                    "type": "endpoint_promotion",
                    "severity": "high",
                    "detail": (
                        f"S-1 may reference '{so['measure'][:80]}' as primary, "
                        f"but ClinicalTrials.gov lists it as a SECONDARY outcome."
                    ),
                })
                break  # one flag per endpoint

    return {
        "ctgov_primary_endpoints": [
            {"measure": p.get("measure", ""), "time_frame": p.get("time_frame", "")}
            for p in primary
        ],
        "ctgov_secondary_endpoints": [
            {"measure": s.get("measure", ""), "time_frame": s.get("time_frame", "")}
            for s in secondary
        ],
        "issues": issues,
    }


def _compare_results(s1_passages: list[dict], ctgov_study: dict) -> dict:
    """Compare posted results against S-1 claims."""
    if not ctgov_study.get("has_results"):
        return {"has_results": False, "issues": []}

    results = ctgov_study.get("results", {})
    outcome_measures = results.get("outcome_measures", [])
    adverse_events = results.get("adverse_events", {})

    s1_text = " ".join(p.get("text", "") for p in s1_passages).lower()
    issues = []

    # Check primary outcomes for statistical significance
    for om in outcome_measures:
        if om.get("type", "").upper() != "PRIMARY":
            continue
        for analysis in om.get("analyses", []):
            p_val_str = analysis.get("pValue", "")
            if not p_val_str:
                continue
            try:
                p_val = float(p_val_str.replace("<", "").replace(">", "").strip())
            except (ValueError, TypeError):
                continue

            title_short = om.get("title", "")[:60]
            if p_val > 0.05:
                # Primary endpoint missed significance
                # Check if S-1 discloses this
                if "not statistically significant" not in s1_text and "did not meet" not in s1_text:
                    issues.append({
                        "type": "undisclosed_missed_endpoint",
                        "severity": "high",
                        "detail": (
                            f"Primary endpoint '{title_short}' has p={p_val_str} "
                            f"(not statistically significant). S-1 may not clearly "
                            f"disclose this missed endpoint."
                        ),
                    })
                else:
                    issues.append({
                        "type": "missed_endpoint_disclosed",
                        "severity": "info",
                        "detail": (
                            f"Primary endpoint '{title_short}' has p={p_val_str} "
                            f"(not significant). S-1 appears to acknowledge this."
                        ),
                    })
            else:
                # Endpoint met significance — check if S-1 overstates
                issues.append({
                    "type": "significant_endpoint",
                    "severity": "info",
                    "detail": (
                        f"Primary endpoint '{title_short}' shows p={p_val_str} "
                        f"(statistically significant)."
                    ),
                })

    # Check adverse events
    serious_events = adverse_events.get("serious_events", [])
    if serious_events:
        # Look for high-frequency serious AEs
        notable_saes = []
        for se in serious_events:
            term = se.get("term", "")
            for stat in se.get("stats", []):
                num = stat.get("numEvents")
                if num and isinstance(num, (int, float)) and num > 0:
                    notable_saes.append({"term": term, "count": num})
                    break

        if notable_saes:
            # Check if S-1 mentions adverse events at all
            ae_terms_in_s1 = sum(
                1 for sae in notable_saes
                if sae["term"].lower() in s1_text
            )
            total_saes = len(notable_saes)
            if ae_terms_in_s1 < total_saes * 0.3 and total_saes > 2:
                issues.append({
                    "type": "adverse_events_underreported",
                    "severity": "medium",
                    "detail": (
                        f"ClinicalTrials.gov reports {total_saes} distinct serious "
                        f"adverse event terms, but only {ae_terms_in_s1} appear "
                        f"to be mentioned in the S-1 passages."
                    ),
                    "notable_saes": [
                        f"{s['term']} ({s['count']} events)"
                        for s in sorted(notable_saes, key=lambda x: -x["count"])[:5]
                    ],
                })

    # Build results summary
    results_summary = {
        "outcome_measures_count": len(outcome_measures),
        "primary_measures": [],
        "serious_ae_count": len(serious_events),
        "other_ae_count": len(adverse_events.get("other_events", [])),
    }
    for om in outcome_measures:
        if om.get("type", "").upper() == "PRIMARY":
            analyses_summary = []
            for a in om.get("analyses", []):
                analyses_summary.append({
                    "p_value": a.get("pValue", ""),
                    "method": a.get("statisticalMethod", ""),
                    "param_value": a.get("paramValue", ""),
                    "ci": a.get("ciNumSides", ""),
                })
            results_summary["primary_measures"].append({
                "title": om.get("title", ""),
                "analyses": analyses_summary,
            })

    return {
        "has_results": True,
        "results_summary": results_summary,
        "issues": issues,
    }


def _check_s1_flags(candidate_data: dict) -> list[dict]:
    """Surface the S-1 parser's own flag detections as issues."""
    issues = []
    flags = candidate_data.get("flags", {})

    # Red flag phrases
    red_flags = flags.get("red_flag_phrases", [])
    if red_flags:
        issues.append({
            "type": "red_flag_language",
            "severity": "medium",
            "detail": (
                f"S-1 contains {len(red_flags)} red-flag phrase(s) for this candidate: "
                + ", ".join(set(r["phrase"] for r in red_flags[:10]))
            ),
            "examples": [
                {"phrase": r["phrase"], "context": r["context"][:200]}
                for r in red_flags[:5]
            ],
        })

    # Comparative claims
    comparatives = flags.get("comparative_claims", [])
    if comparatives:
        issues.append({
            "type": "comparative_language",
            "severity": "medium",
            "detail": (
                f"S-1 contains {len(comparatives)} comparative claim(s): "
                + ", ".join(set(c["phrase"] for c in comparatives[:5]))
            ),
            "examples": [
                {"phrase": c["phrase"], "context": c["context"][:200]}
                for c in comparatives[:5]
            ],
        })

    # FDA language
    fda_lang = flags.get("fda_language", [])
    if fda_lang:
        issues.append({
            "type": "fda_communication_language",
            "severity": "low",
            "detail": (
                f"S-1 references {len(fda_lang)} FDA communication(s): "
                + ", ".join(set(f["phrase"] for f in fda_lang[:5]))
            ),
        })

    # Combined phase labels
    combined = flags.get("combined_phase_labels", [])
    if combined:
        issues.append({
            "type": "combined_phase_labels_in_s1",
            "severity": "medium",
            "detail": (
                f"S-1 uses combined phase label(s): {combined}. "
                f"These can obscure which phase generated cited data."
            ),
        })

    return issues


# ── Main Comparison ──────────────────────────────────────────────────

def build_comparison(
    s1_data: dict,
    candidate_name: str,
    ctgov_dir: str,
) -> dict:
    """Build full comparison between S-1 candidate and CTgov studies.

    Args:
        s1_data: Full output from s1_parser.py find_candidates action.
        candidate_name: Name of the candidate to compare (e.g. "izokibep").
        ctgov_dir: Directory containing CTgov structured JSONs and manifest.

    Returns:
        Structured comparison dict with per-study comparisons and summary.
    """
    # Find the candidate in S-1 data
    candidate = None
    for c in s1_data.get("candidates", []):
        if c["name"].lower() == candidate_name.lower():
            candidate = c
            break
    if not candidate:
        return {"error": f"Candidate '{candidate_name}' not found in S-1 data."}

    # Load CTgov manifest
    manifest_path = os.path.join(ctgov_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return {"error": f"No manifest.json found in {ctgov_dir}. Run fetch-all first."}

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Load all structured study files
    studies = []
    for study_info in manifest.get("studies", []):
        structured_path = study_info.get("structured_file", "")
        if not os.path.exists(structured_path):
            continue
        with open(structured_path, "r", encoding="utf-8") as f:
            studies.append(json.load(f))

    if not studies:
        return {"error": "No structured study files found."}

    # Get S-1 passages for this candidate
    s1_passages = candidate.get("passages", [])

    # Compare each study
    study_comparisons = []
    all_issues = []

    for study in studies:
        nct_id = study.get("identification", {}).get("nct_id", "")
        title = study.get("identification", {}).get("brief_title", "")
        study_indication = _get_study_indication(study)
        matched_indication = _match_study_to_s1_indication(
            study_indication, candidate.get("indications", [])
        )

        # Run comparisons
        phase_cmp = _compare_phase(candidate.get("phase_claims", []), study)
        status_cmp = _compare_status(s1_passages, study)
        enrollment_cmp = _compare_enrollment(s1_passages, study)
        design_cmp = _compare_design(s1_passages, study)
        endpoint_cmp = _compare_endpoints(s1_passages, study)
        results_cmp = _compare_results(s1_passages, study)

        # Collect issues from this study
        study_issues = []
        for cmp in [phase_cmp, status_cmp, enrollment_cmp, design_cmp,
                     endpoint_cmp, results_cmp]:
            study_issues.extend(cmp.get("issues", []))

        # Tag each issue with the NCT ID
        for issue in study_issues:
            issue["nct_id"] = nct_id
        all_issues.extend(study_issues)

        study_comparisons.append({
            "nct_id": nct_id,
            "brief_title": title,
            "study_indication": study_indication,
            "matched_s1_indication": matched_indication,
            "sponsor": study.get("sponsor", {}).get("name", ""),
            "phase": phase_cmp,
            "status": status_cmp,
            "enrollment": enrollment_cmp,
            "design": design_cmp,
            "endpoints": endpoint_cmp,
            "results": results_cmp,
            "issue_count": len(study_issues),
        })

    # S-1 language flags (not tied to a specific study)
    s1_flags = _check_s1_flags(candidate)
    all_issues.extend(s1_flags)

    # Severity summary
    high_count = sum(1 for i in all_issues if i.get("severity") == "high")
    medium_count = sum(1 for i in all_issues if i.get("severity") == "medium")
    low_count = sum(1 for i in all_issues if i.get("severity") == "low")
    info_count = sum(1 for i in all_issues if i.get("severity") == "info")

    return {
        "candidate": {
            "name": candidate["name"],
            "also_known_as": candidate.get("also_known_as", []),
            "indications": candidate.get("indications", []),
            "phase_claims": candidate.get("phase_claims", []),
            "nct_numbers_in_s1": candidate.get("nct_numbers", []),
            "fda_mentions": candidate.get("fda_mentions", []),
            "passage_count": candidate.get("passage_count", 0),
        },
        "ctgov_summary": {
            "studies_found": manifest.get("search_hits", 0),
            "studies_fetched": len(studies),
            "studies_with_results": sum(1 for s in studies if s.get("has_results")),
        },
        "study_comparisons": study_comparisons,
        "all_issues": all_issues,
        "severity_summary": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "info": info_count,
            "total": len(all_issues),
        },
    }


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare S-1 disclosures against ClinicalTrials.gov records"
    )
    parser.add_argument(
        "--s1-json", required=True,
        help="Path to S-1 parser JSON output (from find_candidates action)",
    )
    parser.add_argument(
        "--candidate", required=True,
        help="Candidate name to compare (e.g. 'izokibep')",
    )
    parser.add_argument(
        "--ctgov-dir", required=True,
        help="Directory with CTgov structured JSONs and manifest.json",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    # Load S-1 data
    with open(args.s1_json, "r", encoding="utf-8") as f:
        s1_data = json.load(f)

    # Build comparison
    result = build_comparison(s1_data, args.candidate, args.ctgov_dir)

    # Output
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        # Print summary to stderr
        sev = result.get("severity_summary", {})
        print(f"Comparison complete: {args.candidate}", file=sys.stderr)
        print(f"  Studies compared: {len(result.get('study_comparisons', []))}", file=sys.stderr)
        print(f"  Issues: {sev.get('high',0)} high, {sev.get('medium',0)} medium, "
              f"{sev.get('low',0)} low, {sev.get('info',0)} info", file=sys.stderr)
        print(f"  Output: {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
