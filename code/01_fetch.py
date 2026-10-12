"""
01_fetch.py -- Download all raw data for the Morocco democratization gap analysis.
Sources: World Bank WDI + EdStats API, Barro-Lee v3 (2021), V-Dem via OWID, Maddison via OWID.
"""
import os, sys, time, json, io, ssl, certifi
import urllib.request
import pandas as pd

# This Python build ships without root certificates; point it at certifi.
SSLCTX = ssl.create_default_context(cafile=certifi.where())

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
RAW = os.path.abspath(RAW)
os.makedirs(RAW, exist_ok=True)

def get(url, dest, force=False):
    if os.path.exists(dest) and not force and os.path.getsize(dest) > 0:
        print(f"  cached  {os.path.basename(dest)}")
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
    with urllib.request.urlopen(req, timeout=180, context=SSLCTX) as r:
        blob = r.read()
    head = blob[:200].lstrip()
    if head.startswith(b"{") and b'"error"' in head:      # an API error page, not data
        raise RuntimeError(f"{url} returned an error body: {head[:80]!r}")
    with open(dest, "wb") as f:
        f.write(blob)
    print(f"  fetched {os.path.basename(dest)}  ({os.path.getsize(dest)/1024:.0f} KB)")
    return dest

# ---------------------------------------------------------------- World Bank
WDI = {
    "NY.GDP.PCAP.PP.KD": "GDP pc, PPP const 2021 intl $",
    "NY.GDP.PCAP.KD":    "GDP pc, const 2015 US$",
    "SE.ADT.LITR.ZS":    "Adult literacy rate, 15+",
    "SE.ADT.1524.LT.ZS": "Youth literacy rate, 15-24",
    "SE.SEC.ENRR":       "Gross enrolment, secondary",
    "SE.SEC.NENR":       "Net enrolment, secondary",
    "SE.TER.ENRR":       "Gross enrolment, tertiary",
    "SE.PRM.ENRR":       "Gross enrolment, primary",
    "HD.HCI.HLOS":       "Harmonized test scores",
    "HD.HCI.OVRL":       "Human Capital Index",
    "SE.LPV.PRIM":       "Learning poverty, primary age",
    "SE.SEC.CUAT.UP.ZS": "Pop 25+ with at least upper secondary (%)",
    "SE.SEC.CUAT.LO.ZS": "Pop 25+ with at least lower secondary (%)",
    "SE.PRM.CUAT.ZS":    "Pop 25+ with at least primary (%)",
    "SE.TER.CUAT.BA.ZS": "Pop 25+ with at least bachelor (%)",
    "SE.SCH.LIFE":       "School life expectancy, years",
    "SP.POP.TOTL":       "Population",
    "SL.TLF.CACT.FE.ZS": "Female labour force participation, 15+ (ILO)",
    "NY.GDP.TOTL.RT.ZS": "Total natural resources rents (% GDP)",
    "SI.POV.GINI":       "Gini index",
}
EDSTATS = {   # Barro-Lee v2.2 mirrored in WB EdStats (source=12)
    "BAR.SCHL.15UP":       "BL: avg years total schooling, 15+",
    "BAR.SCHL.25UP":       "BL: avg years total schooling, 25+",
    "BAR.NOED.15UP.ZS":    "BL: % 15+ with no schooling",
    "BAR.SEC.SCHL.15UP":   "BL: avg years secondary schooling, 15+",
    "BAR.TER.SCHL.15UP":   "BL: avg years tertiary schooling, 15+",
    "BAR.SEC.CMPT.15UP.ZS":"BL: % 15+ completed secondary",
}

def wb_indicator(code, source=2):
    """Fetch a full country-year panel for one indicator from the WB API.

    The explicit date range is required: without it the API returns only its own default
    year window, which it narrowed in 2026 (adult literacy came back as 176 observations
    instead of 2,804, and 02_build.py then died on the missing column)."""
    rows, page = [], 1
    while True:
        url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
               f"?format=json&per_page=20000&page={page}&source={source}&date=1960:2026")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
        with urllib.request.urlopen(req, timeout=180, context=SSLCTX) as r:
            js = json.loads(r.read().decode())
        if not isinstance(js, list) or len(js) < 2 or js[1] is None:
            break
        meta, data = js[0], js[1]
        for d in data:
            if d.get("value") is None:
                continue
            rows.append({"iso3": d.get("countryiso3code"), "country": d["country"]["value"],
                         "year": int(d["date"]), "indicator": code, "value": d["value"]})
        if page >= meta["pages"]:
            break
        page += 1
    return pd.DataFrame(rows)

def fetch_wb(dic, source, fname):
    dest = os.path.join(RAW, fname)
    if os.path.exists(dest):
        print(f"  cached  {fname}")
        return
    out = []
    for code in dic:
        try:
            df = wb_indicator(code, source=source)
            print(f"    {code:22s} {len(df):7d} obs")
            out.append(df)
        except Exception as e:
            print(f"    {code:22s} FAILED: {e}")
        time.sleep(0.3)
    pd.concat(out, ignore_index=True).to_csv(dest, index=False)
    print(f"  fetched {fname}")

print("[1/4] World Bank WDI ...")
fetch_wb(WDI, 2, "wdi_long.csv")
print("[2/4] World Bank EdStats (Barro-Lee v2.2) ...")
fetch_wb(EDSTATS, 12, "edstats_long.csv")

# ---------------------------------------------------------------- Barro-Lee v3
print("[3/4] Barro-Lee v3 (2021 update) ...")
BL = "https://raw.githubusercontent.com/barrolee/BarroLeeDataSet/master/BLData/"
for f in ["BL_v3_MF1564.csv", "BL_v3_MF2564.csv", "BL_v3_F2564.csv",
          "BL_v3_M2564.csv", "BL_v3_F1564.csv", "BL_v3_M1564.csv"]:
    get(BL + f, os.path.join(RAW, f))

# ---------------------------------------------------------------- OWID
print("[4/4] OWID (V-Dem, Maddison, literacy) ...")
OWID = {
    "electoral-democracy-index":   "vdem_electdem.csv",
    "liberal-democracy-index":     "vdem_libdem.csv",
    "political-regime":            "vdem_regime.csv",
    "gdp-per-capita-maddison":     "maddison_gdppc.csv",
    "mean-years-of-schooling-long-run": "owid_mys_longrun.csv",
    "average-years-of-schooling":  "owid_mys_undp.csv",
    "cross-country-literacy-rates":"owid_literacy.csv",
    "political-corruption-index":  "owid_political-corruption-index.csv",
    "civil-liberties-index-vdem":  "owid_civil-liberties-index-vdem.csv",
    "participatory-democracy-index":"owid_participatory-democracy-index.csv",
    "rule-of-law-index":           "owid_rule-of-law-index.csv",
    "freedom-of-expression-index": "owid_freedom-of-expression-index.csv",
}
for slug, fname in OWID.items():
    get(f"https://ourworldindata.org/grapher/{slug}.csv?csvType=full&useColumnShortNames=true",
        os.path.join(RAW, fname))

# ---------------------------------------------------------------- Wittgenstein Centre + lookups
print("[5/5] Wittgenstein Centre v3.3 (SSP2), ISO/M49 map, WB country metadata ...")
WCDE = "https://wicshiny2023.iiasa.ac.at/wcde-data/wcde-v3-batch/2/"
for ind in ["bprop", "bmys"]:
    get(WCDE + ind + ".rds", os.path.join(RAW, f"wcde_{ind}.rds"))
get("https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv",
    os.path.join(RAW, "iso_m49.csv"))
get("https://api.worldbank.org/v2/country?format=json&per_page=400",
    os.path.join(RAW, "wb_country_meta.json"))

print("\nDone. Files in", RAW)
for f in sorted(os.listdir(RAW)):
    print(f"  {f:34s} {os.path.getsize(os.path.join(RAW,f))/1024:8.0f} KB")
