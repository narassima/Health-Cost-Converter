# Health Cost Converter

A browser calculator that restates a cost from one country, currency and price year in the currency and prices of another year, for health economic studies and systematic reviews. It applies the three adjustment methods of Turner et al. (2019), *Value in Health* 22(9):1026–1032, and shows every rate and index it uses.

**Open the calculator:** https://narassima.github.io/Health-Cost-Converter/

Version 2.1.1 (see [CHANGELOG.md](CHANGELOG.md)). Data: World Bank WDI (last updated 11 November 2026), IMF World Economic Outlook (October 2026), OECD PPPs.

## What it does

- Adjusts a cost with **Method 1** (convert at the price-year rate, then apply US or output-country inflation), **Method 2** (apply local inflation, then convert at the base-year rate) and **Method 3** (a tradable share through Method 1 and the rest through Method 2).
- **Method 2 with PPP and the GDP deflator is the main result by default.** This follows the CCEMG–EPPI Cost Converter and makes results comparable with past reviews. Methods 1 and 3 are shown as sensitivity analyses. Turner et al. advise reporting in local currency with local inflation for high-income settings.
- Works for **214 countries**. Price indices: the World Bank's **linked GDP deflator** (the default; it removes national-accounts rebasing breaks), the standard GDP deflator (break years are flagged), or the **consumer price index**.
- Reports in **international $** (PPP), **US$** (market exchange rates) or the **local currency of any country**. Exchange rates come from the official rate or the World Bank's **alternative conversion factor**. The tool warns when the two differ by more than 10%, for example in Lebanon, Iran, Syria and Myanmar.
- Handles **old and replaced currencies** through a currency-history table (`data/currency_history.csv`). This covers pre-euro currencies, redenominations (Sierra Leone SLL, Ghana, Turkey TRL, Venezuela, Zimbabwe, Zambia, Turkmenistan, Bulgaria and others) and dollarised economies (Ecuador, El Salvador, Liberia, West Bank and Gaza).
- Converts costs the study already turned into US$ or I$ back to local currency first (Turner et al., Figure 4).
- Accepts **base years up to 2037**. After the last data year, price indices follow the **IMF WEO inflation forecasts** to 2031. A country's own 5-, 10- or 20-year trend can be chosen instead. Projected results are rounded to 3 significant figures and shown with a low–high band from the 5- and 20-year rules. A series that ends more than 3 years before the latest data is not projected.
- Converts **a list of costs** pasted from Excel. It reads decimal commas safely and flags any number that could be read either way. It matches common column headers and lets you change the column mapping, and it reads fiscal years (2015-16) in the way you choose. The export carries full precision, a rounded column, every warning and the tool version.
- Writes a **methods-section paragraph** naming the method, measure, currency, data sources, tool version and data vintage. A **permalink** reopens the exact calculation.

The page is laid out like the CCEMG–EPPI Cost Converter, in LinkedIn blue: Steps 1–6, a Results table (PPP or exchange-rate values, ICF, GDPD values, IIF and the final result, with the other methods as sensitivity analyses), then further options and "Information for users". Projected values are shown in red type. Every field has an **i** button, and the **How to use** page walks through worked examples.

## Files

| File | What it is |
|---|---|
| `index.html` | The calculator. One self-contained page with all data built in. It needs no server and works offline. |
| `Cost_Converter_Workings.xlsx` | The same calculations as live Excel formulas on the same data, so any result can be checked (Formulas › Trace Precedents). It includes the Turner et al. worked example and the 31 CCEMG–EPPI check cases. |
| `DATA_QUALITY.md` | Written at every build: unit tests, currency conversions, deflator breaks, official-vs-alternative rate gaps and stale series. |
| `build/` | `fetch_data.py` downloads the data, `build.py` builds the page and `build_workbook.py` builds the workbook. `app_template.html` is the page source. |
| `data/` | The raw downloads (`raw/`) and the currency-history table. |
| `tests/` | `node tests/run.js index.html` runs 103 checks: the paper to the cent, the 31 EPPI cases, currency units, deflator breaks, alternative rates, projections, number parsing and list mode. |

## Methods

With C the cost in the local currency of country S at year-t0 prices, V the result in currency T at base-year t1 prices, r a conversion rate (local currency per US$, or per I$ for PPP), P a price index and s the tradable share:

```
Method 1   V = C ÷ r_S(t0) × r_T(t0) × P_T(t1) ÷ P_T(t0)
Method 2   V = C × P_S(t1) ÷ P_S(t0) ÷ r_S(t1) × r_T(t1)
Method 3   V = s × V1 + (1 − s) × V2
```

For US$ and I$ outputs, r_T = 1 and P_T is the United States index.

**Currency units.** All values for a country are in its current currency for every year. The World Bank publishes official exchange rates in the currency of each year. These rates are divided by the fixed conversion factor from `data/currency_history.csv`, and every conversion is listed in `DATA_QUALITY.md`. In dollarised economies, the national accounts are in US$. There, the rate for the old local currency is kept separately and used when a cost is entered in that currency.

**Years after the data.** These values are assumptions, not data. You can replace each one with your own forecast in the calculator and in the workbook.
- Price indices follow the IMF WEO forecasts, or the chosen trend if the IMF has no forecast.
- Exchange rates move with the linked GDP-deflator gap against the United States, or are held at the last rate.
- PPP factors move with the same gap.
- Trends above 15% a year are flagged.

## Data

| Series | Source |
|---|---|
| GDP deflator, linked series `NY.GDP.DEFL.ZS.AD`, and standard series `NY.GDP.DEFL.ZS` | World Bank, World Development Indicators |
| Consumer price index (2010 = 100), `FP.CPI.TOTL` | World Bank, World Development Indicators |
| Official exchange rate, `PA.NUS.FCRF`; DEC alternative conversion factor, `PA.NUS.ATLS` | World Bank, World Development Indicators |
| PPP conversion factor, GDP, `PA.NUS.PPP` | World Bank, World Development Indicators (International Comparison Program) |
| GDP in current LCU, US$ and PPP $ (unit checks and the 10%-of-GDP warning) | World Bank, World Development Indicators |
| Purchasing power parities for GDP | OECD Data Explorer, Annual Purchasing Power Parities and exchange rates |
| Inflation, average consumer prices, `PCPIPCH` (forecasts to 2031) | IMF World Economic Outlook, October 2026 |

World Bank and OECD data are published under CC BY 4.0. Statistical agencies revise past values, so results can differ slightly from published studies that used older releases. Any value can be replaced in the calculator's **Values used** table.

## Rebuilding

```
python build/fetch_data.py          # download the latest data into data/raw/ (standard library only)
python build/build.py               # unit-test the data, write DATA_QUALITY.md, Cost_Converter.html and site/index.html
python build/build_workbook.py      # write Cost_Converter_Workings.xlsx (needs pandas and openpyxl)
python build/build.py               # again, to copy the workbook into site/
node tests/run.js site/index.html   # run the tests
```

Copy `site/index.html` and `Cost_Converter_Workings.xlsx` to the repository root to publish. Bump `VERSION` and add a `CHANGELOG.md` entry for every release.

## How to cite

Cite the version and data vintage shown at the top of the page; see [CITATION.cff](CITATION.cff).

## Licence

Code: MIT ([LICENSE](LICENSE)). Data: CC BY 4.0, from the World Bank, OECD and IMF sources above.

## References

- Turner HC, Lauer JA, Tran BX, Teerawattananon Y, Jit M. Adjusting for inflation and currency changes within health economic studies. *Value in Health*. 2019;22(9):1026–1032. https://doi.org/10.1016/j.jval.2019.03.021
- Shemilt I, Thomas J, Morciano M. A web-based tool for adjusting costs to a specific target currency and price year. *Evidence & Policy*. 2010;6(1):51–59. https://doi.org/10.1332/174426410X482999
- Kumaranayake L. The real and the nominal? Making inflationary adjustments to cost and other economic data. *Health Policy and Planning*. 2000;15:230–234.
- Dunn A, Grosse SD, Zuvekas SH. Adjusting health expenditures for inflation: a review of measures for health services research in the United States. *Health Services Research*. 2018;53(1):175–196.
- Global Health Costing Consortium. Reference case for estimating the costs of global health services and interventions. https://ghcosting.org/pages/standards/reference_case
- Council Regulation (EC) No 2866/98 on the conversion rates between the euro and the currencies of the Member States adopting the euro, as amended for each later member.
