# Data quality report

Health Cost Converter 2.1.2, built 2026-11-12 from World Development Indicators (last updated 2026-11-11), IMF World Economic Outlook (October 2026) and OECD PPPs.

This file is written by `build/build.py` at every build. The build stops if a unit test fails.

## Unit tests (all passed)

* The alternative conversion factor (PA.NUS.ATLS) equals GDP in LCU / GDP in US$ within 2% for every economy and year.
* After the currency-history conversion, no official rate differs from the alternative rate by a redenomination factor.
* World Bank PPPs equal GDP in LCU / GDP in PPP international dollars within 2% for every economy, 2022 onwards.
* OECD PPPs never differ from World Bank PPPs by a redenomination factor.

## Currency conversions applied

Official exchange rates are published in the currency of each year; GDP, deflators and PPPs are in today's unit. These conversions were applied (see `data/currency_history.csv`):

* fx AUT: 1960-1998 (39 years) divided by 13.7603
* fx BEL: 1960-1998 (39 years) divided by 40.3399
* fx BGR: 1960-2025 (50 years) divided by 1.95583
* fx HRV: 1992-2022 (31 years) divided by 7.5345
* fx CYP: 1960-2007 (48 years) divided by 0.585274
* fx ECU: national accounts in US dollars; official rate set to 1 (the local currency uses its own rate)
* fx SLV: national accounts in US dollars; official rate set to 1 (the local currency uses its own rate)
* fx EST: 1993-2010 (18 years) divided by 15.6466
* fx FIN: 1960-1998 (39 years) divided by 5.94573
* fx FRA: 1960-1998 (39 years) divided by 6.55957
* fx DEU: 1960-1998 (39 years) divided by 1.95583
* fx GRC: 1960-2000 (41 years) divided by 340.75
* fx IRL: 1960-1998 (39 years) divided by 0.787564
* fx ITA: 1960-1998 (39 years) divided by 1936.27
* fx LVA: 1992-2013 (22 years) divided by 0.702804
* fx LBR: national accounts in US dollars; official rate set to 1 (the local currency uses its own rate)
* fx LTU: 1992-2014 (23 years) divided by 3.4528
* fx LUX: 1960-1998 (39 years) divided by 40.3399
* fx MLT: 1960-2007 (48 years) divided by 0.4293
* fx MCO: 1960-1998 (39 years) divided by 6.55957
* fx NLD: 1960-1998 (39 years) divided by 2.20371
* fx PRT: 1960-1998 (39 years) divided by 200.482
* fx SMR: 1972-1998 (27 years) divided by 1936.27
* fx SVK: 1993-2008 (16 years) divided by 30.126
* fx SVN: 1991-2006 (16 years) divided by 239.64
* fx ESP: 1960-1998 (39 years) divided by 166.386
* fx TKM: 1994-2001 (8 years) divided by 5000
* fx VEN: 1960-2017 (58 years) divided by 1e+11
* fx PSE: national accounts in US dollars; official rate set to 1 (the local currency uses its own rate)
* fx ZMB: 1960-1971 (12 years) divided by 1000
* fx ZWE: 1998-2023 (15 years) divided by 2498.72

## GDP deflator rebasing breaks

The standard GDP deflator (NY.GDP.DEFL.ZS) jumps where a country rebased its national accounts. The app uses the linked series (NY.GDP.DEFL.ZS.AD) by default; the years below are flagged when the standard series is chosen.

50 economies have at least one year where the two series' growth differs by more than 10%.

| Economy | Year (standard vs linked growth) |
|---|---|
| Albania | 1995 (+34% vs +10%) |
| Angola | 2002 (+236% vs +142%) |
| Bahamas, The | 1997 (+73% vs +2%) |
| Bangladesh | 1996 (+19% vs +4%); 2016 (+28% vs +7%) |
| Barbados | 2010 (+32% vs +4%) |
| Benin | 1999 (+48% vs +9%) |
| Bermuda | 2006 (+20% vs +5%) |
| Bolivia | 2017 (+30% vs +6%) |
| Bosnia and Herzegovina | 2000 (+30% vs +6%) |
| Burundi | 2000 (+39% vs +13%) |
| Cabo Verde | 2007 (+19% vs +1%) |
| Cameroon | 1993 (+56% vs +40%) |
| Chad | 2005 (+67% vs +23%) |
| Colombia | 2000 (+34% vs +11%) |
| Cote d'Ivoire | 1996 (+56% vs +5%) |
| Dominica | 2001 (+13% vs +2%) |
| Dominican Republic | 1991 (+103% vs +58%) |
| Equatorial Guinea | 2000 (+65% vs +47%); 2005 (+59% vs +43%) |
| Eritrea | 1994 (+10% vs +22%) |
| Eswatini | 2000 (+22% vs +10%) |
| Gambia, The | 1991 (+134% vs +8%); 1997 (-6% vs +4%); 2001 (+2% vs +15%); 2003 (+13% vs +27%) |
| Ghana | 2006 (+85% vs +13%); 2013 (+54% vs +16%) |
| Guatemala | 2001 (-6% vs +8%) |
| Guyana | 2006 (+175% vs +6%) |
| Haiti | 2000 (+91% vs +11%) |
| Jordan | 2008 (+40% vs +24%) |
| Kenya | 1996 (+42% vs +9%); 2006 (+24% vs +8%); 2009 (+28% vs +12%) |
| Malawi | 2002 (+113% vs +62%) |
| Mauritania | 1991 (+41% vs +11%) |
| Mexico | 1993 (+43% vs +9%) |
| Moldova | 2010 (+33% vs +11%) |
| Morocco | 1998 (+12% vs +0%) |
| Nicaragua | 1991 (+4524% vs +2932%); 1994 (+134% vs +8%) |
| Nigeria | 2019 (+55% vs +10%) |
| Pakistan | 2000 (+68% vs +4%) |
| Panama | 1996 (-8% vs +2%) |
| Papua New Guinea | 2006 (+61% vs +9%) |
| Rwanda | 1999 (+11% vs -4%) |
| Sierra Leone | 2001 (+168% vs +71%) |
| Solomon Islands | 1994 (+28% vs +7%); 2003 (+26% vs +6%) |
| Sri Lanka | 2010 (+27% vs +7%) |
| Suriname | 1991 (+12% vs +33%); 1995 (+277% vs +240%); 1996 (+12% vs +1%); 2006 (+39% vs +13%) |
| Turkiye | 1995 (+158% vs +86%) |
| Turkmenistan | 1996 (+1014% vs +1174%); 2000 (+23% vs +10%); 2001 (+32% vs +15%); 2002 (+25% vs +8%); 2003 (+27% vs +12%); 2004 (+18% vs +6%) |
| Uganda | 2009 (+85% vs +15%) |
| Uzbekistan | 2010 (+66% vs +39%) |
| Vanuatu | 2013 (+17% vs +3%) |
| Venezuela, RB | 2014 (+105% vs +67%) |
| Viet Nam | 2010 (+42% vs +12%) |
| Zimbabwe | 2009 (+93% vs +25%); 2019 (+397% vs +225%) |

## Official vs alternative exchange rate

Years where the official rate differs from the World Bank's alternative conversion factor by more than 10% (multiple or unrepresentative official rates). The app warns in these years and offers the alternative rate.

| Economy | Years | Official / alternative |
|---|---|---|
| Afghanistan | 1960-1992 | 0.382 to 0.86 |
| Angola | 1991-1994, 1996, 2015-2020, 2024-2025 | 0.39 to 1.15 |
| Argentina | 1971-1974, 1976-1977, 1979-1981, 2013 | 0.368 to 0.904 |
| Armenia | 1993-1995 | 1.14 to 2.59 |
| Australia | 1973, 2003, 2015 | 0.898 to 1.11 |
| Bangladesh | 1971-1972, 1975, 1981-1982 | 1.1 to 1.64 |
| Belarus | 1994-1995, 2000 | 1.22 to 3.06 |
| Benin | 1992 | 0.755 to 0.755 |
| Bermuda | 1960-1967 | 0.857 to 0.869 |
| Brazil | 1960-1989 | 1.19 to 1.19 |
| Burundi | 2016-2025 | 0.552 to 0.894 |
| Cambodia | 1990-1991 | 0.794 to 0.878 |
| Chile | 1982 | 0.771 to 0.771 |
| China | 1978-1984, 1987-1989, 1992-1993 | 0.624 to 0.866 |
| Congo, Dem. Rep. | 1999-2001 | 0.316 to 0.689 |
| Cyprus | 1970-1979 | 0.694 to 0.74 |
| Egypt, Arab Rep. | 1971-1972, 1974-1978, 1982-1990, 2003, 2016-2017, 2022-2024 | 0.398 to 1.27 |
| Equatorial Guinea | 1960-1984 | 1.33 to 4.17 |
| Eritrea | 1992, 1994 | 0.612 to 0.888 |
| Estonia | 1993-1995 | 1.15 to 2.24 |
| Ethiopia | 1993, 2009-2010, 2023 | 0.85 to 1.17 |
| Gabon | 1993 | 0.81 to 0.81 |
| Ghana | 1974-1985 | 0.128 to 0.714 |
| Grenada | 1975 | 0.804 to 0.804 |
| Guatemala | 1985-1986 | 0.856 to 0.87 |
| Guinea-Bissau | 1960-1996 | 1.26 to 588 |
| Haiti | 1991 | 1.16 to 1.16 |
| Honduras | 1988-1989 | 0.69 to 0.858 |
| India | 1966 | 0.903 to 0.903 |
| Iran, Islamic Rep. | 1987-2002, 2013, 2018-2023 | 0.109 to 0.899 |
| Iraq | 1971-2002 | 1.61 to 6.46e+03 |
| Israel | 1960-1961, 1968-1970, 1974 | 0.9 to 1.17 |
| Kazakhstan | 1994-1995 | 1.22 to 1.78 |
| Kiribati | 1974 | 1.63 to 1.63 |
| Kyrgyz Republic | 1994-1995 | 1.11 to 1.52 |
| Lao PDR | 1960-1979, 1985 | 0.833 to 2.06e+03 |
| Lebanon | 2020-2023 | 0.0552 to 0.409 |
| Lithuania | 1995 | 1.17 to 1.17 |
| Moldova | 1995 | 1.22 to 1.22 |
| Mongolia | 1991-1992 | 0.841 to 0.843 |
| Myanmar | 1960-2012 | 0.00486 to 0.749 |
| Naoero | 1973, 2003, 2015 | 0.898 to 1.11 |
| Nepal | 1963-1964, 1991 | 0.752 to 1.18 |
| New Zealand | 1960-1964 | 1.39 to 1.39 |
| Nicaragua | 1965-1983, 1985-1988, 1991 | 0.147 to 2.19 |
| Nigeria | 1971-1990 | 0.34 to 0.878 |
| Pakistan | 1972, 1982, 2008, 2018, 2022-2023 | 1.11 to 1.49 |
| Paraguay | 1983-1988 | 0.655 to 0.863 |
| Peru | 1988-1990 | 0.515 to 0.908 |
| Romania | 1987-1989, 1992 | 0.656 to 1.28 |
| Russian Federation | 1993 | 2.52 to 2.52 |
| Rwanda | 1994 | 0.64 to 0.64 |
| Sierra Leone | 1960-1964 | 1.17 to 1.17 |
| Singapore | 1973 | 0.874 to 0.874 |
| Somalia, Fed. Rep. | 1977-1988 | 0.2 to 0.632 |
| South Sudan | 2016-2018, 2021-2024 | 1.11 to 2.76 |
| Sri Lanka | 1963-1964 | 0.8 to 0.8 |
| St. Martin (French part) | 1960-1998 | 6.56 to 6.56 |
| Sudan | 2009-2020 | 0.318 to 0.885 |
| Suriname | 1972-1994, 2020 | 0.0525 to 1.66 |
| Syrian Arab Republic | 1965, 1968-1978, 1985-2010, 2013, 2015, 2019-2022 | 0.215 to 1.27 |
| Tajikistan | 1992-1995 | 1.85 to 7.28 |
| Turkmenistan | 1994-1995, 1999-2001 | 0.422 to 0.635 |
| Tuvalu | 1973 | 0.902 to 0.902 |
| Uganda | 1960-1964, 1975-1992, 1994, 2015 | 0.0742 to 2.16 |
| Ukraine | 1993-1995 | 1.3 to 2.01 |
| Uzbekistan | 1995 | 1.31 to 1.31 |
| Venezuela, RB | 2013-2017 | 0.00332 to 0.641 |
| Viet Nam | 1991 | 1.27 to 1.27 |
| Yemen, Rep. | 1996, 2017-2019 | 0.401 to 0.845 |
| Zambia | 1990 | 0.879 to 0.879 |
| Zimbabwe | 1960-2008, 2020-2025 | 0.0237 to 6.73e+09 |

## Stale series

Series whose last value is more than 3 years before 2025. The app does not project these.

| Economy | Series | Last year |
|---|---|---|
| Afghanistan | Official exchange rate | 2020 |
| Aruba | CPI | 2019 |
| Cayman Islands | CPI | 2016 |
| Congo, Dem. Rep. | CPI | 2016 |
| Cuba | Official exchange rate | 1974 |
| Cuba | Alternative conversion factor | 2020 |
| Cuba | PPP (World Bank) | 2011 |
| Curacao | CPI | 2019 |
| Eritrea | GDP deflator | 2011 |
| Eritrea | PPP (World Bank) | 2021 |
| Eswatini | CPI | 2019 |
| Guinea | Official exchange rate | 2020 |
| Liechtenstein | GDP deflator | 2009 |
| Myanmar | CPI | 2019 |
| Myanmar | Official exchange rate | 2020 |
| Naoero | CPI | 2012 |
| New Caledonia | CPI | 2016 |
| Sint Maarten (Dutch part) | CPI | 2017 |
| Somalia, Fed. Rep. | Official exchange rate | 2017 |
| South Sudan | GDP deflator | 2015 |
| South Sudan | PPP (World Bank) | 2021 |
| St. Martin (French part) | GDP deflator | 2021 |
| Syrian Arab Republic | CPI | 2019 |
| Turkmenistan | Official exchange rate | 2001 |
| Tuvalu | CPI | 2011 |
| Venezuela, RB | CPI | 2016 |
| Venezuela, RB | Official exchange rate | 2017 |
| Venezuela, RB | PPP (World Bank) | 2011 |
| Yemen, Rep. | GDP deflator | 2018 |
| Yemen, Rep. | CPI | 2014 |
| Yemen, Rep. | PPP (World Bank) | 2013 |

## PPP vs GDP before 2022 (not unit errors)

In these years the World Bank PPP differs from GDP in LCU / GDP in PPP dollars by more than 2%. The ratios are constant over runs of years and match national-accounts rebasing (GDP levels were revised, PPPs were not). They are listed for transparency; the app uses the published PPPs.

| Economy | Years | Ratio |
|---|---|---|
| Albania | 1990-1994 | 1.22 to 1.22 |
| Algeria | 1990-2000 | 1.09 to 1.09 |
| Angola | 1990-2001 | 1.39 to 1.39 |
| Aruba | 1990-2000 | 0.92 to 0.92 |
| Bahamas, The | 1990-1996 | 1.7 to 1.7 |
| Bangladesh | 1990-2015 | 1.2 to 1.37 |
| Barbados | 1990-2009 | 1.27 to 1.27 |
| Benin | 1990-1998 | 1.37 to 1.38 |
| Bermuda | 1990-2005 | 1.13 to 1.13 |
| Bhutan | 1990-1999 | 1.09 to 1.09 |
| Bolivia | 1990-2016 | 1.22 to 1.22 |
| Bosnia and Herzegovina | 1990-1999 | 1.23 to 1.23 |
| Botswana | 1990-2005 | 0.978 to 0.978 |
| Burundi | 1990-1999 | 1.23 to 1.23 |
| Cabo Verde | 1990-2006 | 1.03 to 1.17 |
| Cameroon | 1990-1992, 1994-1998 | 1.03 to 1.13 |
| Chad | 1990-2004 | 1.36 to 1.36 |
| Colombia | 1990-1999 | 1.2 to 1.2 |
| Congo, Rep. | 1990-2004 | 1.09 to 1.09 |
| Cote d'Ivoire | 1990-1995 | 1.49 to 1.49 |
| Dominica | 1990-2000 | 1.11 to 1.11 |
| Dominican Republic | 1990 | 1.28 to 1.28 |
| Ecuador | 1990-1999 | 0.957 to 0.957 |
| Equatorial Guinea | 1990-2004 | 1.12 to 1.26 |
| Eritrea | 1992-1993 | 0.892 to 0.892 |
| Eswatini | 1990-1999 | 1.11 to 1.11 |
| Gabon | 1990-2000 | 1.06 to 1.06 |
| Gambia, The | 1990-2002 | 0.649 to 1.41 |
| Ghana | 1990-2012 | 1.33 to 2.18 |
| Guatemala | 1990-2000 | 0.877 to 0.877 |
| Guyana | 1990-2006 | 0.96 to 2.5 |
| Haiti | 1990-1999 | 1.72 to 1.72 |
| India | 1990-2021 | 0.971 to 0.971 |
| Iran, Islamic Rep. | 1990-2015 | 1.04 to 1.12 |
| Jamaica | 1991-2014 | 1.05 to 1.08 |
| Jordan | 1990-2007 | 1.13 to 1.13 |
| Kenya | 1990-2008 | 1.14 to 1.71 |
| Malawi | 1990-2001 | 1.26 to 1.31 |
| Maldives | 2003-2004 | 0.974 to 0.975 |
| Malta | 1990-1994 | 1.08 to 1.08 |
| Mauritania | 1990-2013 | 0.948 to 1.24 |
| Mexico | 1990-1992 | 1.3 to 1.3 |
| Moldova | 1990-2009 | 1.19 to 1.19 |
| Morocco | 1990-1997 | 1.11 to 1.11 |
| Namibia | 1990-1993 | 1.04 to 1.05 |
| Nepal | 1990-2000 | 1.07 to 1.07 |
| Nicaragua | 1990-1993 | 2.17 to 3.31 |
| Nigeria | 1990-2018 | 1.41 to 1.43 |
| Pakistan | 1990-1999 | 1.62 to 1.62 |
| Panama | 1990-1995 | 0.905 to 0.905 |
| Papua New Guinea | 1990-2010 | 1.04 to 1.57 |
| Rwanda | 1990-1998 | 1.15 to 1.15 |
| Sierra Leone | 1990-2000 | 1.56 to 1.56 |
| Sint Maarten (Dutch part) | 2009-2013 | 1.09 to 1.09 |
| Solomon Islands | 1990-2002 | 1.18 to 1.46 |
| Sri Lanka | 1990-2009 | 1.18 to 1.28 |
| St. Kitts and Nevis | 1990-1999 | 0.92 to 0.92 |
| St. Lucia | 1996-1999 | 0.972 to 0.972 |
| St. Vincent and the Grenadines | 1990-2007 | 0.953 to 0.953 |
| Suriname | 1990-2005 | 1.23 to 1.68 |
| Tunisia | 1990-2009 | 1.05 to 1.16 |
| Turkiye | 1990-1994 | 1.39 to 1.39 |
| Turkmenistan | 1990-2003 | 1.12 to 1.9 |
| Uganda | 1990-2008 | 1.62 to 1.62 |
| Uruguay | 1990-1996 | 1.07 to 1.07 |
| Uzbekistan | 1990-2009 | 1.19 to 1.19 |
| Vanuatu | 1990-2012 | 1.1 to 1.14 |
| Venezuela, RB | 1990-2011 | 1.23 to 1.23 |
| Viet Nam | 1990-2009 | 1.27 to 1.27 |
| West Bank and Gaza | 1994-2013 | 1.05 to 1.05 |
| Zimbabwe | 1990-2018 | 1.53 to 2.37 |

## OECD vs World Bank PPP differing by more than 10%

| Economy | Years | OECD / World Bank |
|---|---|---|
| Colombia | 1990-1998 | 0.787 to 0.902 |
| Georgia | 1990-1991 | 1.18 to 1.84 |

## Other notes

* ppp_oecd ISR 1977: no reference value; left as published
