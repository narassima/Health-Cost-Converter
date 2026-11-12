# Changelog

All notable changes to the Health Cost Converter. Versions follow [semantic versioning](https://semver.org/). The codes in brackets refer to the critical appraisal of version 1 (November 2026).

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
