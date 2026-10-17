# Health Cost Converter

A browser calculator that restates a cost from one country, currency and price year in the currency and prices of another year, for health economic studies. It applies the three adjustment methods described by Turner et al. (2019), *Value in Health* 22(9):1026–1032, and shows every rate and index it uses.

**Open the calculator:** `https://<username>.github.io/<repository>/` (replace with this repository's GitHub Pages address)

## What it does

- Adjusts a cost with **Method 1** (convert at the price-year rate, then apply US or output-country inflation), **Method 2** (apply local inflation, then convert at the base-year rate) and **Method 3** (a tradable share through Method 1 and the rest through Method 2).
- Works for **214 countries** with the **GDP implicit price deflator** or the **consumer price index**.
- Reports in **US$** (market exchange rates), **international $** (PPP) or the **local currency of any country**, using market rates or PPP between currencies.
- Handles costs the study already converted to US$ or I$ by turning them back into local currency first, and amounts in pre-euro currencies (DEM, FRF and others) at the fixed euro conversion rates.
- Accepts **base years up to 2037**. After a series' last year of data, values are projected (see below) and marked in green.
- Converts **a list of costs** pasted from Excel and copies the results back.
- Writes a **methods-section paragraph** naming the method, measure, currency and data sources.

Every field has an **i** button, and the **How to use** page in the calculator walks through worked examples.

## Files

| File | What it is |
|---|---|
| `index.html` | The calculator. One self-contained page with all data built in; it needs no server and also works offline after download. |
| `Cost_Converter_Workings.xlsx` | The same calculations as Excel formulas, with the data, so any result can be checked (Formulas › Trace Precedents). Includes the worked example from Turner et al. (2019). |
| `README.md` | This file. |

## Methods

With C the cost in the local currency of country S at year-t0 prices, V the result in currency T at base-year t1 prices, r a conversion rate (local currency per US$, or per I$ for PPP), P a price index and s the tradable share:

```
Method 1   V = C ÷ r_S(t0) × r_T(t0) × P_T(t1) ÷ P_T(t0)
Method 2   V = C × P_S(t1) ÷ P_S(t0) ÷ r_S(t1) × r_T(t1)
Method 3   V = s × V1 + (1 − s) × V2
```

For US$ and I$ outputs, r_T = 1 and P_T is the United States index. Method 2 with the GDP deflator and PPP conversion into another country's currency is the approach of the CCEMG–EPPI Cost Converter (Shemilt et al., 2010).

**Years after the data.** After a country's last year of data, its price index grows at its own average annual rate over its last 10 years of data (5 or 20 can be chosen), exchange rates move with the GDP-deflator gap against the United States (or are held at the last rate), and PPP factors move with the same gap. These are assumptions, not data; each country's rate can be replaced with a forecast in the calculator and in the workbook.

**Euro area.** All money values for euro-area countries are in euros for every year. The World Bank's exchange rates before euro adoption (in the old national currency) are divided by the irrevocable conversion rate.

## Data

Retrieved on 17 October 2026 with Dataset Finder.

| Series | Source | Coverage |
|---|---|---|
| GDP deflator (base year varies by country), `NY.GDP.DEFL.ZS` | World Bank, World Development Indicators | 214 countries, 1960–2025 |
| Consumer price index (2010 = 100), `FP.CPI.TOTL` | World Bank, World Development Indicators | 192 countries |
| Official exchange rate (LCU per US$, period average), `PA.NUS.FCRF` | World Bank, World Development Indicators | 213 countries |
| PPP conversion factor, GDP (LCU per international $), `PA.NUS.PPP` | World Bank, World Development Indicators (International Comparison Program) | 204 countries, 1990–2025 |
| Purchasing power parities for GDP, `DSD_NAMAIN10@DF_TABLE4` | OECD Data Explorer, Annual Purchasing Power Parities and exchange rates | 65 countries |

World Bank and OECD data are published under the Creative Commons Attribution 4.0 International licence (CC BY 4.0). Source: World Bank, World Development Indicators; OECD, Annual Purchasing Power Parities and exchange rates.

Statistical agencies revise past values, so results can differ slightly from published studies that used older releases. Any value can be replaced in the calculator's **Values used** table.

## References

- Turner HC, Lauer JA, Tran BX, Teerawattananon Y, Jit M. Adjusting for inflation and currency changes within health economic studies. *Value in Health*. 2019;22(9):1026–1032. https://doi.org/10.1016/j.jval.2019.03.021
- Shemilt I, Thomas J, Morciano M. A web-based tool for adjusting costs to a specific target currency and price year. *Evidence & Policy*. 2010;6(1):51–59. https://doi.org/10.1332/174426410X482999
- Kumaranayake L. The real and the nominal? Making inflationary adjustments to cost and other economic data. *Health Policy and Planning*. 2000;15:230–234.
- WHO-CHOICE. *Making Choices in Health: WHO Guide to Cost-Effectiveness Analysis*. Geneva: World Health Organization; 2003.
- Global Health Costing Consortium. Reference case for estimating the costs of global health services and interventions. https://ghcosting.org/pages/standards/reference_case
- Council Regulation (EC) No 2866/98 on the conversion rates between the euro and the currencies of the Member States adopting the euro, as amended for each later member.

## Publishing on GitHub Pages

1. Upload `index.html`, `Cost_Converter_Workings.xlsx` and `README.md` to the root of the repository.
2. In the repository, open **Settings › Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
3. After a minute the calculator is live at the address GitHub shows on that page. Put that address at the top of this README.
