#!/usr/bin/env python3
"""
ctgov_fetch.py — Search and download study records from ClinicalTrials.gov API v2.

Usage:
    # Search for studies by drug name (returns summary list)
    python scripts/ctgov_fetch.py search --drug izokibep
    python scripts/ctgov_fetch.py search --drug izokibep --sponsor "ACELYRIN"

    # Download full study records by NCT ID
    python scripts/ctgov_fetch.py fetch --nct NCT05355805
    python scripts/ctgov_fetch.py fetch --nct NCT05355805 --nct NCT05623345
"""

import argparse
import json
import os
import sys
import time

import requests

CTGOV_API_BASE = "https://clinicaltrials.gov/api/v2/studies"
RATE_LIMIT_DELAY = 1.0  # 1 request per second max


def _safe_get(obj, *keys, default=None):
    """Navigate nested dicts/lists safely."""
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        elif isinstance(current, list) and isinstance(key, int) and key < len(current):
            current = current[key]
        else:
            return default
        if current is None:
            return default
    return current


def fetch_study(nct_id: str, output_dir: str = ".") -> dict:
    """Fetch a full study record from ClinicalTrials.gov API v2.

    Returns a summary dict with key metadata and paths to saved files.
    """
    url = f"{CTGOV_API_BASE}/{nct_id}"
    headers = {"Accept": "application/json"}

    time.sleep(RATE_LIMIT_DELAY)
    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        # Retry once after 3 seconds
        print(f"Request failed for {nct_id}, retrying in 3s: {e}", file=sys.stderr)
        time.sleep(3)
        resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code == 404:
        return {"error": f"Study {nct_id} not found on ClinicalTrials.gov. Verify the NCT number."}
    if resp.status_code in (500, 503):
        print(f"Server error {resp.status_code} for {nct_id}, retrying in 3s...", file=sys.stderr)
        time.sleep(3)
        resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    raw_data = resp.json()

    # Save raw JSON
    raw_path = os.path.join(output_dir, f"ctgov_{nct_id}.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)

    # Check results availability
    results_section = raw_data.get("resultsSection")
    has_results = results_section is not None and bool(results_section)

    # Extract structured fields
    structured = _extract_structured(raw_data, has_results)

    # Save structured extraction
    structured_path = os.path.join(output_dir, f"ctgov_{nct_id}_structured.json")
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    return {
        "nct_id": nct_id,
        "brief_title": structured["identification"]["brief_title"],
        "overall_status": structured["status"]["overall_status"],
        "has_results": has_results,
        "sponsor": structured["sponsor"]["name"],
        "raw_file": raw_path,
        "structured_file": structured_path,
    }


def _extract_structured(data: dict, has_results: bool) -> dict:
    """Extract key fields from CTgov API v2 JSON into structured format."""
    proto = data.get("protocolSection", {})

    # Identification
    id_mod = proto.get("identificationModule", {})
    identification = {
        "nct_id": id_mod.get("nctId", ""),
        "brief_title": id_mod.get("briefTitle", ""),
        "official_title": id_mod.get("officialTitle", ""),
    }

    # Status
    status_mod = proto.get("statusModule", {})
    status = {
        "overall_status": status_mod.get("overallStatus", ""),
        "start_date": _safe_get(status_mod, "startDateStruct", "date", default=""),
        "completion_date": _safe_get(status_mod, "completionDateStruct", "date", default=""),
        "last_update_date": _safe_get(status_mod, "lastUpdatePostDateStruct", "date", default=""),
    }

    # Design
    design_mod = proto.get("designModule", {})
    design_info = design_mod.get("designInfo", {})
    masking_info = design_info.get("maskingInfo", {})
    enrollment_info = design_mod.get("enrollmentInfo", {})
    design = {
        "study_type": design_mod.get("studyType", ""),
        "phases": design_mod.get("phases", []),
        "allocation": design_info.get("allocation", ""),
        "intervention_model": design_info.get("interventionModel", ""),
        "masking": masking_info.get("masking", ""),
        "who_masked": masking_info.get("whoMasked", []),
        "enrollment_count": enrollment_info.get("count"),
        "enrollment_type": enrollment_info.get("type", ""),
    }

    # Arms & Interventions
    ai_mod = proto.get("armsInterventionsModule", {})
    arm_groups = ai_mod.get("armGroups", [])
    interventions = ai_mod.get("interventions", [])
    arms_interventions = {
        "arm_groups": [
            {
                "label": ag.get("label", ""),
                "type": ag.get("type", ""),
                "description": ag.get("description", ""),
                "intervention_names": ag.get("interventionNames", []),
            }
            for ag in arm_groups
        ],
        "interventions": [
            {
                "type": iv.get("type", ""),
                "name": iv.get("name", ""),
                "description": iv.get("description", ""),
            }
            for iv in interventions
        ],
    }

    # Endpoints (protocol-defined)
    outcomes_mod = proto.get("outcomesModule", {})
    primary_outcomes = [
        {
            "measure": o.get("measure", ""),
            "description": o.get("description", ""),
            "time_frame": o.get("timeFrame", ""),
        }
        for o in outcomes_mod.get("primaryOutcomes", [])
    ]
    secondary_outcomes = [
        {
            "measure": o.get("measure", ""),
            "description": o.get("description", ""),
            "time_frame": o.get("timeFrame", ""),
        }
        for o in outcomes_mod.get("secondaryOutcomes", [])
    ]

    # Eligibility
    elig_mod = proto.get("eligibilityModule", {})
    eligibility = {
        "criteria": elig_mod.get("eligibilityCriteria", ""),
        "sex": elig_mod.get("sex", ""),
        "minimum_age": elig_mod.get("minimumAge", ""),
        "maximum_age": elig_mod.get("maximumAge", ""),
        "healthy_volunteers": elig_mod.get("healthyVolunteers", ""),
    }

    # Sponsor
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
    lead_sponsor = sponsor_mod.get("leadSponsor", {})
    sponsor = {
        "name": lead_sponsor.get("name", ""),
        "class": lead_sponsor.get("class", ""),
    }

    structured = {
        "identification": identification,
        "status": status,
        "design": design,
        "arms_interventions": arms_interventions,
        "primary_outcomes": primary_outcomes,
        "secondary_outcomes": secondary_outcomes,
        "eligibility": eligibility,
        "sponsor": sponsor,
        "has_results": has_results,
    }

    # Results section (only if results are posted)
    if has_results:
        results = data.get("resultsSection", {})
        structured["results"] = _extract_results(results)

    return structured


def _extract_results(results: dict) -> dict:
    """Extract results section fields."""
    # Participant Flow
    flow_mod = results.get("participantFlowModule", {})
    participant_flow = {
        "groups": flow_mod.get("groups", []),
        "periods": flow_mod.get("periods", []),
    }

    # Baseline Characteristics
    baseline_mod = results.get("baselineCharacteristicsModule", {})
    baseline = {
        "groups": baseline_mod.get("groups", []),
        "denoms": baseline_mod.get("denoms", []),
        "measures": baseline_mod.get("measures", []),
    }

    # Outcome Measures
    outcome_mod = results.get("outcomeMeasuresModule", {})
    outcome_measures = []
    for om in outcome_mod.get("outcomeMeasures", []):
        outcome = {
            "type": om.get("type", ""),
            "title": om.get("title", ""),
            "description": om.get("description", ""),
            "population_description": om.get("populationDescription", ""),
            "reporting_status": om.get("reportingStatus", ""),
            "groups": om.get("groups", []),
            "denoms": om.get("denoms", []),
            "classes": om.get("classes", []),
            "analyses": om.get("analyses", []),
        }
        outcome_measures.append(outcome)

    # Adverse Events
    ae_mod = results.get("adverseEventsModule", {})
    adverse_events = {
        "frequency_threshold": ae_mod.get("frequencyThreshold", ""),
        "time_frame": ae_mod.get("timeFrame", ""),
        "description": ae_mod.get("description", ""),
        "event_groups": ae_mod.get("eventGroups", []),
        "serious_events": ae_mod.get("seriousEvents", []),
        "other_events": ae_mod.get("otherEvents", []),
    }

    return {
        "participant_flow": participant_flow,
        "baseline": baseline,
        "outcome_measures": outcome_measures,
        "adverse_events": adverse_events,
    }


def search_by_name(
    drug_name: str,
    max_results: int = 50,
    sponsor_filter: str = None,
) -> list[dict]:
    """Search ClinicalTrials.gov for studies involving a drug/intervention name.

    Uses the API v2 query.intr parameter. Returns a list of study summaries
    (no full download — caller picks NCTs to fetch in full).

    Args:
        drug_name: Drug or intervention name to search for (e.g. "izokibep").
        max_results: Max number of studies to return (default 50).
        sponsor_filter: Optional sponsor name to narrow results.

    Returns:
        List of dicts with: nct_id, brief_title, overall_status, phases,
        enrollment, sponsor, conditions, interventions, start_date, has_results.
    """
    params = {
        "query.intr": drug_name,
        "pageSize": min(max_results, 100),
        "format": "json",
    }
    if sponsor_filter:
        params["query.spons"] = sponsor_filter

    headers = {"Accept": "application/json"}
    url = CTGOV_API_BASE

    time.sleep(RATE_LIMIT_DELAY)
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as e:
        print(f"Search request failed, retrying in 3s: {e}", file=sys.stderr)
        time.sleep(3)
        resp = requests.get(url, params=params, headers=headers, timeout=30)

    resp.raise_for_status()
    data = resp.json()

    studies = data.get("studies", [])
    results = []
    for study in studies:
        proto = study.get("protocolSection", {})
        id_mod = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        design_mod = proto.get("designModule", {})
        sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
        cond_mod = proto.get("conditionsModule", {})
        ai_mod = proto.get("armsInterventionsModule", {})

        enrollment_info = design_mod.get("enrollmentInfo", {})
        lead_sponsor = sponsor_mod.get("leadSponsor", {})
        has_results = study.get("hasResults", False)

        # Extract intervention names
        intervention_names = []
        for iv in ai_mod.get("interventions", []):
            intervention_names.append(iv.get("name", ""))

        results.append({
            "nct_id": id_mod.get("nctId", ""),
            "brief_title": id_mod.get("briefTitle", ""),
            "overall_status": status_mod.get("overallStatus", ""),
            "phases": design_mod.get("phases", []),
            "enrollment": enrollment_info.get("count"),
            "enrollment_type": enrollment_info.get("type", ""),
            "sponsor": lead_sponsor.get("name", ""),
            "conditions": cond_mod.get("conditions", []),
            "interventions": intervention_names,
            "start_date": _safe_get(status_mod, "startDateStruct", "date", default=""),
            "completion_date": _safe_get(status_mod, "completionDateStruct", "date", default=""),
            "has_results": has_results,
        })

    return results


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ClinicalTrials.gov study fetcher (API v2)"
    )
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # fetch action — download full study records by NCT ID
    fetch_parser = subparsers.add_parser("fetch", help="Download full study record(s)")
    fetch_parser.add_argument(
        "--nct", required=True, action="append",
        help="NCT number(s) to fetch (can specify multiple)",
    )
    fetch_parser.add_argument(
        "--output-dir", default=".",
        help="Directory to save JSON files (default: current directory)",
    )

    # search action — search for studies by drug name
    search_parser = subparsers.add_parser("search", help="Search studies by drug/intervention name")
    search_parser.add_argument(
        "--drug", required=True, help="Drug/intervention name to search for",
    )
    search_parser.add_argument(
        "--sponsor", default=None, help="Optional sponsor name to filter by",
    )
    search_parser.add_argument(
        "--max-results", type=int, default=50,
        help="Maximum number of results (default: 50)",
    )

    args = parser.parse_args()

    if args.action == "fetch":
        os.makedirs(args.output_dir, exist_ok=True)
        results = []
        for nct_id in args.nct:
            nct_id = nct_id.strip().upper()
            print(f"Fetching {nct_id}...", file=sys.stderr)
            result = fetch_study(nct_id, args.output_dir)
            results.append(result)
            if "error" in result:
                print(f"  ERROR: {result['error']}", file=sys.stderr)
            else:
                status = "POSTED" if result["has_results"] else "NOT YET POSTED"
                print(f"  {result['brief_title']}", file=sys.stderr)
                print(f"  Status: {result['overall_status']} | Results: {status}", file=sys.stderr)
        print(json.dumps(results, indent=2))

    elif args.action == "search":
        print(f"Searching ClinicalTrials.gov for: {args.drug}", file=sys.stderr)
        if args.sponsor:
            print(f"  Sponsor filter: {args.sponsor}", file=sys.stderr)
        results = search_by_name(args.drug, args.max_results, args.sponsor)
        print(f"  Found {len(results)} studies", file=sys.stderr)
        for r in results:
            status_str = r['overall_status']
            results_str = " [HAS RESULTS]" if r['has_results'] else ""
            print(f"  {r['nct_id']}: {r['brief_title'][:70]} ({status_str}){results_str}", file=sys.stderr)
        print(json.dumps(results, indent=2))

    else:
        # Backward-compatible: if no subcommand, treat --nct as fetch
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
