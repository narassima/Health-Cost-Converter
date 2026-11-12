# Changelog

All notable changes to the Health Cost Converter. Versions follow [semantic versioning](https://semver.org/). The codes in brackets refer to the critical appraisal of version 1 (November 2026).

## 2.1.2 — 2026-11-12

### Changed
- Colour scheme now follows IHEETS (iheets.co.in):
  - Forest green (#26462C) with white text on the title bar, step labels and table headers. The title bar uses a gradient to #163020 with a thin gold (#F8C300) underline.
  - A light leaf-green tint on the sensitivity rows and the final result, and leaf green (#6EA03F) on the slider.
  - Green links and headings.
- In "Information for users", Methods 1, 2 and 3 each have their own short paragraph, followed by a separate "Which to choose" paragraph.
- Results are unchanged.

## 2.1.1 — 2026-11-12

### Changed
- Colour scheme: the EPPI green is replaced by LinkedIn blue (#0A66C2) on the title bar, step labels and table headers, with white text on blue. Sensitivity rows use a light blue tint. Links and headings now use the same blue family. Results are unchanged.

## 2.1.0 — 2026-11-12

### Changed
- The calculator page now follows the layout of the CCEMG–EPPI Cost Converter:
  - a green title bar and the same introductory text
  - numbered Steps 1–6 with green label cells (cost, PPP source, original currency, target currency, original price year, target price year), with a Recalculate link
  - other settings grouped under "Further options"
- Results are shown in an EPPI-style table:
  - one row for the original currency and one for the target currency
  - columns for PPP values or exchange rates, ICF, GDPD (or CPI) values and IIF
  - the final result, with the other two methods as sensitivity analyses
  - footnotes explaining ICF and IIF
- Projected values are now shown in red type, as IMF estimates are in the EPPI tool. The "How it works" and "Data sources" panels are merged into a single "Information for users" section below the tool.
- Plain system fonts are used, and the dark theme has been removed. Results are unchanged.

## 2.0.0 — 2026-11-12

### Results change
- **Old and replaced currencies (C1, C3).** A currency-history table (`data/currency_history.csv`) covers euro changeovers and redenominations, including Sierra Leone, Ghana, Turkey, Venezuela, Zimbabwe, Zambia, Mauritania, Turkmenistan, Bulgaria and Croatia. It also covers dollarised economies: Ecuador, El Salvador, Liberia, and West Bank and Gaza. The calculator asks which currency an amount is in, and list mode accepts old codes (SLL, TRL, DEM …) in the currency column. Official exchange rates published in an older unit are converted to the current unit.
- **Bulgaria (C2).** Its PPP and national accounts are now read in the correct unit. At build time, each series' units are checked against GDP in LCU, US$ and PPP $.
- **Deflator breaks (C4).** The default price index is now the World Bank's linked GDP deflator (`NY.GDP.DEFL.ZS.AD`). The standard series is still available, and its break years are flagged when a calculation spans one.
- **Official vs. transacted exchange rates (C5).** The World Bank's alternative conversion factor (`PA.NUS.ATLS`) can be chosen, and the tool warns when it differs from the official rate by more than 10%.
- **Projections (C6).**
  - Price indices follow IMF World Economic Outlook inflation forecasts to 2031 by default.
  - Own-trend rules (5, 10 or 20 years) remain as options, and trends above 15% a year are flagged.
  - Series that end more than 3 years before the latest data are not projected.
  - Projected results are rounded to 3 significant figures and shown with a low–high band.
- **Default for reviews.** The main result is now Method 2 with PPP (international $) and the GDP deflator, following CCEMG–EPPI. Methods 1 and 3 are reported as sensitivity analyses.

### Fixed
- The projected-values notice no longer collapses into a 22 px box or throws an error when clicked (U1).
- Number parsing handles decimal commas and thousands separators, and flags numbers that could be read either way. A decimal-mark setting has been added (U2).
- List mode matches exact header names before loose ones, lets the user change the column mapping, and reports a missing Country column. It reads fiscal years (2015-16) as the start year, end year or average (U3).
- List rows carry every warning shown in one-cost mode. The export has full precision, a rounded column, the overrides used, and the tool version and data vintage. Overrides typed in one-cost mode are named when they apply to list rows (U4).
- Larger text and 24 px "i" targets, method markers that do not rely on colour alone, a table that stacks on narrow screens, print styles, and no external font requests (U5).
- The guide says that Turner et al. recommend local currency and local inflation for high-income settings. It also says that the CCEMG–EPPI default is Method 2 with PPP (D4). README placeholders and series descriptions are corrected (D5).

### Added
- `VERSION`, an MIT licence, `CITATION.cff`, this changelog, and the build scripts with the raw data (D1, D2).
- `tests/run.js`: 103 automated checks, run by GitHub Actions on every push (D3). They cover the Turner et al. worked example to the cent, the 31 CCEMG–EPPI cases, currency units, breaks, alternative rates, projections, parsing and list mode.
- `DATA_QUALITY.md`, written at every build. It lists unit tests, currency conversions, deflator breaks, rate gaps and stale series, and the page links to it.
- A permalink that reopens a calculation, and the tool version and data vintage in the generated methods wording.
- The Excel workings use the same processed data as the page. These include the linked deflator, alternative rates, a currency-history lookup, IMF WEO projections and the stale-series rule.

### Data
- World Bank WDI last updated 11 November 2026; IMF WEO October 2026; OECD PPPs.

## 1.0.0 — 2026-10-17
- First public release.
