"""Download the World Bank series the calculator uses into data/raw/ (one CSV per series).

    python build/fetch_data.py

Writes data/raw/wdi_<CODE>.csv (iso3, year, value), data/raw/wdi_countries.csv (iso3, name, aggregate),
data/raw/imf_weo_PCPIPCH.csv (IMF World Economic Outlook inflation, actual and forecast) and
data/raw/wdi_meta.json (series codes, API last-updated date, retrieval date). build.py reads these.
Run with --imf to refresh only the IMF file.
Only the standard library is used, so the script runs anywhere Python 3.9+ is installed.
"""
import csv
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
API = "https://api.worldbank.org/v2"
IMF = "https://www.imf.org/external/datamapper/api/v1"
IMF_ISO = {"UVK": "XKX", "WBG": "PSE"}   # IMF DataMapper codes that differ from the World Bank's

SERIES = {
    "NY.GDP.DEFL.ZS": "GDP deflator (base year varies by country)",
    "NY.GDP.DEFL.ZS.AD": "GDP deflator, linked series (base year varies by country)",
    "FP.CPI.TOTL": "Consumer price index (2010 = 100)",
    "PA.NUS.FCRF": "Official exchange rate (LCU per US$, period average)",
    "PA.NUS.ATLS": "DEC alternative conversion factor (LCU per US$)",
    "PA.NUS.PPP": "PPP conversion factor, GDP (LCU per international $)",
    # used only for the build-time unit checks and the size-of-amount warning
    "NY.GDP.MKTP.CN": "GDP (current LCU)",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.MKTP.PP.CD": "GDP, PPP (current international $)",
}


def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # the API is slow and sometimes drops connections
            print(f"   retry {i + 1} ({e})", flush=True)
            time.sleep(5 * (i + 1))
    raise SystemExit(f"Failed: {url}")


def fetch_series(code):
    rows, page, pages, updated = [], 1, 1, None
    while page <= pages:
        meta, data = get(f"{API}/country/all/indicator/{code}?format=json&per_page=20000&page={page}&source=2")
        pages, updated = int(meta["pages"]), meta.get("lastupdated", updated)
        for d in data or []:
            if d["value"] is not None and d["countryiso3code"]:
                rows.append((d["countryiso3code"], int(d["date"]), d["value"]))
        page += 1
    return sorted(rows), updated


def fetch_imf():
    """IMF World Economic Outlook: inflation, average consumer prices (annual % change), with forecasts."""
    d = get(f"{IMF}/PCPIPCH")["values"]["PCPIPCH"]
    src = get(f"{IMF}/indicators")["indicators"]["PCPIPCH"].get("source", "World Economic Outlook")
    rows = sorted((IMF_ISO.get(iso, iso), int(y), v) for iso, s in d.items() if len(iso) == 3 for y, v in s.items() if v is not None)
    with open(RAW / "imf_weo_PCPIPCH.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["iso3", "year", "value"])
        w.writerows(rows)
    (RAW / "imf_meta.json").write_text(json.dumps({"retrieved": dt.date.today().isoformat(), "source": src,
                                                   "series": "PCPIPCH", "values": len(rows)}, indent=1), encoding="utf-8")
    print(f"IMF PCPIPCH: {len(rows)} values ({src})")


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    fetch_imf()
    if "--imf" in sys.argv:
        return
    meta, cdata = get(f"{API}/country?format=json&per_page=400")
    with open(RAW / "wdi_countries.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["iso3", "name", "aggregate"])
        for c in cdata:
            w.writerow([c["id"], c["name"].strip(), "Yes" if c["region"]["value"] == "Aggregates" else "No"])
    info = {"retrieved": dt.date.today().isoformat(), "source": "World Bank, World Development Indicators (API v2, source 2)", "series": {}}
    for code, label in SERIES.items():
        print(f"{code} ...", flush=True)
        rows, updated = fetch_series(code)
        with open(RAW / f"wdi_{code}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["iso3", "year", "value"])
            w.writerows(rows)
        info["series"][code] = {"label": label, "lastupdated": updated, "values": len(rows)}
        print(f"   {len(rows)} values, last updated {updated}", flush=True)
    (RAW / "wdi_meta.json").write_text(json.dumps(info, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
