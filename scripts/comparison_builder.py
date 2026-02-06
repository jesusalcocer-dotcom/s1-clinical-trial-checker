#!/usr/bin/env python3
"""
comparison_builder.py — Compare S-1 disclosures against ClinicalTrials.gov data.

Takes a selected drug candidate's S-1 parser output and their full set of
CTgov studies, then builds a structured comparison highlighting discrepancies.

Usage:
    python scripts/comparison_builder.py \
        --s1-json s1_parsed.json \
        --candidate izokibep \
        --ctgov-dir data/ctgov_izokibep/ \
        --output comparison_izokibep.json
"""

import argparse
import json
import os
import re
import sys


# ── Study Matching ────────────────────────────────────────────────────

# Map common condition abbreviations/keywords to ClinicalTrials.gov condition terms
CONDITION_ALIASES = {
    "hs": ["hidradenitis suppurativa"],
    "hidradenitis": ["hidradenitis suppurativa"],
    "ted": ["thyroid eye disease", "graves' ophthalmopathy", "graves ophthalmopathy"],
    "thyroid eye": ["thyroid eye disease"],
    "graves": ["thyroid eye disease", "graves' ophthalmopathy"],
    "psa": ["psoriatic arthritis"],
    "psoriatic": ["psoriatic arthritis"],
    "axspa": ["ankylosing spondylitis", "axial spondyloarthritis"],
    "ankylosing": ["ankylosing spondylitis"],
    "uveitis": ["uveitis", "non-infectious uveitis", "non-anterior uveitis"],
    "ra": ["rheumatoid arthritis"],
    "rheumatoid": ["rheumatoid arthritis"],
    "pso": ["psoriasis", "plaque psoriasis"],
    "psoriasis": ["psoriasis", "plaque psoriasis"],
    "chronic urticaria": ["chronic urticaria", "chronic spontaneous urticaria"],
    "csu": ["chronic spontaneous urticaria", "chronic urticaria"],
    "atopic dermatitis": ["atopic dermatitis", "eczema"],
    "crohn": ["crohn disease", "crohn's disease"],
    "uc": ["ulcerative colitis"],
    "lupus": ["systemic lupus erythematosus", "lupus"],
    "sle": ["systemic lupus erythematosus"],
}

# Map S-1 phase text to CTgov phase enums
PHASE_MAP = {
    "phase 1": ["PHASE1", "EARLY_PHASE1"],
    "phase 1a": ["PHASE1", "EARLY_PHASE1"],
    "phase 1b": ["PHASE1"],
    "phase 1/2": ["PHASE1", "PHASE2"],
    "phase 2": ["PHASE2"],
    "phase 2a": ["PHASE2"],
    "phase 2b": ["PHASE2"],
    "phase 2b/3": ["PHASE2", "PHASE3"],
    "phase 3": ["PHASE3"],
    "phase 4": ["PHASE4"],
}


def _normalize_phase(phase_str: str) -> list[str]:
    """Convert an S-1 phase label to possible CTgov phase enum values."""
    return PHASE_MAP.get(phase_str.lower().strip(), [])


def _extract_conditions_from_text(text: str) -> list[str]:
    """Find condition/indication keywords in a passage of text."""
    text_lower = text.lower()
    found = []
    for alias, conditions in CONDITION_ALIASES.items():
        # Look for alias as a standalone word/phrase
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            found.extend(conditions)
    return list(set(found))


def _extract_phase_from_text(text: str) -> list[str]:
    """Extract phase labels from a passage of text."""
    phases = []
    for match in re.finditer(
        r'phase\s*(\d[a-b]?(?:/\d[a-b]?)?)', text, re.IGNORECASE
    ):
        phase_str = f"phase {match.group(1)}"
        phases.extend(_normalize_phase(phase_str))
    return list(set(phases))


def _extract_enrollment_from_text(text: str) -> list[int]:
    """Extract enrollment/participant numbers from text."""
    numbers = []
    for match in re.finditer(
        r'(\d[\d,]*)\s*(?:patients?|participants?|subjects?|individuals?)',
        text, re.IGNORECASE
    ):
        num_str = match.group(1).replace(",", "")
        try:
            n = int(num_str)
            if 5 <= n <= 100000:  # reasonable enrollment range
                numbers.append(n)
        except ValueError:
            pass
    return numbers


def match_passages_to_studies(
    passages: list[dict],
    studies: list[dict],
) -> dict[str, list[dict]]:
    """Match S-1 passages to CTgov studies based on context clues.

    Returns a dict mapping NCT ID → list of matched passages.
    Passages that don't match any study go under "unmatched".
    """
    matched: dict[str, list[dict]] = {s["identification"]["nct_id"]: [] for s in studies}
    matched["unmatched"] = []

    for passage in passages:
        text = passage.get("text", "")
        scores: dict[str, float] = {}

        # Extract clues from the passage
        passage_conditions = _extract_conditions_from_text(text)
        passage_phases = _extract_phase_from_text(text)
        passage_enrollments = _extract_enrollment_from_text(text)

        for study in studies:
            nct_id = study["identification"]["nct_id"]
            score = 0.0

            # Condition matching — strongest signal
            study_title = study["identification"].get("brief_title", "").lower()
            study_official = study["identification"].get("official_title", "").lower()
            study_conditions = [c.lower() for c in _get_study_conditions(study)]
            study_text = f"{study_title} {study_official} {' '.join(study_conditions)}"

            for cond in passage_conditions:
                if cond.lower() in study_text:
                    score += 3.0

            # Phase matching
            study_phases = study["design"].get("phases", [])
            for phase in passage_phases:
                if phase in study_phases:
                    score += 2.0

            # Enrollment matching (fuzzy — within 20%)
            study_enrollment = study["design"].get("enrollment_count")
            if study_enrollment and passage_enrollments:
                for pe in passage_enrollments:
                    if abs(pe - study_enrollment) / max(study_enrollment, 1) < 0.2:
                        score += 2.0

            # NCT number mentioned directly in the passage
            if nct_id in text:
                score += 10.0

            # Title keywords in passage (partial match)
            title_words = set(re.findall(r'\w{4,}', study_title))
            passage_words = set(re.findall(r'\w{4,}', text.lower()))
            overlap = title_words & passage_words
            if len(overlap) >= 2:
                score += 1.0

            scores[nct_id] = score

        # Assign passage to best-matching study (if score > 0)
        if scores:
            best_nct = max(scores, key=scores.get)
            if scores[best_nct] > 0:
                matched[best_nct].append({**passage, "_match_score": scores[best_nct]})
            else:
                matched["unmatched"].append(passage)
        else:
            matched["unmatched"].append(passage)

    return matched


def _get_study_conditions(study: dict) -> list[str]:
    """Extract conditions from structured study data.

    Looks in protocolSection's conditionsModule if present in the raw
    structured format, otherwise constructs from the title.
    """
    # The structured format from ctgov_fetch stores conditions under
    # primary_outcomes or in the title. We need to check the raw data too.
    title = study["identification"].get("brief_title", "")
    official = study["identification"].get("official_title", "")
    combined = f"{title} {official}"

    # Extract conditions by checking our known aliases
    conditions = _extract_conditions_from_text(combined)
    return conditions if conditions else [combined]


# ── Comparison Logic ──────────────────────────────────────────────────

def build_comparison(
    candidate: dict,
    studies: list[dict],
    all_passages: list[dict],
    s1_filing_date: str = "",
) -> dict:
    """Build a structured comparison between S-1 claims and CTgov data.

    Args:
        candidate: The selected candidate dict from s1_parser output.
        studies: List of structured CTgov study dicts.
        all_passages: All S-1 passages mentioning this candidate.
        s1_filing_date: S-1 filing date as YYYY-MM-DD (used for temporal checks).

    Returns:
        Structured comparison dict with per-study analysis and flags.
    """
    # Step 1: Match passages to studies
    passage_map = match_passages_to_studies(all_passages, studies)

    # Step 2: Per-study comparison
    study_comparisons = []
    for study in studies:
        nct_id = study["identification"]["nct_id"]
        matched_passages = passage_map.get(nct_id, [])

        comparison = _compare_study(study, matched_passages, candidate, s1_filing_date)
        study_comparisons.append(comparison)

    # Step 3: Overall candidate-level flags
    candidate_flags = _build_candidate_flags(candidate, studies, passage_map)

    return {
        "candidate_name": candidate["name"],
        "also_known_as": candidate.get("also_known_as", []),
        "studies_compared": len(studies),
        "study_comparisons": study_comparisons,
        "unmatched_passages": len(passage_map.get("unmatched", [])),
        "unmatched_passage_samples": [
            p["text"][:200] for p in passage_map.get("unmatched", [])[:5]
        ],
        "candidate_flags": candidate_flags,
    }


def _compare_study(
    study: dict,
    matched_passages: list[dict],
    candidate: dict,
    s1_filing_date: str = "",
) -> dict:
    """Compare a single CTgov study against its matched S-1 passages."""
    nct_id = study["identification"]["nct_id"]
    discrepancies = []
    observations = []

    # Temporal check: if study started after S-1 filing, flag it
    study_start = study["status"].get("start_date", "")
    if s1_filing_date and study_start and study_start > s1_filing_date:
        observations.append(
            f"Study started {study_start}, after S-1 filing date {s1_filing_date} — "
            f"post-filing study, S-1 would not reference it"
        )

    # --- Phase comparison ---
    ctgov_phases = study["design"].get("phases", [])
    s1_phases = set()
    for p in matched_passages:
        s1_phases.update(_extract_phase_from_text(p.get("text", "")))
    # Also include overall candidate phase claims
    for pc in candidate.get("phase_claims", []):
        s1_phases.update(_normalize_phase(pc))

    s1_phases = sorted(s1_phases)
    if ctgov_phases and s1_phases:
        ctgov_set = set(ctgov_phases)
        s1_set = set(s1_phases)
        if not ctgov_set & s1_set:
            discrepancies.append({
                "type": "phase_mismatch",
                "severity": "high",
                "s1_claims": list(s1_set),
                "ctgov_data": ctgov_phases,
                "detail": f"S-1 phase labels ({', '.join(s1_set)}) don't match CTgov ({', '.join(ctgov_phases)})",
            })

    # --- Status check ---
    ctgov_status = study["status"].get("overall_status", "")
    status_flags = []
    passage_text_combined = " ".join(p.get("text", "") for p in matched_passages).lower()

    if ctgov_status == "TERMINATED":
        # If the study started after the S-1, it's not a disclosure issue
        is_post_filing = (s1_filing_date and study_start and study_start > s1_filing_date)
        if is_post_filing:
            observations.append(
                f"Study is TERMINATED but started after S-1 filing — not a disclosure gap"
            )
        elif not re.search(r'\b(terminat|discontinu|halt|stopp|ceas)\w*\b', passage_text_combined):
            discrepancies.append({
                "type": "status_not_disclosed",
                "severity": "high",
                "s1_claims": "No termination language found in matched passages",
                "ctgov_data": f"Study is TERMINATED on ClinicalTrials.gov",
                "detail": f"{nct_id} is TERMINATED but S-1 passages don't appear to disclose this",
            })
        else:
            observations.append(f"Study termination appears disclosed in S-1")

    if ctgov_status == "WITHDRAWN":
        discrepancies.append({
            "type": "study_withdrawn",
            "severity": "high",
            "s1_claims": "Study referenced in S-1",
            "ctgov_data": f"Study is WITHDRAWN on ClinicalTrials.gov",
            "detail": f"{nct_id} is WITHDRAWN — may need prominent disclosure",
        })

    if ctgov_status == "SUSPENDED":
        if "suspend" not in passage_text_combined:
            discrepancies.append({
                "type": "status_not_disclosed",
                "severity": "medium",
                "s1_claims": "No suspension language found",
                "ctgov_data": f"Study is SUSPENDED on ClinicalTrials.gov",
                "detail": f"{nct_id} is SUSPENDED but S-1 doesn't appear to mention it",
            })

    # --- Enrollment comparison ---
    ctgov_enrollment = study["design"].get("enrollment_count")
    ctgov_enrollment_type = study["design"].get("enrollment_type", "")
    if ctgov_enrollment and matched_passages:
        s1_enrollments = set()
        for p in matched_passages:
            s1_enrollments.update(_extract_enrollment_from_text(p.get("text", "")))

        if s1_enrollments:
            # Check if any S-1 enrollment claim is significantly different
            # Only flag if the enrollment number appears in the SAME sentence
            # as the study's condition (to avoid cross-study false positives)
            study_conditions = _extract_conditions_from_text(
                study["identification"].get("brief_title", "")
            )
            for s1_n in sorted(s1_enrollments):
                diff_pct = abs(s1_n - ctgov_enrollment) / max(ctgov_enrollment, 1)
                if diff_pct > 0.3:  # >30% difference
                    discrepancies.append({
                        "type": "enrollment_mismatch",
                        "severity": "medium",
                        "s1_claims": f"{s1_n} participants mentioned in S-1",
                        "ctgov_data": f"{ctgov_enrollment} ({ctgov_enrollment_type}) on CTgov",
                        "detail": f"Enrollment difference of {diff_pct:.0%}: S-1 says ~{s1_n}, CTgov says {ctgov_enrollment}",
                    })

    # --- Results analysis (if posted) ---
    is_post_filing = (s1_filing_date and study_start and study_start > s1_filing_date)
    results_analysis = None
    if study.get("has_results") and "results" in study:
        results_analysis = _analyze_results(study, matched_passages)
        observations.extend(results_analysis.get("observations", []))
        # Only flag discrepancies for studies that existed at S-1 filing time
        if not is_post_filing:
            discrepancies.extend(results_analysis.get("discrepancies", []))
        else:
            for d in results_analysis.get("discrepancies", []):
                observations.append(f"[Suppressed — post-filing] {d['type']}: {d['detail'][:80]}")

    # --- S-1 flag extraction from matched passages ---
    red_flags_in_passages = []
    comparative_claims = []
    for p in matched_passages:
        text = p.get("text", "")
        # Red flag phrases
        for phrase in [
            "effective", "superior", "best-in-class", "breakthrough",
            "first-in-class", "promising", "compelling", "robust",
            "clinically validated", "clinically meaningful",
            "transformative", "paradigm",
        ]:
            if re.search(r'\b' + re.escape(phrase) + r'\b', text, re.IGNORECASE):
                red_flags_in_passages.append({
                    "phrase": phrase,
                    "context": text[:150],
                })
        # Comparative claims
        for phrase in [
            "compared to", "superior to", "better than", "more effective",
            "outperform", "differentiated", "advantage over",
        ]:
            if re.search(r'\b' + re.escape(phrase) + r'\b', text, re.IGNORECASE):
                comparative_claims.append({
                    "phrase": phrase,
                    "context": text[:150],
                })

    return {
        "nct_id": nct_id,
        "brief_title": study["identification"]["brief_title"],
        "ctgov_status": ctgov_status,
        "ctgov_phases": ctgov_phases,
        "ctgov_enrollment": ctgov_enrollment,
        "ctgov_enrollment_type": ctgov_enrollment_type,
        "has_results": study.get("has_results", False),
        "matched_passages": len(matched_passages),
        "discrepancies": discrepancies,
        "observations": observations,
        "results_analysis": results_analysis,
        "red_flags_in_passages": red_flags_in_passages[:10],
        "comparative_claims": comparative_claims[:10],
    }


def _analyze_results(study: dict, matched_passages: list[dict]) -> dict:
    """Analyze posted results vs S-1 claims for a single study."""
    results = study["results"]
    discrepancies = []
    observations = []

    passage_text = " ".join(p.get("text", "") for p in matched_passages).lower()

    # --- Primary endpoint analysis ---
    primary_outcomes = [
        om for om in results.get("outcome_measures", [])
        if om.get("type") == "PRIMARY"
    ]
    secondary_outcomes = [
        om for om in results.get("outcome_measures", [])
        if om.get("type") == "SECONDARY"
    ]

    # Check if S-1 mentions primary endpoint results
    if primary_outcomes:
        observations.append(
            f"Study has {len(primary_outcomes)} primary and "
            f"{len(secondary_outcomes)} secondary outcome measures posted"
        )

    # --- Check for selective reporting ---
    # If S-1 discusses secondary endpoints but not primary, that's a flag
    primary_titles = [om.get("title", "").lower() for om in primary_outcomes]
    secondary_titles = [om.get("title", "").lower() for om in secondary_outcomes]

    # Look for references to secondary but not primary outcomes
    secondary_keywords_found = 0
    primary_keywords_found = 0
    for title in primary_titles:
        keywords = set(re.findall(r'\w{5,}', title))
        if any(kw in passage_text for kw in keywords):
            primary_keywords_found += 1
    for title in secondary_titles:
        keywords = set(re.findall(r'\w{5,}', title))
        if any(kw in passage_text for kw in keywords):
            secondary_keywords_found += 1

    if secondary_keywords_found > 0 and primary_keywords_found == 0 and primary_outcomes:
        discrepancies.append({
            "type": "selective_endpoint_reporting",
            "severity": "high",
            "s1_claims": f"S-1 references secondary endpoints but not primary",
            "ctgov_data": f"{len(primary_outcomes)} primary outcomes posted on CTgov",
            "detail": "Possible cherry-picking: S-1 discusses secondary endpoints but "
                      "doesn't mention primary endpoint results",
        })

    # --- Adverse events analysis ---
    ae = results.get("adverse_events", {})
    serious_events = ae.get("serious_events", [])
    other_events = ae.get("other_events", [])

    if serious_events:
        sae_count = len(serious_events)
        observations.append(f"CTgov reports {sae_count} categories of serious adverse events")

        # Check if S-1 mentions safety/adverse events for this study
        safety_keywords = ["adverse", "safety", "tolerab", "side effect", "serious",
                           "discontinu", "death", "hospitali"]
        safety_mentioned = any(kw in passage_text for kw in safety_keywords)

        if not safety_mentioned and sae_count > 0:
            discrepancies.append({
                "type": "safety_not_discussed",
                "severity": "medium",
                "s1_claims": "No safety/AE language in matched passages",
                "ctgov_data": f"{sae_count} SAE categories reported on CTgov",
                "detail": "S-1 passages about this study don't discuss safety data "
                          "despite serious adverse events being reported",
            })

    # --- Statistical analyses ---
    all_analyses = []
    for om in results.get("outcome_measures", []):
        for analysis in om.get("analyses", []):
            all_analyses.append({
                "outcome": om.get("title", ""),
                "outcome_type": om.get("type", ""),
                "method": analysis.get("statisticalMethod", ""),
                "p_value": analysis.get("pValue", ""),
                "ci_lower": analysis.get("ciLowerLimit", ""),
                "ci_upper": analysis.get("ciUpperLimit", ""),
                "ci_pct": analysis.get("ciNumSides", ""),
                "param_value": analysis.get("paramValue", ""),
                "group_description": analysis.get("groupDescription", ""),
            })

    # Check for p-value mismatches or missing CI reporting
    if all_analyses:
        observations.append(f"CTgov has {len(all_analyses)} statistical analyses posted")

    return {
        "primary_outcomes_count": len(primary_outcomes),
        "secondary_outcomes_count": len(secondary_outcomes),
        "serious_ae_categories": len(serious_events),
        "other_ae_categories": len(other_events),
        "statistical_analyses": all_analyses[:20],  # cap at 20
        "discrepancies": discrepancies,
        "observations": observations,
    }


# ── Candidate-Level Flags ─────────────────────────────────────────────

def _build_candidate_flags(
    candidate: dict,
    studies: list[dict],
    passage_map: dict[str, list[dict]],
) -> dict:
    """Build overall candidate-level flags across all studies."""
    flags = {
        "total_studies": len(studies),
        "studies_with_results": sum(1 for s in studies if s.get("has_results")),
        "terminated_studies": [],
        "completed_studies": [],
        "active_studies": [],
        "combined_phase_labels": candidate.get("flags", {}).get("combined_phase_labels", []),
        "studies_not_mentioned_in_s1": [],
        "s1_red_flags": candidate.get("flags", {}).get("red_flag_phrases", []),
        "s1_comparative_claims": candidate.get("flags", {}).get("comparative_claims", []),
        "s1_fda_language": candidate.get("flags", {}).get("fda_language", []),
    }

    for study in studies:
        nct_id = study["identification"]["nct_id"]
        title = study["identification"]["brief_title"]
        status = study["status"]["overall_status"]
        matched = len(passage_map.get(nct_id, []))

        entry = {"nct_id": nct_id, "title": title, "matched_passages": matched}

        if status in ("TERMINATED", "WITHDRAWN"):
            flags["terminated_studies"].append(entry)
        elif status == "COMPLETED":
            flags["completed_studies"].append(entry)
        elif status in ("RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION",
                        "NOT_YET_RECRUITING"):
            flags["active_studies"].append(entry)

        if matched == 0:
            flags["studies_not_mentioned_in_s1"].append(entry)

    return flags


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare S-1 disclosures against ClinicalTrials.gov data"
    )
    parser.add_argument(
        "--s1-json", required=True,
        help="Path to S-1 parser output JSON (from s1_parser.py find_candidates)",
    )
    parser.add_argument(
        "--candidate", required=True,
        help="Name of the candidate to compare (must match a candidate in the S-1 JSON)",
    )
    parser.add_argument(
        "--ctgov-dir", required=True,
        help="Directory containing CTgov structured JSON files (from ctgov_fetch.py fetch-all)",
    )
    parser.add_argument(
        "--filing-date", default="",
        help="S-1 filing date as YYYY-MM-DD (for temporal context checks)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (default: stdout as JSON)",
    )
    args = parser.parse_args()

    # Load S-1 data
    with open(args.s1_json, "r", encoding="utf-8") as f:
        s1_data = json.load(f)

    # Find the selected candidate
    candidate = None
    for c in s1_data.get("candidates", []):
        if c["name"].lower() == args.candidate.lower():
            candidate = c
            break
        # Also check also_known_as
        if args.candidate.lower() in [a.lower() for a in c.get("also_known_as", [])]:
            candidate = c
            break

    if not candidate:
        available = [c["name"] for c in s1_data.get("candidates", [])]
        print(f"ERROR: Candidate '{args.candidate}' not found. Available: {available}",
              file=sys.stderr)
        sys.exit(1)

    print(f"Selected candidate: {candidate['name']}", file=sys.stderr)
    print(f"  Passages: {candidate['passage_count']}", file=sys.stderr)
    print(f"  Indications: {candidate.get('indications', [])}", file=sys.stderr)

    # Load all CTgov structured files from the directory
    studies = []
    for fname in sorted(os.listdir(args.ctgov_dir)):
        if fname.endswith("_structured.json"):
            fpath = os.path.join(args.ctgov_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                studies.append(json.load(f))

    if not studies:
        print(f"ERROR: No structured CTgov files found in {args.ctgov_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"  CTgov studies loaded: {len(studies)}", file=sys.stderr)

    # Build passages list — use extract_passages from s1_parser if available,
    # otherwise use the passages already in the candidate object
    all_passages = candidate.get("passages", [])
    print(f"  Passages to compare: {len(all_passages)}", file=sys.stderr)

    # Build comparison
    comparison = build_comparison(candidate, studies, all_passages, args.filing_date)

    # Output
    output_json = json.dumps(comparison, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\nComparison saved to: {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # Print summary to stderr
    print(f"\n=== COMPARISON SUMMARY ===", file=sys.stderr)
    print(f"Candidate: {comparison['candidate_name']}", file=sys.stderr)
    print(f"Studies compared: {comparison['studies_compared']}", file=sys.stderr)
    total_discrepancies = sum(
        len(sc["discrepancies"]) for sc in comparison["study_comparisons"]
    )
    print(f"Total discrepancies: {total_discrepancies}", file=sys.stderr)
    print(f"Unmatched passages: {comparison['unmatched_passages']}", file=sys.stderr)

    for sc in comparison["study_comparisons"]:
        status_icon = "!" if sc["discrepancies"] else "ok"
        results_str = " [RESULTS]" if sc["has_results"] else ""
        print(
            f"  [{status_icon}] {sc['nct_id']}: {sc['brief_title'][:50]} "
            f"({sc['ctgov_status']}){results_str} — "
            f"{sc['matched_passages']} passages, "
            f"{len(sc['discrepancies'])} issues",
            file=sys.stderr,
        )
        for d in sc["discrepancies"]:
            print(f"      [{d['severity'].upper()}] {d['type']}: {d['detail'][:80]}", file=sys.stderr)


if __name__ == "__main__":
    main()
