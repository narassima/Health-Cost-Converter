// Tests for the Health Cost Converter. Run: node tests/run.js [path/to/Cost_Converter.html]
// Loads the calculator's own script from the built page and checks it against the paper, the CCEMG-EPPI tool,
// currency units, number parsing and the cases in the critical appraisal.
"use strict";
const H = require("./load.js")(process.argv[2]);
const EPPI = require("./eppi_cases.json");

let pass = 0, fail = 0;
function check(name, cond, info) {
  if (cond) pass++; else { fail++; console.log("FAIL " + name + (info !== undefined ? ": " + JSON.stringify(info) : "")); }
}
const near = (a, b, tol) => a != null && b != null && Math.abs(a - b) <= tol;
const rel = (a, b, tol) => a != null && b != null && Math.abs(a / b - 1) <= tol;
const clear = () => { Object.keys(H.OV).forEach((k) => delete H.OV[k]); H.PROJ.how = "weo"; H.PROJ.fx = "gap"; H.PROJ_LOG.clear(); };
const SET = (o) => Object.assign({ y1: 2016, out: "USD", tIso: "USA", basis: "fx", measure: "gdpd_l", fxSrc: "fx", pppSrc: "ppp", share: 0.2 }, o);
const run = (inp, o) => H.compute(Object.assign({ cur: "LCU", old: "" }, inp), SET(o));
const texts = (r) => H.checks(r).map((c) => c.cls + "|" + c.text.replace(/<[^>]+>/g, ""));
const hasCheck = (r, re, cls) => H.checks(r).some((c) => re.test(c.text) && (cls === undefined || c.cls === cls));

/* 1. Turner et al. (2019), Figures 1, 2 and 4, with the paper's rates and indices typed in */
function paper() {
  H.OV["fx:VNM:2006"] = 15994.25; H.OV["fx:VNM:2016"] = 21935;
  H.OV["gdpd_l:VNM:2016"] = H.raw("gdpd_l", "VNM", 2006) * 2.360037;
  H.OV["gdpd_l:USA:2016"] = H.raw("gdpd_l", "USA", 2006) * 1.1684;
}
clear(); paper();
let r = run({ cost: 1e6, iso: "VNM", y0: 2006 });
check("paper M1 73.05", near(r.v1, 73.05, 0.005), r.v1);
check("paper M2 107.59", near(r.v2, 107.59, 0.005), r.v2);
check("paper M3 100.68", near(r.v3, 100.68, 0.005), r.v3);
r = run({ cost: 100, cur: "USD", iso: "VNM", y0: 2006 });
check("paper US$ M1 116.84", near(r.v1, 116.84, 0.005), r.v1);
check("paper US$ M2 172.09", near(r.v2, 172.09, 0.005), r.v2);
check("paper US$ M3 161.04", near(r.v3, 161.04, 0.005), r.v3);
check("paper uses typed values note", hasCheck(r, /typed in by hand/));

/* 2. CCEMG-EPPI v1.7: with EPPI's own deflators and PPPs typed in, Method 2 must equal EPPI's result */
EPPI.forEach((c) => {
  clear();
  const e = c.eppi;
  H.OV["gdpd_l:" + c.iso + ":" + c.y0] = +e.lblSourceGDPD;
  H.OV["gdpd_l:" + c.iso + ":" + c.y1] = +e.lblTargetGDPD;
  H.OV["ppp:" + c.iso + ":" + c.y1] = +e.lblTargetPPP;
  H.OV["ppp:" + c.tiso + ":" + c.y1] = +e.lblTargetCountryPPP2;
  const x = run({ cost: c.cost, iso: c.iso, y0: c.y0 }, { y1: c.y1, out: "LCU", tIso: c.tiso, basis: "ppp" });
  check("EPPI case " + c.id + " " + c.iso + "->" + c.tiso, rel(x.v2, +e.lblStage2, 5e-5) || near(x.v2, +e.lblStage2, 0.01), [x.v2, +e.lblStage2]);
});
check("31 EPPI cases", EPPI.length === 31, EPPI.length);

/* 3. Currency units (appraisal C1-C3) */
clear();
r = run({ cost: 100, iso: "BGR", y0: 2020, old: "BGN" }, { y1: 2020, out: "INT" });
check("Bulgaria BGN 100 (2020) = I$ 148", near(r.v2, 148.1, 0.5), r.v2);
const pl = H.raw("ppp", "BGR", 2020) / H.raw("fx", "BGR", 2020);
check("Bulgaria price level 2020 about 39% of US", pl > 0.33 && pl < 0.45, pl);
const a = run({ cost: 72e9, iso: "SLE", y0: 2017 }, { y1: 2017 });
const b = run({ cost: 72e9, iso: "SLE", y0: 2017, old: "SLL" }, { y1: 2017 });
check("Sierra Leone SLL is 1000 x SLE", rel(a.v2 / b.v2, 1000, 1e-9), a.v2 / b.v2);
check("Sierra Leone 72bn read as SLE warns (GDP share)", hasCheck(a, /% of Sierra Leone's GDP/, "bad"), texts(a));
check("Sierra Leone 72bn read as SLE suggests SLL", hasCheck(a, /SLL/), texts(a));
check("Sierra Leone with SLL no GDP warning", !hasCheck(b, /GDP in/), texts(b));
r = run({ cost: 1e6, iso: "GHA", y0: 2005, old: "GHC" }, { y1: 2005 });
check("Ghana 1,000,000 GHC (2005) about US$ 110", near(r.v2, 110, 5), r.v2);
r = run({ cost: 1e6, iso: "TUR", y0: 2004, old: "TRL" }, { y1: 2004 });
check("Turkey TRL divided by 1,000,000", rel(r.CS, 1, 1e-12), r.CS);
r = run({ cost: 1000, iso: "DEU", y0: 1995, old: "DEM" }, { y1: 1995 });
check("Germany DEM divided by 1.95583", rel(r.CS, 1000 / 1.95583, 1e-12), r.CS);
const ves = H.DATA.countries.find((c) => c.iso === "VEN").old.map((o) => o.code);
check("Venezuela old codes distinct from VES", ves.indexOf("VES") < 0 && ves.indexOf("VES2018") >= 0 && ves.indexOf("VEF") >= 0, ves);
r = run({ cost: 1000, iso: "VEN", y0: 2015, old: "VEF" }, { y1: 2015, fxSrc: "fx" });
check("Venezuela VEF 2015 converts", r.v2 != null && r.v2 > 0, r.v2);
r = run({ cost: 100, iso: "ECU", y0: 1995 }, { y1: 1995 });
check("Ecuador 1995 read as US$ warns about sucres", hasCheck(r, /ECS/), texts(r));
const ecu = run({ cost: 2564, iso: "ECU", y0: 1995, old: "ECS" }, { y1: 1995 });
check("Ecuador ECS converted at the 1995 rate", rel(ecu.CS, 2564 / H.raw("oldfx", "ECU", 1995), 1e-12) && ecu.CS > 0.5 && ecu.CS < 1.5, ecu.CS);
r = run({ cost: 100, iso: "PSE", y0: 2015 }, { y1: 2020 });
check("West Bank and Gaza converts to US$", r.v1 != null && r.v2 != null, [r.v1, r.v2]);
check("West Bank and Gaza amount suggests ILS", hasCheck(r, /ILS/), texts(r));

/* 4. Units: PPP against the alternative rate gives a plausible price level everywhere */
const unitBad = [];
H.DATA.countries.forEach((c) => {
  for (let y = 1990; y <= 2024; y++) {
    const fx = H.raw("fx_alt", c.iso, y), p = H.raw("ppp", c.iso, y);
    if (fx && p && (p / fx < 0.01 || p / fx > 5)) unitBad.push(c.iso + y);
  }
});
check("PPP / alternative rate price level within 1%-500% everywhere (Azerbaijan 1992 is 1.4%)", unitBad.length === 0, unitBad.slice(0, 10));

/* 5. Deflator breaks (C4) */
clear();
r = run({ cost: 1e6, iso: "VNM", y0: 2006 });
check("Viet Nam linked deflator 2006-2016 about 2.29", near(r.infS, 2.29, 0.02), r.infS);
r = run({ cost: 1e6, iso: "VNM", y0: 2006 }, { measure: "gdpd" });
check("Viet Nam standard deflator flags the 2010 break", hasCheck(r, /rebased/), texts(r));
r = run({ cost: 1e6, iso: "GHA", y0: 2009 });
check("Ghana linked deflator 2009-2016 about 2.87 (paper Box 2: 2.83)", near(r.infS, 2.87, 0.05), r.infS);

/* 6. Official against alternative exchange rates (C5) */
r = run({ cost: 1e6, iso: "LBN", y0: 2022 }, { y1: 2022 });
check("Lebanon 2022 official rate warns", hasCheck(r, /alternative conversion factor/), texts(r));
const lo = run({ cost: 1e6, iso: "LBN", y0: 2022 }, { y1: 2022, fxSrc: "fx_alt" });
check("Lebanon 2022 alternative factor gives a smaller US$ value", lo.v2 < r.v2 / 5, [r.v2, lo.v2]);

/* 7. Projections (C6, U1) */
clear();
r = run({ cost: 5000, iso: "IND", y0: 2022 }, { y1: 2030, out: "LCU", tIso: "IND" });
check("India 2022->2030 projected", r.projected, r.projected);
check("India 2022->2030 no errors", !H.checks(r).some((c) => c.cls === "bad"), texts(r));
check("India 2022->2030 projected note uses class note", H.checks(r).some((c) => c.cls === "note" && /projected/.test(c.text)));
check("India projection uses IMF WEO", Array.from(H.PROJ_LOG.values()).some((e) => e.how === "weo"));
check("Projected results to 3 significant figures", H.num(6596.6, true) === "6,600", H.num(6596.6, true));
const bd = H.band({ cost: 5000, cur: "LCU", iso: "IND", y0: 2022, old: "" }, SET({ y1: 2030, out: "LCU", tIso: "IND" }), r);
check("Projection band is ordered", bd[1][0] > 0 && bd[1][0] <= r.v2 && r.v2 <= bd[1][1], [bd[1], r.v2]);
check("Band leaves the projection rule unchanged", H.PROJ.how === "weo", H.PROJ.how);
r = run({ cost: 1000, iso: "TKM", y0: 2015 }, { y1: 2015 });
check("Turkmenistan official rate (ends 2001) is not projected", r.v2 == null && hasCheck(r, /ends in/, "bad"), texts(r));
r = run({ cost: 1000, iso: "TKM", y0: 2015 }, { y1: 2015, fxSrc: "fx_alt" });
check("Turkmenistan alternative factor works", r.v2 != null, r.v2);
H.PROJ.how = 10;
r = run({ cost: 1000, iso: "ARG", y0: 2020 }, { y1: 2032, out: "LCU", tIso: "ARG" });
check("Argentina 10-year trend flagged above 15%", hasCheck(r, /very uncertain/), texts(r));
clear();

/* 8. Number parsing (U2) */
const P = (s, m) => H.parseAmount(s, m || "auto").v;
[["12,5", 12.5], ["1,5", 1.5], ["1.234,56", 1234.56], ["£1,200", 1200], ["1.000.000", 1e6], ["1,000,000", 1e6], ["2500.50", 2500.5],
 ["1 234,5", 1234.5], ["€ 0,1206", 0.1206], ["US$ 3.5", 3.5], ["1e6", 1e6], ["-12,5", -12.5]].forEach((t) =>
  check("parse " + t[0], P(t[0]) === t[1], P(t[0])));
check("parse 1,000 auto is ambiguous", H.parseAmount("1,000", "auto").amb === true);
check("parse 1,000 with comma decimal = 1", P("1,000", ",") === 1);
check("parse 1.000 with comma decimal = 1000", P("1.000", ",") === 1000);
check("parse rejects 1,00,0", P("1,00,0", ".") === null);
check("parse rejects text", P("abc") === null);

/* 9. List mode (U3, U4) */
const m = H.guessMap(["Row", "Study", "Cost item", "Amount", "Currency", "Price year", "Country", "Publication year"]);
check("header: Cost item is not the amount", m.cost === 3, m);
check("header: Price year preferred", m.year === 5, m);
check("header: Country found", m.country === 6, m);
check("fiscal 2015-16 avg", JSON.stringify(H.readYear("2015-16", "avg")) === JSON.stringify({ y: 2015, y2: 2016, fy: "2015-16" }));
check("fiscal 2015/16 end", H.readYear("2015/16", "end").y === 2016);
check("fiscal refused when not allowed", !!H.readYear("2015/16", "cal").err);
check("SLL accepted in lists", H.readCurrency("SLL", "SLE").old === "SLL");
check("DEM accepted in lists", H.readCurrency("DEM", "DEU").old === "DEM");
const L = H.convertList("Study\tCost item\tAmount\tCountry\tPrice year\tCurrency\n" +
  "Nemeth\tvisit\t0,1206\tHungary\t2016\tEUR\n" +
  "SL\ttotal\t72000000000\tSierra Leone\t2017\t\n" +
  "EC\ttotal\t100\tEcuador\t1995\t\n" +
  "UK\tunit\t1200\tUnited Kingdom\t2015/16\tGBP\n" +
  "NoC\tx\t5\tAtlantis\t2015\t", SET({ y1: 2024, out: "INT" }), { dec: "auto", fy: "avg" });
check("list: EUR for Hungary rejected", /does not match/.test(L.rows[0].note), L.rows[0].note);
check("list: Sierra Leone flagged", /GDP/.test(L.rows[1].note), L.rows[1].note);
check("list: Ecuador 1995 note", /ECS/.test(L.rows[2].warn + L.rows[2].note), L.rows[2]);
check("list: fiscal year averaged", L.rows[3].yUsed === "avg 2015/2016" && L.rows[3].v[1] > 0, L.rows[3]);
check("list: unknown country", /not recognised/.test(L.rows[4].note), L.rows[4].note);
const L2 = H.convertList("Study\tAmount\tCountry\tPrice year\tCurrency\nNemeth\t0,1206\tHungary\t2016\tHUF", SET({ y1: 2016, out: "LCU", tIso: "HUN" }), {});
check("list: decimal comma and full precision kept", near(L2.rows[0].v[1], 0.1206, 1e-12), L2.rows[0].v);
H.OV["fx:HUN:2016"] = 300;
const L3 = H.convertList("Study\tAmount\tCountry\tPrice year\tCurrency\nX\t1000\tHungary\t2016\tHUF", SET({ y1: 2016, out: "USD" }), {});
check("list: typed values are reported", /your values/.test(L3.rows[0].warn), L3.rows[0]);
clear();
const L4 = H.convertList("Amount\tPrice year\n5\t2015", SET({}), {});
check("list: missing Country column is an error", /Country/.test(L4.err), L4.err);

console.log((fail ? "FAILED " : "OK ") + pass + " passed, " + fail + " failed (version " + H.VERSION + ", WDI " + H.DATA.meta.wdi_updated + ")");
process.exit(fail ? 1 : 0);
