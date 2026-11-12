"""Build Cost_Converter.html (and the GitHub Pages copy) from the raw data and the app template.

    python build/fetch_data.py      # once per data refresh: World Bank WDI + IMF WEO -> data/raw/
    python build/build.py           # this script
    python build/build_workbook.py  # the Excel workings

Steps
  1. Read data/raw (WDI series, IMF WEO inflation, OECD PPPs) and data/currency_history.csv.
  2. Put every money series into the unit of the World Bank national accounts. The World Bank's
     alternative conversion factor (PA.NUS.ATLS) equals GDP in LCU / GDP in US$ exactly, so it is the
     unit reference: the official rate (PA.NUS.FCRF) is published in the currency of each year and is
     divided by the redenomination factor that matches its ratio to ATLS (euro changeovers, Bulgaria,
     Croatia, Venezuela, ...). Dollarised economies and economies with US-dollar accounts use 1.
  3. Splice the linked GDP deflator (NY.GDP.DEFL.ZS.AD, which removes rebasing breaks) back to earlier
     years with the growth of the standard series, and list the break years of the standard series.
  4. Unit tests (the build stops on failure) and DATA_QUALITY.md.
  5. Inline data, version and fonts into build/app_template.html.
"""
import base64
import csv
import datetime as dt
import json
import math
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import pycountry
from babel.numbers import get_territory_currencies

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "data" / "raw"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "dev"
TODAY = dt.date.today()

WDI = {"gdpd": "NY.GDP.DEFL.ZS", "gdpd_ad": "NY.GDP.DEFL.ZS.AD", "cpi": "FP.CPI.TOTL",
       "fx_off": "PA.NUS.FCRF", "fx_alt": "PA.NUS.ATLS", "ppp": "PA.NUS.PPP",
       "gdp": "NY.GDP.MKTP.CN", "gdp_usd": "NY.GDP.MKTP.CD", "gdp_ppp": "NY.GDP.MKTP.PP.CD"}
OECD_SHEET = "5 Annual Purchasing Power"
WEO_FROM = 2015            # IMF WEO inflation rates kept from this year (used only after the last data year)
BREAK = math.log(1.10)     # standard vs linked deflator growth differing by more than 10% = a rebasing break
GAP = math.log(1.10)       # official vs alternative exchange rate differing by more than 10%


# ---------------------------------------------------------------------------------------------- reading
def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_series(path):
    out = defaultdict(dict)
    for r in read_csv(path):
        if r["value"] not in ("", None):
            out[r["iso3"]][int(r["year"])] = float(r["value"])
    return dict(out)


def oecd_csv():
    """OECD PPPs (PPP_B1GQ) as iso3,year,value. Extracted once from the Dataset Finder export."""
    out = RAW / "oecd_ppp_gdp.csv"
    if not out.exists():
        import pandas as pd
        xlsx = sorted((ROOT / "data").glob("Cost_Converter_inputs_*.xlsx"))[-1]
        o = pd.read_excel(xlsx, sheet_name=OECD_SHEET)
        o = o[(o["TRANSACTION"] == "PPP_B1GQ") & ~o["REF_AREA"].isin(["DEU_F", "EA20", "EU"])].dropna(subset=["OBS_VALUE"])
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["iso3", "year", "value"])
            for a, y, v in sorted(zip(o["REF_AREA"], o["TIME_PERIOD"], o["OBS_VALUE"])):
                w.writerow([a, int(y), repr(float(v))])
        (RAW / "oecd_meta.json").write_text(json.dumps({"source": "OECD Data Explorer, PPPs and exchange rates (annual)",
                                                         "transaction": "PPP_B1GQ", "extracted_from": xlsx.name}, indent=1))
    return read_series(out)


def history():
    rows = read_csv(ROOT / "data" / "currency_history.csv")
    by = defaultdict(list)
    for r in rows:
        r["old_per_new"] = float(r["old_per_new"]) if r["old_per_new"] else None
        r["year"] = int(r["year"]) if r["year"] else None
        r["month"] = int(r["month"]) if r["month"] else None
        by[r["iso3"]].append(r)
    return by


# ---------------------------------------------------------------------------------------------- units
def chain_factor(entries, code):
    """Units of `code` per unit of the country's current currency (follows old -> new links)."""
    f, seen = 1.0, set()
    while code not in seen:
        seen.add(code)
        nxt = [e for e in entries if e["old"] == code and e["kind"] in ("euro", "redenom") and e["old_per_new"]]
        if not nxt:
            break
        f *= nxt[0]["old_per_new"]
        code = nxt[0]["new"]
    return f


def candidates(entries, y):
    """Possible factors between a year-y value published 'in the currency of the time' and today's unit."""
    later = sorted((e for e in entries if e["kind"] in ("euro", "redenom") and e["year"] and e["year"] > y),
                   key=lambda e: -e["year"])
    out, f = [1.0], 1.0
    for e in later:
        f *= e["old_per_new"]
        out.append(f)
    return out


def to_unit(name, iso, s, ref, entries, log):
    """Divide each year's value by the candidate factor closest (in logs) to its ratio to the reference."""
    out, chosen = {}, {}
    for y, v in s.items():
        c = candidates(entries, y)
        if len(c) == 1:
            out[y] = v
            continue
        if y in ref and ref[y] > 0 and v > 0:
            r = math.log(v / ref[y])
            k = min(c, key=lambda f: abs(r - math.log(f)))
            chosen[y] = k
    for y, v in s.items():
        c = candidates(entries, y)
        if len(c) == 1:
            continue
        if y not in chosen:   # no reference value that year: same decision as the nearest year with the same candidates
            near = sorted((abs(z - y), z) for z in chosen if candidates(entries, z) == c)
            chosen[y] = chosen[near[0][1]] if near else 1.0
            if not near:
                log.append(f"{name} {iso} {y}: no reference value; left as published")
        out[y] = v / chosen[y]
    conv = sorted(y for y, k in chosen.items() if k != 1.0)
    if conv:
        ks = sorted({chosen[y] for y in conv})
        log.append(f"{name} {iso}: {conv[0]}-{conv[-1]} ({len(conv)} years) divided by "
                   + ", ".join(f"{k:g}" for k in ks))
    return out


# ---------------------------------------------------------------------------------------------- deflator
def splice(linked, std):
    """Linked series where published; earlier/later years follow the standard series' growth."""
    if not linked:
        return dict(std)
    out = dict(linked)
    y = min(linked)
    while y - 1 in std and y in std and y in out:
        out[y - 1] = out[y] * std[y - 1] / std[y]
        y -= 1
    y = max(linked)
    while y + 1 in std and y in std and y in out:
        out[y + 1] = out[y] * std[y + 1] / std[y]
        y += 1
    return out


def breaks(std, linked_raw):
    out = []
    for y in sorted(std):
        if y - 1 in std and y in linked_raw and y - 1 in linked_raw:
            d = math.log(std[y] / std[y - 1]) - math.log(linked_raw[y] / linked_raw[y - 1])
            if abs(d) > BREAK:
                out.append((y, std[y] / std[y - 1] - 1, linked_raw[y] / linked_raw[y - 1] - 1))
    return out


# ---------------------------------------------------------------------------------------------- countries
ALIASES = {  # extra names people type for World Bank country names
    "USA": ["US", "United States of America", "America"], "GBR": ["UK", "Britain", "Great Britain", "England"],
    "VNM": ["Vietnam"], "KOR": ["South Korea", "Korea"], "PRK": ["North Korea"], "RUS": ["Russia"],
    "IRN": ["Iran"], "EGY": ["Egypt"], "TUR": ["Turkey"], "LAO": ["Laos"], "SYR": ["Syria"],
    "VEN": ["Venezuela"], "BOL": ["Bolivia"], "TZA": ["Tanzania"], "CZE": ["Czech Republic"],
    "CIV": ["Ivory Coast"], "COD": ["DRC", "DR Congo", "Democratic Republic of the Congo"],
    "COG": ["Republic of the Congo"], "KGZ": ["Kyrgyzstan"], "SVK": ["Slovakia"], "GMB": ["Gambia"],
    "BHS": ["Bahamas"], "YEM": ["Yemen"], "FSM": ["Micronesia"], "HKG": ["Hong Kong"], "MAC": ["Macau", "Macao"],
    "SWZ": ["Swaziland"], "MKD": ["Macedonia"], "MDA": ["Moldova"], "CPV": ["Cape Verde"], "STP": ["Sao Tome"],
    "LCA": ["Saint Lucia"], "KNA": ["Saint Kitts and Nevis"], "VCT": ["Saint Vincent"], "BRN": ["Brunei"],
    "PSE": ["Palestine"], "MMR": ["Burma"], "TLS": ["East Timor"],
}


def alt_names(iso3, wb_name):
    out = set(ALIASES.get(iso3, []))
    c = pycountry.countries.get(alpha_3=iso3)
    if c:
        out.add(c.alpha_2)
        for attr in ("name", "common_name", "official_name"):
            v = getattr(c, attr, None)
            if v:
                out.add(v)
    out.discard(wb_name)
    return sorted(out)


def currency_of(iso3, entries):
    """Currency unit of the World Bank data: the end of the currency-history chain, else today's ISO code."""
    for e in entries:
        if e["kind"] in ("dollar", "usd_accounts"):
            return "USD"
    chg = [e for e in entries if e["kind"] in ("euro", "redenom") and e["year"]]
    if chg:
        return max(chg, key=lambda e: e["year"])["new"]
    c = pycountry.countries.get(alpha_3=iso3)
    if not c:
        return {"XKX": "EUR", "CHI": "GBP"}.get(iso3, "")
    day = TODAY
    try:
        cur = get_territory_currencies(c.alpha_2, start_date=day, end_date=day)
    except Exception:
        cur = []
    return cur[0] if cur else ""


# ---------------------------------------------------------------------------------------------- load
def load():
    """Everything both builds need: names, processed series (in the World Bank data unit), history, log."""
    countries = read_csv(RAW / "wdi_countries.csv")
    names = {r["iso3"]: r["name"].strip() for r in countries}
    agg = {r["iso3"] for r in countries if r["aggregate"] == "Yes"}
    raw = {k: read_series(RAW / f"wdi_{code}.csv") for k, code in WDI.items()}
    raw["ppp_oecd"] = oecd_csv()
    raw["weo"] = read_series(RAW / "imf_weo_PCPIPCH.csv")
    hist = history()
    log = []

    isos = sorted((c for c in names if c not in agg and (c in raw["gdpd"] or c in raw["cpi"])), key=lambda c: names[c])
    S = {k: {} for k in ("gdpd", "gdpd_l", "cpi", "fx", "fx_alt", "ppp", "ppp_oecd", "gdp", "weo", "oldfx")}
    brk = {}
    for iso in isos:
        ent = hist.get(iso, [])
        kinds = {e["kind"] for e in ent}
        alt = raw["fx_alt"].get(iso, {})
        std, lk = raw["gdpd"].get(iso, {}), raw["gdpd_ad"].get(iso, {})
        if std:
            S["gdpd"][iso] = std
            S["gdpd_l"][iso] = splice(lk, std)
            b = breaks(std, lk)
            if b:
                brk[iso] = b
        elif lk:
            S["gdpd_l"][iso] = dict(lk)
        if iso in raw["cpi"]:
            S["cpi"][iso] = raw["cpi"][iso]
        if alt:
            S["fx_alt"][iso] = alt
        off = raw["fx_off"].get(iso, {})
        if kinds & {"dollar", "usd_accounts"}:
            # national accounts in US dollars: 1 US$ per US$; the local currency goes through `oldfx`
            S["fx"][iso] = {y: alt.get(y, 1.0) for y in sorted(set(off) | set(alt))}
            if "usd_accounts" in kinds:
                src = raw["fx_off"].get("ISR", {}) if iso == "PSE" else off
                S["oldfx"][iso] = dict(src)
            else:
                e = next(e for e in ent if e["kind"] == "dollar")
                last = max(set(off) | set(alt))
                S["oldfx"][iso] = {y: (v if y < e["year"] else e["old_per_new"]) for y, v in off.items() if y < e["year"]}
                S["oldfx"][iso].update({y: e["old_per_new"] for y in range(e["year"], last + 1)})
            log.append(f"fx {iso}: national accounts in US dollars; official rate set to 1 (the local currency uses its own rate)")
        elif off:
            S["fx"][iso] = to_unit("fx", iso, off, alt, ent, log)
        if iso in raw["ppp"]:
            S["ppp"][iso] = raw["ppp"][iso]
        if iso in raw["ppp_oecd"]:
            S["ppp_oecd"][iso] = to_unit("ppp_oecd", iso, raw["ppp_oecd"][iso], raw["ppp"].get(iso, {}), ent, log)
        if iso in raw["gdp"]:
            S["gdp"][iso] = raw["gdp"][iso]
        if iso in raw["weo"]:
            S["weo"][iso] = {y: v for y, v in raw["weo"][iso].items() if y >= WEO_FROM}
    return {"names": names, "isos": isos, "raw": raw, "S": S, "hist": hist, "breaks": brk, "log": log}


# ---------------------------------------------------------------------------------------------- tests
def unit_tests(D):
    """Fail the build if any money series is not in the unit of the national accounts (appraisal C2)."""
    raw, S = D["raw"], D["S"]
    fails, notes = [], defaultdict(list)
    tens = [10.0 ** k for k in range(2, 15)]   # an undocumented redenomination would show as a power of ten

    for iso in D["isos"]:
        own = D["hist"].get(iso, [])
        factors = tens + [f for f in candidates(own, 0)[1:] if abs(math.log(f)) > math.log(1.5)]

        def near_factor(r):
            return next((f for f in factors if abs(abs(math.log(r)) - abs(math.log(f))) < math.log(1.03)), None)

        cn, cd, pp = (raw[k].get(iso, {}) for k in ("gdp", "gdp_usd", "gdp_ppp"))
        # (a) alternative rate = GDP-implied rate, every year
        for y, v in S["fx_alt"].get(iso, {}).items():
            if y in cn and y in cd and cd[y]:
                r = v / (cn[y] / cd[y])
                if abs(math.log(r)) > math.log(1.02):
                    fails.append(f"fx_alt {iso} {y}: {r:.4f} x GDP-implied")
        # (b) official rate, after conversion, must not differ from the alternative rate by a currency factor
        for y, v in S["fx"].get(iso, {}).items():
            a = S["fx_alt"].get(iso, {}).get(y)
            if a:
                r = v / a
                f = near_factor(r)
                if f:
                    fails.append(f"fx {iso} {y}: official / alternative = {r:.5g}, a currency factor ({f:g})")
                elif abs(math.log(r)) > GAP:
                    notes["gap"].append((iso, y, r))
        # (c) PPP = GDP-implied PPP for the years since the ICP 2021 benchmark; earlier differences reported
        for y, v in S["ppp"].get(iso, {}).items():
            if y in cn and y in pp and pp[y]:
                r = v / (cn[y] / pp[y])
                if near_factor(r):
                    fails.append(f"ppp {iso} {y}: {r:.5g} x GDP-implied, a currency factor")
                elif abs(math.log(r)) > math.log(1.02):
                    if y >= 2022:
                        fails.append(f"ppp {iso} {y}: {r:.4f} x GDP-implied")
                    else:
                        notes["ppp_old"].append((iso, y, r))
        # (d) OECD PPP vs World Bank PPP: no currency factor between them
        for y, v in S["ppp_oecd"].get(iso, {}).items():
            w = S["ppp"].get(iso, {}).get(y)
            if w:
                r = v / w
                if near_factor(r):
                    fails.append(f"ppp_oecd {iso} {y}: {r:.5g} x World Bank PPP, a currency factor")
                elif abs(math.log(r)) > math.log(1.10):
                    notes["oecd"].append((iso, y, r))
    return fails, notes


# ---------------------------------------------------------------------------------------------- report
def ranges(years):
    years = sorted(years)
    out, start = [], None
    for i, y in enumerate(years):
        if start is None:
            start = y
        if i == len(years) - 1 or years[i + 1] != y + 1:
            out.append(f"{start}" if start == y else f"{start}-{y}")
            start = None
    return ", ".join(out)


def report(D, notes, meta):
    names, S = D["names"], D["S"]
    L = [f"# Data quality report", "",
         f"Health Cost Converter {VERSION}, built {TODAY.isoformat()} from World Development Indicators "
         f"(last updated {meta['wdi_updated']}), IMF World Economic Outlook ({meta['weo']}) and OECD PPPs.", "",
         "This file is written by `build/build.py` at every build. The build stops if a unit test fails.", "",
         "## Unit tests (all passed)", "",
         "* The alternative conversion factor (PA.NUS.ATLS) equals GDP in LCU / GDP in US$ within 2% for every economy and year.",
         "* After the currency-history conversion, no official rate differs from the alternative rate by a redenomination factor.",
         "* World Bank PPPs equal GDP in LCU / GDP in PPP international dollars within 2% for every economy, 2022 onwards.",
         "* OECD PPPs never differ from World Bank PPPs by a redenomination factor.", "",
         "## Currency conversions applied", "",
         "Official exchange rates are published in the currency of each year; GDP, deflators and PPPs are in today's "
         "unit. These conversions were applied (see `data/currency_history.csv`):", ""]
    L += [f"* {x}" for x in D["log"] if "divided" in x or "US dollars" in x]
    L += ["", "## GDP deflator rebasing breaks", "",
          "The standard GDP deflator (NY.GDP.DEFL.ZS) jumps where a country rebased its national accounts. "
          "The app uses the linked series (NY.GDP.DEFL.ZS.AD) by default; the years below are flagged when the standard series is chosen.", "",
          f"{len(D['breaks'])} economies have at least one year where the two series' growth differs by more than 10%.", "",
          "| Economy | Year (standard vs linked growth) |", "|---|---|"]
    for iso in sorted(D["breaks"], key=lambda c: names[c]):
        L.append(f"| {names[iso]} | " + "; ".join(f"{y} ({a:+.0%} vs {b:+.0%})" for y, a, b in D["breaks"][iso]) + " |")
    gap = defaultdict(list)
    for iso, y, r in notes["gap"]:
        gap[iso].append((y, r))
    L += ["", "## Official vs alternative exchange rate", "",
          "Years where the official rate differs from the World Bank's alternative conversion factor by more than 10% "
          "(multiple or unrepresentative official rates). The app warns in these years and offers the alternative rate.", "",
          "| Economy | Years | Official / alternative |", "|---|---|---|"]
    for iso in sorted(gap, key=lambda c: names[c]):
        rs = [r for _, r in gap[iso]]
        L.append(f"| {names[iso]} | {ranges([y for y, _ in gap[iso]])} | {min(rs):.3g} to {max(rs):.3g} |")
    last = max(max(s) for s in S["fx_alt"].values())
    L += ["", "## Stale series", "",
          f"Series whose last value is more than 3 years before {last}. The app does not project these.", "",
          "| Economy | Series | Last year |", "|---|---|---|"]
    lab = {"gdpd_l": "GDP deflator", "cpi": "CPI", "fx": "Official exchange rate", "fx_alt": "Alternative conversion factor", "ppp": "PPP (World Bank)"}
    for iso in D["isos"]:
        for k, nm in lab.items():
            s = S[k].get(iso)
            if s and max(s) < last - 3:
                L.append(f"| {names[iso]} | {nm} | {max(s)} |")
    old = defaultdict(list)
    for iso, y, r in notes["ppp_old"]:
        old[iso].append((y, r))
    L += ["", "## PPP vs GDP before 2022 (not unit errors)", "",
          "In these years the World Bank PPP differs from GDP in LCU / GDP in PPP dollars by more than 2%. The ratios are "
          "constant over runs of years and match national-accounts rebasing (GDP levels were revised, PPPs were not). "
          "They are listed for transparency; the app uses the published PPPs.", "",
          "| Economy | Years | Ratio |", "|---|---|---|"]
    for iso in sorted(old, key=lambda c: names[c]):
        rs = [r for _, r in old[iso]]
        L.append(f"| {names[iso]} | {ranges([y for y, _ in old[iso]])} | {min(rs):.3g} to {max(rs):.3g} |")
    oe = defaultdict(list)
    for iso, y, r in notes["oecd"]:
        oe[iso].append((y, r))
    L += ["", "## OECD vs World Bank PPP differing by more than 10%", "", "| Economy | Years | OECD / World Bank |", "|---|---|---|"]
    for iso in sorted(oe, key=lambda c: names[c]):
        rs = [r for _, r in oe[iso]]
        L.append(f"| {names[iso]} | {ranges([y for y, _ in oe[iso]])} | {min(rs):.3g} to {max(rs):.3g} |")
    L += ["", "## Other notes", ""] + [f"* {x}" for x in D["log"] if not ("divided" in x or "US dollars" in x)] + [""]
    (ROOT / "DATA_QUALITY.md").write_text("\n".join(L), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------------------------- page
def sig(v, n=8):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return float(f"{v:.{n}g}")


def pack(series, isos, n=8):
    out = {}
    for iso in isos:
        s = series.get(iso)
        if not s:
            continue
        y0, y1 = min(s), max(s)
        out[iso] = [y0, [sig(s.get(y), n) for y in range(y0, y1 + 1)]]
    return out


def fonts_css():
    """Self-hosted fonts (SIL Open Font License) inlined as data URIs; falls back to system fonts if absent."""
    spec = HERE / "fonts" / "fonts.json"
    if not spec.exists():
        print("   fonts: build/fonts/fonts.json missing, using system fonts")
        return ""
    css = []
    for f in json.loads(spec.read_text(encoding="utf-8")):
        b64 = base64.b64encode((HERE / "fonts" / f["file"]).read_bytes()).decode("ascii")
        css.append(f"@font-face {{ font-family: \"{f['family']}\"; font-style: {f['style']}; font-weight: {f['weight']}; "
                   f"font-display: swap; src: url(data:font/woff2;base64,{b64}) format(\"woff2\"); "
                   f"unicode-range: {f['range']}; }}")
    return "\n".join(css)


def main():
    D = load()
    fails, notes = unit_tests(D)
    if fails:
        print(f"UNIT TESTS FAILED ({len(fails)}):")
        print("\n".join("   " + f for f in fails[:60]))
        sys.exit(1)
    print("Unit tests passed.")
    wmeta = json.loads((RAW / "wdi_meta.json").read_text(encoding="utf-8"))
    imeta = json.loads((RAW / "imf_meta.json").read_text(encoding="utf-8"))
    meta = {"version": VERSION, "built": TODAY.isoformat(), "wdi_updated": max(v["lastupdated"] for v in wmeta["series"].values()),
            "wdi_retrieved": wmeta["retrieved"], "weo": imeta["source"].split("(")[-1].rstrip(")"), "weo_retrieved": imeta["retrieved"]}
    report(D, notes, meta)

    names, isos, S, hist = D["names"], D["isos"], D["S"], D["hist"]
    countries = []
    for iso in isos:
        ent = hist.get(iso, [])
        cur = currency_of(iso, ent)
        old = []
        for e in sorted(ent, key=lambda e: -(e["year"] or 0)):
            if e["kind"] in ("euro", "redenom"):
                old.append({"code": e["old"], "name": e["old_name"], "per": chain_factor(ent, e["old"]),
                            "year": e["year"], "month": e["month"]})
            elif e["kind"] in ("dollar", "usd_accounts"):
                old.append({"code": e["old"], "name": e["old_name"], "rate": True, "year": e["year"]})
        note = " ".join(e["note"] for e in ent if e["note"]) or None
        countries.append({"iso": iso, "name": names[iso], "cur": cur, "alt": alt_names(iso, names[iso]),
                          "old": old or None, "note": note})
    data = {
        "meta": meta,
        "countries": countries,
        "breaks": {iso: [b[0] for b in v] for iso, v in D["breaks"].items()},
        "series": {**{k: pack(S[k], isos) for k in ("gdpd", "gdpd_l", "cpi", "fx", "fx_alt", "ppp", "ppp_oecd", "oldfx")},
                   "gdp": pack(S["gdp"], isos, 4), "weo": pack(S["weo"], isos, 4)},
    }
    print("No currency code:", [c["iso"] for c in countries if not c["cur"]])
    print("Countries:", len(countries), {k: len(v) for k, v in data["series"].items()})

    js = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    (HERE / "data.json").write_text(js, encoding="utf-8")
    tpl = (HERE / "app_template.html").read_text(encoding="utf-8")
    page = tpl.replace("/*__DATA__*/null", js).replace("__VERSION__", VERSION).replace("/*__FONTS__*/", fonts_css())
    assert page != tpl and "<!--BODY-->" in page and "/*__DATA__*/" not in page, "placeholders missing in template"
    head, body = page.split("<!--BODY-->", 1)
    standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                  f"{head}</head>\n<body>\n{body}</body>\n</html>\n")
    (ROOT / "Cost_Converter.html").write_text(standalone, encoding="utf-8", newline="\n")
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(standalone, encoding="utf-8", newline="\n")
    xl = ROOT / "Cost_Converter_Workings.xlsx"
    if xl.exists():
        shutil.copy2(xl, site / xl.name)
    print(f"Wrote Cost_Converter.html ({len(standalone) / 1024:.0f} KB) and site/index.html"
          + (" (+ workbook)" if xl.exists() else " (workbook missing: run build_workbook.py)"))


if __name__ == "__main__":
    main()
