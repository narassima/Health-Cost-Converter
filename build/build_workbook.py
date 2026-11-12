"""Build Cost_Converter_Workings.xlsx: the calculator as live Excel formulas, so anyone can check it.

    python build/build_workbook.py

Sheets: README, Calculator, List, Paper example, EPPI check, then the data sheets (GDPD_L, GDPD, CPI, FX, FX_raw,
FX_ALT, PPP_WB, PPP_OECD, OLDFX, IMF_WEO), Countries, CurrencyHistory and Lists. The data are the same processed
series the web page uses (build.load()). FX holds formulas that re-express FX_raw in today's currency unit where the
World Bank publishes an older one; every projected value after the last data year is a formula.
All data sheets share one layout: row = country (same order as Countries), column C = 1960 ... CB = 2037.
"""
import json
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402  (same data, currency history and unit conversions as the web app)

sys.stdout.reconfigure(encoding="utf-8")
Y_FIRST, Y_END = 1960, 2037
COL0 = 3                                   # column C = 1960
STALE = 3                                  # a series ending more than 3 years before the latest data is not projected


def ycol(y):
    return CL(COL0 + y - Y_FIRST)


C_LAST = ycol(Y_END)                       # CB
C_LY, C_TS, C_TR, C_YR, C_RU = (CL(COL0 + Y_END - Y_FIRST + i) for i in range(1, 6))   # CC..CG
INPUT = PatternFill("solid", fgColor="FFF4C2")
HEAD = PatternFill("solid", fgColor="EEF0F6")
PROJ = PatternFill("solid", fgColor="E6F4F1")
CONV = PatternFill("solid", fgColor="F1EEFB")
BOLD = Font(bold=True)
TITLE = Font(bold=True, size=14)
NOTE = Font(italic=True, color="5F6B7A")
SERIES = ["GDPD_L", "GDPD", "CPI", "FX", "FX_ALT", "PPP_WB", "PPP_OECD", "OLDFX"]
SKEY = {"GDPD_L": "gdpd_l", "GDPD": "gdpd", "CPI": "cpi", "FX": "fx", "FX_ALT": "fx_alt", "PPP_WB": "ppp", "PPP_OECD": "ppp_oecd", "OLDFX": "oldfx"}


def main():
    D = B.load()
    S, isos, names, hist = D["S"], D["isos"], D["names"], D["hist"]
    wmeta = json.loads((B.RAW / "wdi_meta.json").read_text(encoding="utf-8"))
    imeta = json.loads((B.RAW / "imf_meta.json").read_text(encoding="utf-8"))
    wdi_upd = max(v["lastupdated"] for v in wmeta["series"].values())
    weo = imeta["source"]
    n = len(isos)
    R0, R1 = 2, n + 1                       # data rows
    row_of = {iso: R0 + i for i, iso in enumerate(isos)}
    us = row_of["USA"]
    RNG = lambda sh: f"{sh}!$C${R0}:${C_LAST}${R1}"      # noqa: E731
    LASTY = lambda sh: f"{sh}!${C_LY}${R0}:${C_LY}${R1}"  # noqa: E731
    last_all = {k: max(max(s) for s in S[k].values() if s) for k in SKEY.values()}
    y_last_data = max(last_all[k] for k in ("gdpd", "cpi", "fx", "ppp"))
    weo_end = max(max(s) for s in S["weo"].values() if s)

    wb = Workbook()
    ws_readme = wb.active
    ws_readme.title = "README"
    ws_calc = wb.create_sheet("Calculator")
    ws_list = wb.create_sheet("List")
    ws_paper = wb.create_sheet("Paper example")
    ws_eppi = wb.create_sheet("EPPI check")
    sheets = {s: wb.create_sheet(s) for s in ["GDPD_L", "GDPD", "CPI", "FX", "FX_raw", "FX_ALT", "PPP_WB", "PPP_OECD", "OLDFX", "IMF_WEO"]}
    ws_c = wb.create_sheet("Countries")
    ws_h = wb.create_sheet("CurrencyHistory")
    ws_l = wb.create_sheet("Lists")

    def name(nm, ref):
        wb.defined_names[nm] = DefinedName(nm, attr_text=ref)

    # ------------------------------------------------------------------ Countries and currency history
    ws_c.append(["ISO3", "Country (World Bank name)", "Currency of the data", "Older currencies (choose under 'Amount is in')", "Note"])
    for iso in isos:
        ent = hist.get(iso, [])
        olds = ", ".join(e["old"] for e in ent if e["kind"] in ("euro", "redenom", "dollar", "usd_accounts"))
        note = " ".join(e["note"] for e in ent if e["note"]) or None
        ws_c.append([iso, names[iso], B.currency_of(iso, ent), olds or None, note])
    for c in ws_c[1]:
        c.font, c.fill = BOLD, HEAD
    for col, w in zip("ABCDE", [7, 34, 10, 30, 80]):
        ws_c.column_dimensions[col].width = w
    ws_c.freeze_panes = "C2"

    ws_h.append(["Key", "ISO3", "Old code", "Old currency", "Old units per current unit", "Changeover year", "How converted", "Source table"])
    for iso in isos:
        for e in hist.get(iso, []):
            if e["kind"] in ("euro", "redenom"):
                ws_h.append([f"{iso}|{e['old']}", iso, e["old"], e["old_name"], B.chain_factor(hist[iso], e["old"]), e["year"],
                             "fixed divisor", "data/currency_history.csv"])
            elif e["kind"] in ("dollar", "usd_accounts"):
                ws_h.append([f"{iso}|{e['old']}", iso, e["old"], e["old_name"], None, e["year"],
                             "each year's rate (OLDFX sheet)", "data/currency_history.csv"])
    h_last = ws_h.max_row
    for c in ws_h[1]:
        c.font, c.fill = BOLD, HEAD
    for col, w in zip("ABCDEFGH", [14, 7, 10, 30, 22, 14, 30, 26]):
        ws_h.column_dimensions[col].width = w
    ws_h.freeze_panes = "B2"
    HK, HPER, HHOW = (f"CurrencyHistory!${c}$2:${c}${h_last}" for c in "AEG")

    # ------------------------------------------------------------------ Lists (for dropdowns)
    lists = {
        "A": ["Years"] + list(range(Y_FIRST, Y_END + 1)),
        "B": ["Reported in", "Local currency", "US$", "I$"],
        "C": ["Output currency", "I$", "US$", "Local currency of a country"],
        "D": ["Convert with", "Market rates", "PPP"],
        "E": ["Inflation measure", "GDP deflator, linked", "GDP deflator, standard", "Consumer price index"],
        "F": ["PPP source", "World Bank", "OECD"],
        "G": ["Exchange rates from", "Official", "Alternative"],
        "H": ["Projection rule", "IMF WEO", 5, 10, 20],
        "I": ["Exchange rates after the data", "Follow inflation gap", "Hold last rate"],
        "J": ["Main method", 2, 1, 3],
    }
    for col, vals in lists.items():
        for i, v in enumerate(vals, start=1):
            ws_l[f"{col}{i}"] = v
    ws_l.sheet_state = "hidden"
    sizes = {k: len(v) - 1 for k, v in lists.items()}

    def dv(ws, ref, col):
        d = DataValidation(type="list", formula1=f"Lists!${col}$2:${col}${sizes[col] + 1}", allow_blank=True)
        ws.add_data_validation(d)
        d.add(ref)

    def dv_country(ws, ref):
        d = DataValidation(type="list", formula1=f"Countries!$B${R0}:$B${R1}", allow_blank=True)
        ws.add_data_validation(d)
        d.add(ref)

    # ------------------------------------------------------------------ Calculator inputs (names used everywhere)
    ws = ws_calc
    ws["A1"] = f"Health Cost Converter {B.VERSION}: workings"
    ws["A1"].font = TITLE
    ws["A2"] = ("Yellow cells are inputs. Every other number is a formula: select a cell and use Formulas > Trace Precedents "
                "to follow it back to the data sheets. Method: Turner et al. (2019), Value in Health 22(9):1026-1032.")
    ws["A2"].font = NOTE
    ws["A3"], ws["D3"] = "Inputs", "Derived from the inputs"
    ws["A3"].font = ws["D3"].font = BOLD
    inputs = [  # row, label, name, value, list column (or 'country' / None), number format
        (4, "Amount", "Amount", 1000000, None, "#,##0.00"),
        (5, "Reported in", "ReportedIn", "Local currency", "B", None),
        (6, "Country where the cost was incurred", "CountryS", "Viet Nam", "country", None),
        (7, "Price year of the cost", "PriceYear", 2006, "A", "0"),
        (8, "Amount is in (old currency code; blank = currency of the data)", "AmountUnit", None, None, None),
        (10, "Base year", "BaseYear", 2016, "A", "0"),
        (11, "Output currency", "OutCur", "I$", "C", None),
        (12, "Output country (if local currency)", "CountryT", "India", "country", None),
        (13, "Convert between currencies with", "ConvWith", "Market rates", "D", None),
        (14, "Inflation measure", "Measure", "GDP deflator, linked", "E", None),
        (15, "PPP values from", "PPPSource", "World Bank", "F", None),
        (16, "Exchange rates from", "FxFrom", "Official", "G", None),
        (17, "Tradable share (Method 3)", "Share", 0.2, None, "0%"),
        (18, "Main method", "MainM", 2, "J", "0"),
        (19, "Years after the data: price indices", "ProjRule", "IMF WEO", "H", None),
        (20, "Years after the data: exchange rates", "FxAfterData", "Follow inflation gap", "I", None),
    ]
    for r, label, nm, val, lst, nf in inputs:
        ws[f"A{r}"] = label
        c = ws[f"B{r}"]
        c.value, c.fill = val, INPUT
        if nf:
            c.number_format = nf
        name(nm, f"Calculator!$B${r}")
        if lst == "country":
            dv_country(ws, f"B{r}")
        elif lst:
            dv(ws, f"B{r}", lst)
    ws["A9"] = "(Old codes for each country are on the Countries and CurrencyHistory sheets, e.g. DEM for Germany, SLL for Sierra Leone.)"
    ws["A9"].font = NOTE

    derived = [
        (4, "Row of the cost country", "RowS", f"=MATCH(CountryS,Countries!$B${R0}:$B${R1},0)"),
        (5, "ISO code of the cost country", "IsoS", f"=INDEX(Countries!$A${R0}:$A${R1},RowS)"),
        (6, "Currency of the data", "CurS", f"=INDEX(Countries!$C${R0}:$C${R1},RowS)"),
        (7, "Row of the output country (USA for US$ and I$)", "RowT",
         f'=IF(OutCur="Local currency of a country",MATCH(CountryT,Countries!$B${R0}:$B${R1},0),MATCH("USA",Countries!$A${R0}:$A${R1},0))'),
        (8, "Row of the Method 1 inflation country", "RowI", "=RowT"),
        (9, "Same country in and out (inflation only)?", "Same", '=AND(OutCur="Local currency of a country",RowT=RowS)'),
        (10, "PPP series", "PPPSeries", '=IF(PPPSource="OECD","PPP_OECD","PPP_WB")'),
        (11, "Exchange-rate series", "FXSeries", '=IF(FxFrom="Alternative","FX_ALT","FX")'),
        (12, "Conversion series", "ConvSeries", '=IF(OutCur="US$",FXSeries,IF(OutCur="I$",PPPSeries,IF(ConvWith="PPP",PPPSeries,FXSeries)))'),
        (13, "Price index series", "IdxSeries", '=IF(Measure="GDP deflator, linked","GDPD_L",IF(Measure="GDP deflator, standard","GDPD","CPI"))'),
        (14, "Series to undo the study's conversion", "InSeries", '=IF(ReportedIn="US$",FXSeries,IF(ReportedIn="I$",PPPSeries,"none"))'),
        (15, "Old-currency divisor series", "OldSeries",
         f'=IF(OR(ReportedIn<>"Local currency",AmountUnit=""),"none",IF(INDEX({HHOW},MATCH(IsoS&"|"&AmountUnit,{HK},0))="fixed divisor","fixed","OLDFX"))'),
        (16, "Old-currency fixed divisor", "OldFixed",
         f'=IF(OldSeries="fixed",INDEX({HPER},MATCH(IsoS&"|"&AmountUnit,{HK},0)),1)'),
        (17, "Output currency label", "OutLabel", f'=IF(OutCur="US$","US$",IF(OutCur="I$","I$",INDEX(Countries!$C${R0}:$C${R1},RowT)))'),
        (18, "Trend years when the IMF has no forecast", "TrendYears", '=IF(ProjRule="IMF WEO",10,ProjRule)'),
    ]
    for r, label, nm, f in derived:
        ws[f"D{r}"], ws[f"E{r}"] = label, f
        name(nm, f"Calculator!$E${r}")

    # Generic lookup: value of a series for a country row and a year (#N/A when the data has no value).
    SLIST = "{" + ",".join(f'"{s}"' for s in SERIES) + "}"

    def LOOK(series, row, year):
        idx = ",".join(f"INDEX({RNG(s)},{row},{year}-{Y_FIRST}+1)" for s in SERIES)
        return f"IFERROR(1/(1/CHOOSE(MATCH({series},{SLIST},0),{idx})),NA())"

    def LASTYEAR(series, row):
        idx = ",".join(f"INDEX({LASTY(s)},{row})" for s in SERIES)
        return f"CHOOSE(MATCH({series},{SLIST},0),{idx})"

    ws["A22"] = "Values used"
    ws["A22"].font = BOLD
    ws["A23"] = ("Each value is looked up from the data sheets. Values after a series' last data year are projections "
                 "(formulas in the data sheets). Type in column H to use your own value instead.")
    ws["A23"].font = NOTE
    hdr = ["Value", "Series", "Country row", "Country", "Year", "From the data sheets", "After the last data year?", "Your value", "Value used", "Used for"]
    for i, h in enumerate(hdr):
        c = ws.cell(row=24, column=1 + i, value=h)
        c.font, c.fill = BOLD, HEAD
    vrows = [  # label, series expr, row expr, year expr, used for
        ("Rate to undo the study's conversion", "InSeries", "RowS", "PriceYear", "Back to local currency"),
        ("Old-currency rate (dollarised economies)", 'IF(OldSeries="OLDFX","OLDFX","none")', "RowS", "PriceYear", "Old currency to the data's currency"),
        ("Conversion rate, cost country, price year", "ConvSeries", "RowS", "PriceYear", "Method 1"),
        ("Conversion rate, cost country, base year", "ConvSeries", "RowS", "BaseYear", "Method 2"),
        ("Conversion rate, output country, price year", "ConvSeries", "RowT", "PriceYear", "Method 1"),
        ("Conversion rate, output country, base year", "ConvSeries", "RowT", "BaseYear", "Method 2"),
        ("Price index, cost country, price year", "IdxSeries", "RowS", "PriceYear", "Method 2 inflation"),
        ("Price index, cost country, base year", "IdxSeries", "RowS", "BaseYear", "Method 2 inflation"),
        ("Price index, Method 1 country, price year", "IdxSeries", "RowI", "PriceYear", "Method 1 inflation"),
        ("Price index, Method 1 country, base year", "IdxSeries", "RowI", "BaseYear", "Method 1 inflation"),
    ]
    vnames = ["V_in", "V_old", "V_rS0", "V_rS1", "V_rT0", "V_rT1", "V_iS0", "V_iS1", "V_iT0", "V_iT1"]
    for i, ((label, s, rw, yr, use), vn) in enumerate(zip(vrows, vnames)):
        r = 25 + i
        ws[f"A{r}"] = label
        ws[f"B{r}"] = f"={s}"
        ws[f"C{r}"] = f"={rw}"
        ws[f"D{r}"] = f"=INDEX(Countries!$B${R0}:$B${R1},C{r})"
        ws[f"E{r}"] = f"={yr}"
        ws[f"F{r}"] = f'=IF(B{r}="none",1,{LOOK(f"B{r}", f"C{r}", f"E{r}")})'
        ws[f"G{r}"] = f'=IF(B{r}="none","",IF(E{r}>{LASTYEAR(f"B{r}", f"C{r}")},"projected","data"))'
        ws[f"H{r}"].fill = INPUT
        ws[f"I{r}"] = f"=IF(ISNUMBER(H{r}),H{r},F{r})"
        ws[f"J{r}"] = use
        name(vn, f"Calculator!$I${r}")
        for col in "FHI":
            ws[f"{col}{r}"].number_format = "#,##0.000000"

    ws["A37"] = "Results"
    ws["A37"].font = BOLD
    for i, h in enumerate(["Step", "Value", "Formula"]):
        c = ws.cell(row=38, column=1 + i, value=h)
        c.font, c.fill = BOLD, HEAD
    steps = [
        ("Cost in the data's currency at price-year prices", "=Amount*V_in/OldFixed/V_old",
         "Amount × rate to undo the study's conversion ÷ old-currency divisor", "CostLocal"),
        ("Conversion factor at the price year", "=IF(Same,1,V_rT0/V_rS0)", "output-country rate ÷ cost-country rate (1 when the same country)", "ConvF0"),
        ("Conversion factor at the base year", "=IF(Same,1,V_rT1/V_rS1)", "output-country rate ÷ cost-country rate (1 when the same country)", "ConvF1"),
        ("Inflation factor, cost country", "=V_iS1/V_iS0", "price index base year ÷ price year", "InflS"),
        ("Inflation factor, Method 1 country", "=V_iT1/V_iT0", "price index base year ÷ price year (US for US$ and I$)", "InflT"),
        ("Method 1, after conversion (price-year prices)", "=CostLocal*ConvF0", "cost × conversion factor at the price year", None),
        ("METHOD 1 RESULT", "=CostLocal*ConvF0*InflT", "convert at the price year, then inflate with Method 1 country prices", "Res_M1"),
        ("Method 2, after local inflation (local currency)", "=CostLocal*InflS", "cost × local inflation factor", None),
        ("METHOD 2 RESULT", "=CostLocal*InflS*ConvF1", "inflate with local prices, then convert at the base year", "Res_M2"),
        ("Method 3, tradable part", "=Share*Res_M1", "tradable share × Method 1 result", None),
        ("Method 3, nontradable part", "=(1-Share)*Res_M2", "(1 − tradable share) × Method 2 result", None),
        ("METHOD 3 RESULT", "=Share*Res_M1+(1-Share)*Res_M2", "tradable part + nontradable part", "Res_M3"),
        ("MAIN RESULT", "=CHOOSE(MainM,Res_M1,Res_M2,Res_M3)", "the method chosen as main result; the others are sensitivity analyses", "Res_Main"),
        ("Results are in", "=OutLabel&\" at \"&BaseYear&\" prices\"", "", None),
    ]
    for i, (label, f, words, nm) in enumerate(steps):
        r = 39 + i
        ws[f"A{r}"], ws[f"B{r}"], ws[f"C{r}"] = label, f, words
        ws[f"B{r}"].number_format = "#,##0.00" if "RESULT" in label or "part" in label or "after" in label or "Cost" in label else "0.000000"
        if "RESULT" in label:
            ws[f"A{r}"].font = ws[f"B{r}"].font = BOLD
        if nm:
            name(nm, f"Calculator!$B${r}")
    for col, w in zip("ABCDEFGHIJ", [52, 22, 11, 46, 8, 20, 22, 14, 18, 22]):
        ws.column_dimensions[col].width = w

    # ------------------------------------------------------------------ Data sheets
    def write_series(sh, key, kind):
        ws = sheets[sh]
        data = S[key] if key else {}
        extra = {"index": ["Last data year", "Trend start year", "Trend rate (data)", "Your rate", "Rate used if no IMF forecast"],
                 "rate": ["Last data year", "After the last data year"], "raw": [], "weo": []}[kind]
        ws.append(["ISO3", "Country"] + list(range(Y_FIRST, Y_END + 1)) + extra)
        for c in ws[1]:
            c.font, c.fill = BOLD, HEAD
        for iso in isos:
            r = row_of[iso]
            ws.cell(row=r, column=1, value=iso)
            ws.cell(row=r, column=2, value=names[iso])
            s = (D["raw"]["fx_off"].get(iso) if kind == "raw" else data.get(iso)) or {}
            for y, v in s.items():
                if Y_FIRST <= y <= Y_END and v is not None:
                    ws.cell(row=r, column=COL0 + y - Y_FIRST, value=B.sig(v))
            if not s or kind in ("raw", "weo"):
                continue
            L = max(s)
            Lc = ycol(L)
            ws[f"{C_LY}{r}"] = L
            if L < last_all[key] - STALE:
                ws[f"{CL(COL0 + Y_END - Y_FIRST + 2)}{r}"] = f"Not projected: series ends in {L}, more than {STALE} years before the latest data"
                continue
            if kind == "index":
                a = ycol(max(Y_FIRST, L - 20))
                ws[f"{C_TS}{r}"] = (f"=_xlfn.AGGREGATE(15,6,{a}$1:{Lc}$1/(ISNUMBER({a}{r}:{Lc}{r})*({a}$1:{Lc}$1>=${C_LY}{r}-TrendYears)),1)")
                ws[f"{C_TR}{r}"] = (f"=(${Lc}{r}/INDEX({a}{r}:{Lc}{r},MATCH(${C_TS}{r},{a}$1:{Lc}$1,0)))^(1/(${C_LY}{r}-${C_TS}{r}))-1")
                ws[f"{C_YR}{r}"].fill = INPUT
                ws[f"{C_RU}{r}"] = f"=IF(ISNUMBER(${C_YR}{r}),${C_YR}{r},${C_TR}{r})"
                for col in (C_TR, C_YR, C_RU):
                    ws[f"{col}{r}"].number_format = "0.00%"
                # IMF WEO path when chosen, available for every year from L+1 and no own rate typed; else the trend
                weo_ok = (f'AND(ProjRule="IMF WEO",NOT(ISNUMBER(${C_YR}{r})),'
                          f"COUNT(IMF_WEO!{ycol(min(L + 1, weo_end))}{r}:IMF_WEO!${ycol(weo_end)}{r})={max(weo_end - L, 1)})")
                for y in range(L + 1, Y_END + 1):
                    w = f"IMF_WEO!${ycol(min(y, weo_end))}{r}"
                    c = ws[f"{ycol(y)}{r}"]
                    c.value = f"={ycol(y - 1)}{r}*(1+IF({weo_ok},{w}/100,${C_RU}{r}))"
                    c.fill = PROJ
            else:
                hold = 'FxAfterData="Hold last rate",' if sh in ("FX", "FX_ALT") else ""
                if sh == "OLDFX":
                    ws[f"{CL(COL0 + Y_END - Y_FIRST + 2)}{r}"] = "Held at the last rate"
                    for y in range(L + 1, Y_END + 1):
                        ws[f"{ycol(y)}{r}"] = f"=${Lc}{r}"
                        ws[f"{ycol(y)}{r}"].fill = PROJ
                    continue
                ws[f"{CL(COL0 + Y_END - Y_FIRST + 2)}{r}"] = (
                    "Held at the last rate, or moved with the linked GDP-deflator gap against the US (see Calculator)" if hold
                    else "Moved with the linked GDP-deflator gap against the US")
                for y in range(L + 1, Y_END + 1):
                    yc = ycol(y)
                    ok = f"AND(ISNUMBER(GDPD_L!{yc}{r}),ISNUMBER(GDPD_L!${Lc}{r}),ISNUMBER(GDPD_L!{yc}{us}),ISNUMBER(GDPD_L!${Lc}{us}))"
                    gap = f"${Lc}{r}*(GDPD_L!{yc}{r}/GDPD_L!${Lc}{r})/(GDPD_L!{yc}{us}/GDPD_L!${Lc}{us})"
                    c = ws[f"{yc}{r}"]
                    c.value = f"=IF(OR({hold}NOT({ok})),${Lc}{r},{gap})"
                    c.fill = PROJ
        ws.freeze_panes = "C2"
        ws.column_dimensions["B"].width = 26
        return ws

    write_series("GDPD_L", "gdpd_l", "index")
    write_series("GDPD", "gdpd", "index")
    write_series("CPI", "cpi", "index")
    write_series("FX_raw", None, "raw")       # downloaded values only; source of the re-expressed FX sheet
    write_series("FX", "fx", "rate")
    write_series("FX_ALT", "fx_alt", "rate")
    write_series("PPP_WB", "ppp", "rate")
    write_series("PPP_OECD", "ppp_oecd", "rate")
    write_series("OLDFX", "oldfx", "rate")
    write_series("IMF_WEO", "weo", "weo")
    # FX cells published in an older currency unit: formula = FX_raw ÷ old units per current unit
    nconv = 0
    for iso in isos:
        kinds = {e["kind"] for e in hist.get(iso, [])}
        if kinds & {"dollar", "usd_accounts"}:
            continue
        raw = D["raw"]["fx_off"].get(iso) or {}
        for y, v in (S["fx"].get(iso) or {}).items():
            rv = raw.get(y)
            if rv and v and abs(rv / v - 1) > 1e-9:
                c = sheets["FX"][f"{ycol(y)}{row_of[iso]}"]
                c.value = f"=FX_raw!{ycol(y)}{row_of[iso]}/{B.sig(rv / v, 9)}"
                c.fill = CONV
                nconv += 1
    sheets["FX"]["A1"].comment = Comment(
        "Violet cells = FX_raw ÷ old units per current unit (euro changeovers, Bulgaria, Croatia, Venezuela, Zimbabwe, Zambia, "
        "Turkmenistan; see CurrencyHistory and DATA_QUALITY.md). Ecuador, El Salvador, Liberia and West Bank and Gaza keep national "
        "accounts in US$, so their rate is 1 and the local currency uses OLDFX. Green cells are projections.", "Cost Converter")
    sheets["IMF_WEO"]["A1"].comment = Comment(f"IMF {weo}, inflation, average consumer prices (PCPIPCH), % a year, {B.WEO_FROM}-{weo_end}.",
                                              "Cost Converter")

    # ------------------------------------------------------------------ List sheet
    ws = ws_list
    ws["A1"] = "A list of costs"
    ws["A1"].font = TITLE
    ws["A2"] = ("Yellow cells are inputs. Base year, output currency, inflation measure, exchange-rate and PPP source and tradable share "
                "come from the Calculator sheet. Each row repeats the Calculator's formulas.")
    ws["A2"].font = NOTE
    heads = ["Study", "Amount", "Country", "Price year", "Reported in", "Amount is in (old code)", "Country row", "Undo-conversion rate",
             "Old-currency divisor", "Rate S, price yr", "Rate S, base yr", "Rate T, price yr", "Rate T, base yr", "Index S, price yr",
             "Index S, base yr", "Index M1, price yr", "Index M1, base yr", "Cost in the data's currency", "Method 1", "Method 2", "Method 3"]
    for i, h in enumerate(heads):
        c = ws.cell(row=4, column=1 + i, value=h)
        c.font, c.fill = BOLD, HEAD
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4].height = 30
    ws["S3"] = '="Results in "&OutLabel&" at "&BaseYear&" prices"'
    ws["S3"].font = BOLD
    examples = [("Example A", 1000000, "Viet Nam", 2006, "Local currency", None), ("Example B", 100, "Viet Nam", 2006, "US$", None),
                ("Example C", 2500, "India", 2012, "Local currency", None), ("Example D", 850, "Germany", 1997, "Local currency", "DEM"),
                ("Example E", 1200, "United Kingdom", 2015, "Local currency", None),
                ("Example F", 72000000000, "Sierra Leone", 2017, "Local currency", "SLL")]
    iso_col = lambda r: f"INDEX(Countries!$A${R0}:$A${R1},$G{r})"  # noqa: E731
    for i in range(40):
        r = 5 + i
        if i < len(examples):
            for j, v in enumerate(examples[i]):
                ws.cell(row=r, column=1 + j, value=v)
        for col in "ABCDEF":
            ws[f"{col}{r}"].fill = INPUT
        blank = f'$B{r}=""'
        key = f'{iso_col(r)}&"|"&$F{r}'
        f = {
            "G": f"=IF({blank},\"\",MATCH($C{r},Countries!$B${R0}:$B${R1},0))",
            "H": f'=IF({blank},"",IF($E{r}="US$",{LOOK("FXSeries", f"$G{r}", f"$D{r}")},IF($E{r}="I$",{LOOK("PPPSeries", f"$G{r}", f"$D{r}")},1)))',
            "I": (f'=IF({blank},"",IF(OR($E{r}<>"Local currency",$F{r}=""),1,IF(INDEX({HHOW},MATCH({key},{HK},0))="fixed divisor",'
                  f'INDEX({HPER},MATCH({key},{HK},0)),{LOOK(chr(34) + "OLDFX" + chr(34), f"$G{r}", f"$D{r}")})))'),
            "J": f'=IF({blank},"",{LOOK("ConvSeries", f"$G{r}", f"$D{r}")})',
            "K": f'=IF({blank},"",{LOOK("ConvSeries", f"$G{r}", "BaseYear")})',
            "L": f'=IF({blank},"",{LOOK("ConvSeries", "RowT", f"$D{r}")})',
            "M": f'=IF({blank},"",{LOOK("ConvSeries", "RowT", "BaseYear")})',
            "N": f'=IF({blank},"",{LOOK("IdxSeries", f"$G{r}", f"$D{r}")})',
            "O": f'=IF({blank},"",{LOOK("IdxSeries", f"$G{r}", "BaseYear")})',
            "P": f'=IF({blank},"",{LOOK("IdxSeries", "RowI", f"$D{r}")})',
            "Q": f'=IF({blank},"",{LOOK("IdxSeries", "RowI", "BaseYear")})',
            "R": f'=IF({blank},"",$B{r}*$H{r}/$I{r})',
            "S": f'=IF({blank},"",$R{r}*IF(AND(OutCur="Local currency of a country",RowT=$G{r}),1,$L{r}/$J{r})*$Q{r}/$P{r})',
            "T": f'=IF({blank},"",$R{r}*$O{r}/$N{r}*IF(AND(OutCur="Local currency of a country",RowT=$G{r}),1,$M{r}/$K{r}))',
            "U": f'=IF({blank},"",Share*$S{r}+(1-Share)*$T{r})',
        }
        for col, formula in f.items():
            ws[f"{col}{r}"] = formula
            ws[f"{col}{r}"].number_format = "#,##0.00" if col in "RSTU" else ("0" if col == "G" else "#,##0.0000")
    dv_country(ws, "C5:C44")
    dv(ws, "D5:D44", "A")
    dv(ws, "E5:E44", "B")
    for col, w in zip("ABCDEFGHIJKLMNOPQRSTU", [14, 15, 18, 9, 15, 11, 8] + [12] * 10 + [14, 14, 14, 14]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "B5"

    # ------------------------------------------------------------------ Paper example
    ws = ws_paper
    ws["A1"] = "Worked example from Turner et al. (2019), Figures 1 and 2 and the abstract"
    ws["A1"].font = TITLE
    ws["A2"] = "The paper's own rates and inflation factors (yellow) and the three methods as formulas. Column D is the figure printed in the paper."
    ws["A2"].font = NOTE
    rows = [
        ("Cost, VND (2006 prices)", 1000000, None, None),
        ("Exchange rate 2006, VND per US$", 15994.25, None, "Figure 1A: US$1 = VND 15,994"),
        ("Exchange rate 2016, VND per US$", 21935, None, "Figure 1B: US$1 = VND 21,935"),
        ("US inflation factor 2006 to 2016", 1.1684, None, "Figure 1A: × 1.17; abstract US$ 116.84 from US$ 100"),
        ("Vietnam inflation factor 2006 to 2016", 2.360037, None, "Figure 1B: × 2.36 (VND 2,360,037)"),
        ("Tradable share", 0.2, None, "Figure 2: 20%"),
        ("Method 1, US$ (2016 prices)", "=B4/B5*B7", 73.05, "Figure 1A"),
        ("Method 2, US$ (2016 prices)", "=B4*B8/B6", 107.59, "Figure 1B"),
        ("Method 3, US$ (2016 prices)", "=B9*B10+(1-B9)*B11", 100.68, "Figure 2"),
        ("Cost reported as US$ 100 in 2006 (abstract)", 100, None, None),
        ("Back to VND at the 2006 rate", "=B13*B5", None, "Figure 4, correct path"),
        ("Method 1, US$", "=B14/B5*B7", 116.84, "Abstract"),
        ("Method 2, US$", "=B14*B8/B6", 172.09, "Abstract"),
        ("Method 3, US$", "=B9*B15+(1-B9)*B16", 161.04, "Abstract"),
    ]
    for i, h in enumerate(["Item", "Value", "Check: rounded result − paper", "Paper (printed)", "Where in the paper"]):
        c = ws.cell(row=3, column=1 + i, value=h)
        c.font, c.fill = BOLD, HEAD
    for i, (label, v, paper, where) in enumerate(rows):
        r = 4 + i
        ws[f"A{r}"], ws[f"B{r}"] = label, v
        if not (isinstance(v, str) and v.startswith("=")):
            ws[f"B{r}"].fill = INPUT
        if paper is not None:
            ws[f"D{r}"] = paper
            ws[f"C{r}"] = f"=ROUND(B{r},2)-D{r}"
            ws[f"C{r}"].number_format = ws[f"D{r}"].number_format = "#,##0.00"
        ws[f"E{r}"] = where
        ws[f"B{r}"].number_format = "0%" if "share" in label else ("#,##0.000000" if "factor" in label else "#,##0.00")
    ws["A19"] = "Same example with this workbook's World Bank data: linked GDP deflator (column B) and standard series (column C)"
    ws["A19"].font = BOLD
    vn, usr = row_of["VNM"], row_of["USA"]
    wbrows = [
        ("Exchange rate 2006", f"=FX!{ycol(2006)}{vn}", f"=FX!{ycol(2006)}{vn}"),
        ("Exchange rate 2016", f"=FX!{ycol(2016)}{vn}", f"=FX!{ycol(2016)}{vn}"),
        ("US inflation factor", f"=GDPD_L!{ycol(2016)}{usr}/GDPD_L!{ycol(2006)}{usr}", f"=GDPD!{ycol(2016)}{usr}/GDPD!{ycol(2006)}{usr}"),
        ("Vietnam inflation factor", f"=GDPD_L!{ycol(2016)}{vn}/GDPD_L!{ycol(2006)}{vn}", f"=GDPD!{ycol(2016)}{vn}/GDPD!{ycol(2006)}{vn}"),
        ("Method 1, US$", "=B4/B20*B22", "=B4/C20*C22"), ("Method 2, US$", "=B4*B23/B21", "=B4*C23/C21"),
        ("Method 3, US$", "=B9*B24+(1-B9)*B25", "=B9*C24+(1-B9)*C25"),
    ]
    for i, (label, f, g) in enumerate(wbrows):
        r = 20 + i
        ws[f"A{r}"], ws[f"B{r}"], ws[f"C{r}"] = label, f, g
        ws[f"B{r}"].number_format = ws[f"C{r}"].number_format = "#,##0.000000" if "factor" in label else "#,##0.00"
    ws["A28"] = ("The standard series counts Vietnam's 2010 rebasing of the national accounts as inflation (× 2.91 against the linked 2.29 "
                 "and the paper's 2.36).")
    ws["A28"].font = NOTE
    for col, w in zip("ABCDE", [44, 18, 26, 16, 52]):
        ws.column_dimensions[col].width = w

    # ------------------------------------------------------------------ EPPI check
    ws = ws_eppi
    eppi = json.loads((HERE / "eppi_results.json").read_text(encoding="utf-8"))
    ws["A1"] = "Check against the CCEMG–EPPI Cost Converter (v1.7), run on 17 October 2026"
    ws["A1"].font = TITLE
    ws["A2"] = ("EPPI's result = cost × GDPD(original, base year) ÷ GDPD(original, price year) × PPP(target, base year) ÷ PPP(original, base year): "
                "Method 2 with PPP. Columns K–O are the values shown in EPPI's Results panel (typed in). Columns P–Q recompute them; "
                "columns R–X recompute the case with this workbook's data (linked GDP deflator).")
    ws["A2"].font = NOTE
    heads = ["Case", "EPPI data", "From", "ISO", "Price year", "To", "ISO", "Base year", "Cost", "Pre-euro code",
             "EPPI: GDPD orig, price yr", "EPPI: GDPD orig, base yr", "EPPI: PPP orig, base yr", "EPPI: PPP target, base yr", "EPPI result",
             "Ours with EPPI's inputs", "Difference", "Our GDPD, price yr", "Our GDPD, base yr", "Our PPP orig, base yr", "Our PPP target, base yr",
             "Old-currency divisor", "Ours with our data", "Difference", "EPPI marks as IMF estimates"]
    for i, h in enumerate(heads):
        c = ws.cell(row=4, column=1 + i, value=h)
        c.font, c.fill = BOLD, HEAD
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4].height = 45
    num = lambda s: float(str(s).replace(",", ""))  # noqa: E731
    red_names = {"lblTargetPPP": "PPP orig", "lblTargetCountryPPP2": "PPP target", "lblTargetGDPD": "GDPD base yr", "lblSourceGDPD": "GDPD price yr"}
    for i, c in enumerate(eppi):
        r = 5 + i
        e = c["eppi"]
        old = next((h["old"] for h in hist.get(c["iso"], []) if h["kind"] == "euro"), None) if c.get("pre_euro") else None
        vals = [c["id"], c["source"], c["orig"], c["iso"], c["y0"], c["target"], c["tiso"], c["y1"], c["cost"], old,
                num(e["lblSourceGDPD"]), num(e["lblTargetGDPD"]), num(e["lblTargetPPP"]), num(e["lblTargetCountryPPP2"]), num(e["lblStage2"])]
        for j, v in enumerate(vals):
            ws.cell(row=r, column=1 + j, value=v)
        ppp = '"PPP_OECD"' if c["source"] == "OECD" else '"PPP_WB"'
        rs = f"MATCH($D{r},Countries!$A${R0}:$A${R1},0)"
        rt = f"MATCH($G{r},Countries!$A${R0}:$A${R1},0)"
        ws[f"P{r}"] = f"=$I{r}*$L{r}/$K{r}*$N{r}/$M{r}"
        ws[f"Q{r}"] = f"=P{r}/O{r}-1"
        ws[f"R{r}"] = f"={LOOK(chr(34) + 'GDPD_L' + chr(34), rs, f'$E{r}')}"
        ws[f"S{r}"] = f"={LOOK(chr(34) + 'GDPD_L' + chr(34), rs, f'$H{r}')}"
        ws[f"T{r}"] = f"={LOOK(ppp, rs, f'$H{r}')}"
        ws[f"U{r}"] = f"={LOOK(ppp, rt, f'$H{r}')}"
        ws[f"V{r}"] = f'=IF($J{r}="",1,INDEX({HPER},MATCH($D{r}&"|"&$J{r},{HK},0)))'
        ws[f"W{r}"] = f"=$I{r}/$V{r}*$S{r}/$R{r}*IF($D{r}=$G{r},1,$U{r}/$T{r})"
        ws[f"X{r}"] = f"=W{r}/O{r}-1"
        ws[f"Y{r}"] = ", ".join(red_names.get(k, k) for k in e.get("red", []))
        for col in "IOPW":
            ws[f"{col}{r}"].number_format = "#,##0.00"
        for col in "KLMNRSTUV":
            ws[f"{col}{r}"].number_format = "#,##0.0000"
        for col in "QX":
            ws[f"{col}{r}"].number_format = "0.0000%"
    last = 4 + len(eppi)
    s0 = last + 2
    summary = [
        ("Cases", f"=COUNT(A5:A{last})", "0"),
        ("Cases where our formula with EPPI's inputs matches EPPI to the cent", f"=SUMPRODUCT(--(ABS(P5:P{last}-O5:O{last})<0.005))", "0"),
        ("Largest difference with EPPI's inputs", f"=_xlfn.AGGREGATE(14,6,ABS(Q5:Q{last}),1)", "0.0000%"),
        ("Median absolute difference with our data", f"=_xlfn.AGGREGATE(16,6,ABS(X5:X{last}),0.5)", "0.0%"),
        ("Cases within 5% with our data", f"=SUMPRODUCT(--(ABS(X5:X{last})<=0.05))", "0"),
        ("Cases within 10% with our data", f"=SUMPRODUCT(--(ABS(X5:X{last})<=0.1))", "0"),
    ]
    ws[f"A{s0}"] = "Summary"
    ws[f"A{s0}"].font = BOLD
    for i, (label, f, nf) in enumerate(summary):
        r = s0 + 1 + i
        ws[f"A{r}"], ws[f"F{r}"] = label, f
        ws[f"F{r}"].number_format = nf
    ws[f"A{s0 + 8}"] = ("Differences in column X come from the data: EPPI uses IMF World Economic Outlook (October 2023) deflators and IMF or OECD "
                        f"PPPs; this workbook uses World Bank, OECD and IMF data (WDI last updated {wdi_upd}). For the pre-euro French cases EPPI "
                        "shows PPP in francs, so column P needs no divisor; column W divides the cost by 6.55957 francs per euro.")
    ws[f"A{s0 + 8}"].font = NOTE
    for col, w in zip("ABCDEFGHIJ", [6, 7, 15, 6, 8, 15, 6, 8, 12, 8]):
        ws.column_dimensions[col].width = w
    for col in "KLMNOPQRSTUVWX":
        ws.column_dimensions[col].width = 13
    ws.column_dimensions["Y"].width = 30
    ws.freeze_panes = "C5"

    # ------------------------------------------------------------------ README
    ws = ws_readme
    lines = [
        (f"Health Cost Converter {B.VERSION}: workings", TITLE),
        ("This workbook repeats every calculation of the Health Cost Converter (https://narassima.github.io/Health-Cost-Converter/) as "
         "Excel formulas, so a reader can check any result. Methods follow Turner et al. (2019), Value in Health 22(9):1026-1032.", None),
        (f"Data vintage: World Bank WDI last updated {wdi_upd} (retrieved {wmeta['retrieved']}); IMF {weo}; OECD PPPs. Built {B.TODAY.isoformat()}.", None),
        ("", None),
        ("Sheets", BOLD),
        ("Calculator: the same inputs as the web page (yellow cells, with dropdowns). 'Values used' looks up each rate and index; "
         "'Results' works through Methods 1, 2 and 3 and the main result step by step.", None),
        ("List: a list of costs, one per row, with all three methods. Uses the Calculator's Convert-to settings.", None),
        ("Paper example: Turner et al.'s Figures 1-2 and abstract recomputed from the paper's own rates, with a check column; then the "
         "same example on this workbook's data, with the linked and the standard GDP deflator.", None),
        ("EPPI check: 31 conversions run through the CCEMG-EPPI Cost Converter, recomputed by formula from EPPI's displayed values and "
         "from this workbook's data.", None),
        ("GDPD_L (linked GDP deflator, NY.GDP.DEFL.ZS.AD, extended with the growth of the standard series where it is missing), GDPD "
         "(standard series), CPI, FX (official rate in today's currency unit), FX_ALT (alternative conversion factor), PPP_WB, PPP_OECD, "
         "OLDFX (rates of the local currency in dollarised economies): one row per country (same order as Countries), columns 1960 to 2037. "
         "White cells are data; green cells after the last data year are projection formulas; violet cells in FX are rates published in "
         "an older currency unit, re-expressed by formula from FX_raw.", None),
        ("FX_raw: World Bank official exchange rates exactly as downloaded. IMF_WEO: IMF inflation forecasts (% a year).", None),
        ("Countries and CurrencyHistory: currency of the data, older currencies and their conversion (data/currency_history.csv).", None),
        ("", None),
        ("How to check a result", BOLD),
        ("1. On Calculator, set the inputs to the case you want. 2. Compare Res_M1, Res_M2, Res_M3 and Res_Main with the web page. "
         "3. Select any value and use Formulas > Trace Precedents to follow it to the data cell it comes from.", None),
        (f"Projection rules (years after a series' last data year): price indices follow the IMF WEO inflation forecasts to {weo_end} "
         "(then the last rate) or grow at the country's average annual rate over its last 5, 10 or 20 years (Calculator B19; type your own "
         "rate in column 'Your rate' of GDPD_L, GDPD or CPI). Exchange rates move with the linked GDP-deflator gap against the US or stay at "
         f"the last rate (Calculator B20). PPP factors always move with the gap. A series that ends more than {STALE} years before the latest "
         "data is not projected (#N/A).", None),
        ("", None),
        ("Sources", BOLD),
        ("World Bank World Development Indicators, licence CC BY 4.0: GDP deflator (NY.GDP.DEFL.ZS) and linked series (NY.GDP.DEFL.ZS.AD); "
         "consumer price index, 2010 = 100 (FP.CPI.TOTL); official exchange rate (PA.NUS.FCRF); DEC alternative conversion factor "
         "(PA.NUS.ATLS); PPP conversion factor, GDP (PA.NUS.PPP); GDP in current LCU and US$ (unit checks).", None),
        ("OECD Data Explorer, Annual Purchasing Power Parities and exchange rates, PPP for GDP, CC BY 4.0.", None),
        (f"IMF {weo}, inflation, average consumer prices (PCPIPCH).", None),
        ("Turner HC, Lauer JA, Tran BX, Teerawattananon Y, Jit M. Adjusting for inflation and currency changes within health economic "
         "studies. Value in Health. 2019;22(9):1026-1032. doi:10.1016/j.jval.2019.03.021", None),
        ("Shemilt I, Thomas J, Morciano M. A web-based tool for adjusting costs to a specific target currency and price year. "
         "Evidence & Policy. 2010;6(1):51-59. doi:10.1332/174426410X482999", None),
        ("Council Regulation (EC) No 2866/98, as amended for each later member: irrevocable euro conversion rates; national redenomination laws.", None),
        ("", None),
        ("Colour key: yellow = input; green = projected value (formula); violet = rate re-expressed in today's currency unit (formula).", NOTE),
    ]
    for i, (t, font) in enumerate(lines, start=1):
        c = ws.cell(row=i, column=1, value=t)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if font:
            c.font = font
    ws.column_dimensions["A"].width = 130

    out = ROOT / "Cost_Converter_Workings.xlsx"
    wb.save(out)
    print("Saved", out, "| countries", n, "| USA row", us, "| VNM row", row_of["VNM"], "| FX cells re-expressed", nconv,
          "| last data year", y_last_data)


if __name__ == "__main__":
    main()
