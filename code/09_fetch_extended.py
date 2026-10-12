"""
09_fetch_extended.py -- Extra raw data for the extended (cohort / disaggregated) analysis.
Writes only into data/raw/ext/, so the original pipeline (01-08) is untouched.

  * Wittgenstein Centre v3.3: population by 5-year age x sex x education (epop), plus the
    broad-age proportion and mean-years files, for SSP1 / SSP2 / SSP3
  * V-Dem v16 full dataset (component indices, regime-legitimation indices, mobilisation)
  * Afrobarometer Round 9 merged file (39 countries, incl. Morocco 2022)
  * World Bank WDI: labour-market and structural controls not pulled by 01_fetch.py
"""
import os, time, json, ssl, zipfile, certifi, urllib.request
import pandas as pd

SSLCTX = ssl.create_default_context(cafile=certifi.where())
HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.abspath(os.path.join(HERE, "..", "data", "raw", "ext"))
os.makedirs(EXT, exist_ok=True)

def get(url, dest, tries=6, wait=20):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  cached  {os.path.basename(dest)}"); return dest
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
            with urllib.request.urlopen(req, timeout=600, context=SSLCTX) as r:
                blob = r.read()
            if blob[:200].lstrip().startswith((b"<!DOCTYPE", b"<html")):
                raise RuntimeError("HTML page instead of data")
            tmp = dest + ".part"
            open(tmp, "wb").write(blob); os.replace(tmp, dest)
            print(f"  fetched {os.path.basename(dest)}  ({len(blob)/1e6:.1f} MB)"); return dest
        except Exception as e:
            print(f"  retry {k+1}/{tries} {os.path.basename(dest)}: {e}"); time.sleep(wait*(k+1))
    raise RuntimeError(f"could not fetch {url}")

# ---------------------------------------------------------------- Wittgenstein Centre v3.3
print("[1/4] Wittgenstein Centre v3.3, SSP1-3 ...")
WC = "https://wicshiny2023.iiasa.ac.at/wcde-data/wcde-v3-batch/{s}/{f}.rds"
for s in ("1", "2", "3"):
    for f in ("epop", "bprop", "bmys"):
        get(WC.format(s=s, f=f), os.path.join(EXT, f"wcde_ssp{s}_{f}.rds")); time.sleep(3)

# ---------------------------------------------------------------- V-Dem v16 (full)
print("[2/4] V-Dem v16 full dataset ...")
vz = get("https://v-dem.net/media/datasets/V-Dem-CY-FullOthers-v16_csv.zip",
         os.path.join(EXT, "vdem_v16_full.zip"))
VVARS = ["country_name","country_text_id","year",
         # headline indices
         "v2x_polyarchy","v2x_libdem","v2x_regime","v2x_regime_amb",
         # the five Polyarchy components
         "v2x_elecoff","v2x_suffr","v2xel_frefair","v2x_frassoc_thick","v2x_freexp_altinf",
         # liberal and other components
         "v2x_jucon","v2xlg_legcon","v2x_rule","v2x_cspart","v2xcl_rol","v2x_civlib",
         "v2x_partipdem","v2x_delibdem","v2x_egaldem","v2xca_academ","v2x_gender","v2x_corr",
         # how the chief executive is legitimised
         "v2x_ex_hereditary","v2x_ex_military","v2x_ex_party","v2x_ex_confidence","v2x_ex_direlect",
         # mobilisation and repression
         "v2cademmob","v2caautmob","v2cagenmob","v2csreprss","v2mecenefm",
         # Regimes-of-the-World thresholds and aggregation inputs
         "v2elmulpar_osp","v2elfrfair_osp","v2x_liberal","v2x_api","v2x_mpi","v2x_elecreg",
         "v2ex_hosw","v2exhoshog","v2expathhs",
         # sanity / controls in the V-Dem "other" block
         "e_regiongeo","e_regionpol_6C"]
vcsv = os.path.join(EXT, "vdem_v16_subset.csv")
if not os.path.exists(vcsv):
    with zipfile.ZipFile(vz) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(name) as fh:
            hdr = pd.read_csv(fh, nrows=0).columns
        keep = [c for c in VVARS if c in hdr]
        miss = [c for c in VVARS if c not in hdr]
        with z.open(name) as fh:
            pd.read_csv(fh, usecols=keep, low_memory=False).to_csv(vcsv, index=False)
    print(f"  wrote   vdem_v16_subset.csv ({len(keep)} vars; not in file: {miss})")

# ---------------------------------------------------------------- Afrobarometer R9
print("[3/4] Afrobarometer Round 9 merged file ...")
get("https://www.afrobarometer.org/wp-content/uploads/2025/06/"
    "R9.Merge_39ctry.20Nov23.final_.release_Updated.4Jun25-3.sav",
    os.path.join(EXT, "afrobarometer_r9_merged.sav"))
get("https://www.afrobarometer.org/wp-content/uploads/2024/06/MOR_R9.Codebook_10Jun24.final_.pdf",
    os.path.join(EXT, "afrobarometer_r9_morocco_codebook.pdf"))

# ---------------------------------------------------------------- WDI extras
print("[4/4] World Bank WDI extras ...")
WDI_X = {
    "SL.UEM.1524.ZS":   "Youth unemployment, 15-24 (ILO modelled)",
    "SL.UEM.ADVN.ZS":   "Unemployment, advanced education (% of labour force with advanced ed.)",
    "SL.UEM.INTM.ZS":   "Unemployment, intermediate education",
    "SL.UEM.BASC.ZS":   "Unemployment, basic education",
    "SL.UEM.NEET.ZS":   "Youth not in education, employment or training (%)",
    "SP.URB.TOTL.IN.ZS":"Urban population (%)",
    "SP.POP.1564.TO.ZS":"Population 15-64 (% total)",
}
dest = os.path.join(EXT, "wdi_extra_long.csv")
if not os.path.exists(dest):
    rows = []
    for code in WDI_X:
        page = 1
        while True:
            url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
                   f"?format=json&per_page=20000&page={page}&source=2&date=1960:2026")
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}),
                                        timeout=180, context=SSLCTX) as r:
                js = json.loads(r.read().decode())
            if not isinstance(js, list) or len(js) < 2 or js[1] is None: break
            rows += [{"iso3": d["countryiso3code"], "year": int(d["date"]), "indicator": code,
                      "value": d["value"]} for d in js[1] if d.get("value") is not None]
            if page >= js[0]["pages"]: break
            page += 1
        print(f"    {code:22s} {sum(r['indicator']==code for r in rows):7d} obs"); time.sleep(0.3)
    pd.DataFrame(rows).to_csv(dest, index=False)

print("\nDone:", EXT)
for f in sorted(os.listdir(EXT)):
    print(f"  {f:44s} {os.path.getsize(os.path.join(EXT,f))/1e6:8.1f} MB")
