#!/usr/bin/env python3
"""
edgar_fetch.py — Ticker → S-1/F-1 filing lookup and download from EDGAR.

Usage:
    python scripts/edgar_fetch.py --ticker SLRN --action lookup
    python scripts/edgar_fetch.py --ticker SLRN --action download --url <document_url>
"""

import argparse
import json
import os
import re
import sys
import time

import requests

HEADERS = {
    "User-Agent": "S1DisclosureChecker/1.0 (contact@example.com)",
    "Accept-Encoding": "gzip, deflate",
}

RATE_LIMIT_DELAY = 0.2  # seconds between requests (max 10 req/sec)

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
EFTS_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"


def _rate_limited_get(url, **kwargs):
    """GET with User-Agent header and rate-limit delay."""
    headers = {**HEADERS, **kwargs.pop("headers", {})}
    time.sleep(RATE_LIMIT_DELAY)
    resp = requests.get(url, headers=headers, timeout=30, **kwargs)
    if resp.status_code in (403, 429):
        print("EDGAR rate limit hit. Waiting 5 s and retrying...", file=sys.stderr)
        time.sleep(5)
        resp = requests.get(url, headers=headers, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


# ── Step 1: Ticker → CIK ─────────────────────────────────────────────

def _efts_ticker_search(ticker: str) -> dict | None:
    """Fallback: search EDGAR EFTS for a (possibly delisted) ticker.

    Returns {"cik_str": int, "ticker": str, "title": str} or None.
    """
    params = {"q": f'"{ticker}"', "forms": "S-1,F-1", "dateRange": "custom",
              "startdt": "2000-01-01", "enddt": "2099-12-31"}
    resp = _rate_limited_get(EFTS_SEARCH_URL, params=params)
    data = resp.json()
    hits = data.get("hits", {}).get("hits", [])
    ticker_upper = ticker.upper()
    for hit in hits:
        src = hit.get("_source", {})
        for display_name in src.get("display_names", []):
            # Format: "ACELYRIN, Inc.  (SLRN)  (CIK 0001962918)"
            if f"({ticker_upper})" in display_name.upper():
                cik_match = re.search(r"\(CIK\s+0*(\d+)\)", display_name)
                if cik_match:
                    cik_int = int(cik_match.group(1))
                    # Extract company name (everything before the first paren)
                    name = display_name.split("(")[0].strip()
                    return {"cik_str": cik_int, "ticker": ticker_upper, "title": name}
    return None


def ticker_to_cik(ticker: str) -> dict:
    """Return {"cik_str": int, "ticker": str, "title": str} or raise."""
    # Primary: active tickers file
    resp = _rate_limited_get(COMPANY_TICKERS_URL)
    data = resp.json()
    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry["ticker"].upper() == ticker_upper:
            return entry

    # Fallback: EFTS search (catches delisted tickers)
    print(f"Ticker {ticker} not in active list, searching EDGAR filings...",
          file=sys.stderr)
    result = _efts_ticker_search(ticker)
    if result:
        return result

    raise SystemExit(f"Ticker not found in EDGAR. Check spelling: {ticker}")


# ── Step 2–5: CIK → Filing metadata → URL ────────────────────────────

VALID_FORM_TYPES = {"S-1", "S-1/A", "F-1", "F-1/A"}


def _search_filings(recent: dict) -> int | None:
    """Return index of first S-1/F-1 variant in the recent filings, or None."""
    forms = recent.get("form", [])
    for idx, form in enumerate(forms):
        if form in VALID_FORM_TYPES:
            return idx
    return None


def lookup(ticker: str) -> dict:
    """Full lookup: ticker → filing metadata + document URL."""
    # Step 1
    entry = ticker_to_cik(ticker)
    cik_raw = entry["cik_str"]
    cik_padded = str(cik_raw).zfill(10)

    # Step 2 — fetch submission history
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    resp = _rate_limited_get(submissions_url)
    sub = resp.json()

    company_name = sub.get("name", "")
    tickers = sub.get("tickers", [])

    recent = sub.get("filings", {}).get("recent", {})
    idx = _search_filings(recent)

    # If not found in recent, check older filing index files
    if idx is None:
        older_files = sub.get("filings", {}).get("files", [])
        for older in older_files:
            older_url = f"https://data.sec.gov/submissions/{older['name']}"
            older_resp = _rate_limited_get(older_url)
            older_data = older_resp.json()
            idx = _search_filings(older_data)
            if idx is not None:
                recent = older_data
                break

    if idx is None:
        raise SystemExit(
            "No S-1 or F-1 filings found. This company may not have "
            "an IPO registration statement on file."
        )

    # Step 4 — extract metadata
    accession = recent["accessionNumber"][idx]
    filing_date = recent["filingDate"][idx]
    form_type = recent["form"][idx]
    primary_doc = recent["primaryDocument"][idx]

    # Step 5 — build document URL
    accession_no_dashes = accession.replace("-", "")
    cik_for_url = str(cik_raw)  # no leading zeros
    document_url = (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_for_url}/{accession_no_dashes}/{primary_doc}"
    )

    result = {
        "company_name": company_name,
        "cik": cik_padded,
        "tickers": tickers,
        "form_type": form_type,
        "filing_date": filing_date,
        "accession_number": accession,
        "primary_document": primary_doc,
        "document_url": document_url,
    }
    return result


# ── Action: download ──────────────────────────────────────────────────

def download(ticker: str, url: str, filing_date: str = "") -> str:
    """Download the S-1 HTML document and save locally."""
    resp = _rate_limited_get(url)
    date_part = filing_date if filing_date else str(int(time.time()))
    filename = f"s1_{ticker.upper()}_{date_part}.html"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(resp.text)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"Downloaded: {filepath} ({size_kb:.0f} KB)", file=sys.stderr)
    return filepath


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="EDGAR S-1/F-1 fetcher")
    parser.add_argument("--ticker", required=True, help="Company ticker symbol")
    parser.add_argument(
        "--action",
        required=True,
        choices=["lookup", "download"],
        help="lookup = find filing metadata; download = fetch HTML document",
    )
    parser.add_argument(
        "--url",
        help="Document URL (required for download action)",
    )
    parser.add_argument(
        "--filing-date",
        default="",
        help="Filing date for download filename (e.g. 2023-05-03)",
    )
    args = parser.parse_args()

    if args.action == "lookup":
        result = lookup(args.ticker)
        print(json.dumps(result, indent=2))

    elif args.action == "download":
        if not args.url:
            raise SystemExit("--url is required for download action")
        filepath = download(args.ticker, args.url, args.filing_date)
        print(json.dumps({"file_path": filepath}))


if __name__ == "__main__":
    main()
