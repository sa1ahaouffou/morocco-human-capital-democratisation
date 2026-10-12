"""
02_build.py -- Assemble the country-year panel and the democratic-transition event file.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW   = os.path.join(HERE, "..", "data", "raw")
CLEAN = os.path.join(HERE, "..", "data", "clean")
os.makedirs(CLEAN, exist_ok=True)
R = lambda f: pd.read_csv(os.path.join(RAW, f))

# Codes that differ across providers for the same country. Without these the country's
# rows split in two and silently fail to merge.
BL_FIX   = {"ROM": "MDA", "SER": "SRB"}     # Barro-Lee legacy codes: Moldova, Serbia
OWID_FIX = {"OWID_KOS": "XKX"}             # V-Dem/OWID Kosovo -> World Bank Kosovo

# ------------------------------------------------------------------ 1. V-Dem
nn = lambda d: d[d.code.notna()].assign(code=lambda x: x.code.replace(OWID_FIX)).drop_duplicates(["code","year"])
regime  = nn(R("vdem_regime.csv").rename(columns={"regime_row_owid": "regime"}))
electdem= nn(R("vdem_electdem.csv").rename(columns={"electdem_vdem__estimate_best": "electdem"}))
libdem  = nn(R("vdem_libdem.csv").rename(columns={"libdem_vdem__estimate_best": "libdem"}))
extra = {}
for fn, col, new in [("owid_political-corruption-index.csv","corruption_vdem__estimate_best","corrupt"),
                     ("owid_civil-liberties-index-vdem.csv","civ_libs_vdem__estimate_best","civlib"),
                     ("owid_participatory-democracy-index.csv","participdem_vdem__estimate_best","partdem"),
                     ("owid_rule-of-law-index.csv","rule_of_law_vdem__estimate_best","rolaw"),
                     ("owid_freedom-of-expression-index.csv","freeexpr_vdem__estimate_best","freeexpr")]:
    try:
        d = R(fn).rename(columns={col:new}); d = d[d.code.notna()]
        d["code"] = d["code"].replace(OWID_FIX)
        extra[new] = d[["code","year",new]].drop_duplicates(["code","year"])
    except Exception as e:
        print("  skip", fn, e)

vdem = (regime[["code","entity","year","regime"]]
        .merge(electdem[["code","year","electdem"]], on=["code","year"], how="outer")
        .merge(libdem[["code","year","libdem"]],     on=["code","year"], how="outer"))
for new, d in extra.items():
    vdem = vdem.merge(d, on=["code","year"], how="outer")
vdem = vdem[vdem.code.notna()].rename(columns={"code":"iso3","entity":"country"})

# ------------------------------------------------------------------ 2. Maddison GDP pc (2011 int$), full history incl. Taiwan
mad = R("maddison_gdppc.csv").rename(columns={"code":"iso3","gdp_per_capita":"gdppc_mad"})
mad = mad[mad.iso3.notna()][["iso3","year","gdppc_mad"]]

# ------------------------------------------------------------------ 3. Barro-Lee v3 (2021), 25-64, interpolated to annual
def bl(fn, tag):
    d = R(fn).rename(columns={"WBcode":"iso3"})
    d["iso3"] = d["iso3"].replace(BL_FIX)
    d = d[["iso3","country","year","yr_sch","lu","lp","lpc","ls","lsc","lh","lhc",
           "yr_sch_pri","yr_sch_sec","yr_sch_ter"]]
    d.columns = ["iso3","country","year"] + [f"{c}_{tag}" for c in
        ["yr_sch","lu","lp","lpc","ls","lsc","lh","lhc","yr_sch_pri","yr_sch_sec","yr_sch_ter"]]
    return d
bl_mf = bl("BL_v3_MF2564.csv","mf")
bl_f  = bl("BL_v3_F2564.csv","f").drop(columns=["country"])
bl_m  = bl("BL_v3_M2564.csv","m").drop(columns=["country"])
blv3  = bl_mf.merge(bl_f, on=["iso3","year"], how="left").merge(bl_m, on=["iso3","year"], how="left")
blv3["iso3"] = blv3.iso3.replace({"TWN":"TWN"})
# Taiwan carries no WB code in BL -> patch from BLcode/country
tw = R("BL_v3_MF2564.csv")
tw = tw[tw.country=="Taiwan"]
if blv3[blv3.iso3=="TWN"].empty and not tw.empty:
    t = tw[["year","yr_sch","lu","lp","lpc","ls","lsc","lh","lhc","yr_sch_pri","yr_sch_sec","yr_sch_ter"]].copy()
    t.columns = ["year"] + [f"{c}_mf" for c in t.columns[1:]]
    t["iso3"]="TWN"; t["country"]="Taiwan"
    blv3 = pd.concat([blv3, t], ignore_index=True)

# annual interpolation of BL within country
grid = []
num = [c for c in blv3.columns if c not in ("iso3","country","year")]
for iso, g in blv3.groupby("iso3"):
    nm = g["country"].dropna().iloc[0] if g["country"].notna().any() else iso
    g = g.sort_values("year").set_index("year")[num].astype(float)
    full = g.reindex(range(int(g.index.min()), 2016)).interpolate(method="index", limit_area="inside")
    full["iso3"] = iso; full["country"] = nm
    grid.append(full.reset_index().rename(columns={"index":"year"}))
blv3a = pd.concat(grid, ignore_index=True)

# ------------------------------------------------------------------ 4. WDI (wide)
wdi = R("wdi_long.csv")
wdi = wdi[wdi.iso3.notna() & (wdi.iso3.str.len()==3)]
wdiw = wdi.pivot_table(index=["iso3","year"], columns="indicator", values="value").reset_index()
wdiw = wdiw.rename(columns={
    "NY.GDP.PCAP.PP.KD":"gdppc_ppp21", "NY.GDP.PCAP.KD":"gdppc_usd15",
    "SE.ADT.LITR.ZS":"lit_adult", "SE.ADT.1524.LT.ZS":"lit_youth",
    "SE.SEC.ENRR":"enr_sec", "SE.SEC.NENR":"enr_sec_net", "SE.TER.ENRR":"enr_ter",
    "SE.PRM.ENRR":"enr_pri", "HD.HCI.HLOS":"hlo", "HD.HCI.OVRL":"hci",
    "SE.LPV.PRIM":"learnpov", "SE.SEC.CUAT.UP.ZS":"att_upsec", "SE.SEC.CUAT.LO.ZS":"att_losec",
    "SE.PRM.CUAT.ZS":"att_pri", "SE.TER.CUAT.BA.ZS":"att_ba", "SE.SCH.LIFE":"sle",
    "SP.POP.TOTL":"pop", "SL.TLF.CACT.FE.ZS":"flfp", "NY.GDP.TOTL.RT.ZS":"resrents",
    "SI.POV.GINI":"gini"})

# ------------------------------------------------------------------ 5. EdStats BL v2.2 + UNDP MYS + literacy long run
eds = R("edstats_long.csv")
eds = eds[eds.iso3.notna() & (eds.iso3.str.len()==3)]
edsw = eds.pivot_table(index=["iso3","year"], columns="indicator", values="value").reset_index()
edsw = edsw.rename(columns={"BAR.SCHL.15UP":"bl22_yrsch15","BAR.SCHL.25UP":"bl22_yrsch25",
                            "BAR.NOED.15UP.ZS":"bl22_noed15","BAR.SEC.CMPT.15UP.ZS":"bl22_seccmp15",
                            "BAR.SEC.SCHL.15UP":"bl22_secyrs15","BAR.TER.SCHL.15UP":"bl22_teryrs15"})
undp = R("owid_mys_undp.csv").rename(columns={"code":"iso3","mys__sex_total":"mys_undp"})[["iso3","year","mys_undp"]]
undp = undp[undp.iso3.notna()]
litlr = R("owid_literacy.csv").rename(columns={"code":"iso3","literacy_rate":"lit_longrun"})[["iso3","year","lit_longrun"]]
litlr = litlr[litlr.iso3.notna()]


# ------------------------------------------------------------------ 5b. HCI (HLO, LAYS) + PISA/TIMSS
def widen(fn, ren):
    d = R(fn); d = d[d.iso3.notna() & (d.iso3.str.len()==3)]
    w = d.pivot_table(index=["iso3","year"], columns="indicator", values="value").reset_index()
    return w.rename(columns=ren)
hci = widen("hci_long.csv", {"HD.HCI.HLOS":"hlo","HD.HCI.OVRL":"hci","HD.HCI.LAYS":"lays",
                             "HD.HCI.EYRS":"eyrs","HD.HCI.HLOS.FE":"hlo_f","HD.HCI.HLOS.MA":"hlo_m"})
pisa = widen("pisa_long.csv", {"LO.PISA.MAT":"pisa_mat","LO.PISA.REA":"pisa_rea",
                               "LO.PISA.SCI":"pisa_sci","LO.TIMSS.MAT4":"timss_mat4"})

# ------------------------------------------------------------------ 6. merge
panel = (vdem
         .merge(mad,   on=["iso3","year"], how="outer")
         .merge(blv3a.drop(columns=["country"]), on=["iso3","year"], how="outer")
         .merge(wdiw,  on=["iso3","year"], how="outer")
         .merge(edsw,  on=["iso3","year"], how="outer")
         .merge(undp,  on=["iso3","year"], how="outer")
         .merge(litlr, on=["iso3","year"], how="outer")
         .merge(hci,   on=["iso3","year"], how="outer")
         .merge(pisa,  on=["iso3","year"], how="outer"))
# ------------------------------------------------------------------ 6b. country universe
# Keep sovereign states, territories and historical polities; drop every regional or
# income-group aggregate (WB metadata region "NA", plus OWID's own regional codes).
meta = json.load(open(os.path.join(RAW, "wb_country_meta.json")))[1]
WB_AGG = {m["id"] for m in meta if m["region"]["id"] == "NA"}
OWID_AGG = {"OWID_AFR","OWID_ASI","OWID_EUR","OWID_NAM","OWID_OCE","OWID_SAM","OWID_WRL",
            "OWID_EU27","OWID_HIC","OWID_LIC","OWID_LMC","OWID_UMC"}
panel = panel[~panel.iso3.isin(WB_AGG | OWID_AGG) & ~panel.iso3.str.startswith("WB_")].copy()
panel["historical_state"] = panel.iso3.str.startswith("OWID_")   # USSR, GDR, Yugoslavia, ...

# one name per code: V-Dem first, then World Bank, then ISO; never the first row blindly
iso_tab = pd.read_csv(os.path.join(RAW, "iso_m49.csv"))
names = {}
for src in (dict(zip(iso_tab["alpha-3"], iso_tab["name"])),
            {m["id"]: m["name"] for m in meta},
            R("maddison_gdppc.csv").dropna(subset=["code"]).drop_duplicates("code").set_index("code")["entity"].to_dict(),
            vdem.dropna(subset=["country"]).drop_duplicates("iso3").set_index("iso3")["country"].to_dict(),
            {"ANT": "Netherlands Antilles", "XKX": "Kosovo", "OWID_CIS": "Former USSR (Maddison)"}):
    names.update(src)                          # later sources win: V-Dem > WB > ISO
panel["country"] = panel.iso3.map(names).fillna(panel["country"])
panel = panel[(panel.year >= 1900) & (panel.year <= 2026)].sort_values(["iso3","year"])

# best available mean years of schooling: BL v3 (25-64) then UNDP (25+)
panel["mys"] = panel["yr_sch_mf"].combine_first(panel["mys_undp"])
# provenance flags: never ship an imputed or spliced value without saying so
panel["mys_source"] = np.where(panel.yr_sch_mf.notna(), "BarroLee_v3_25-64",
                      np.where(panel.mys_undp.notna(), "UNDP_HDR_25+", ""))
panel["bl_interpolated"] = panel.yr_sch_mf.notna() & (panel.year % 5 != 0)
panel.to_csv(os.path.join(CLEAN,"panel.csv"), index=False)
print("panel:", panel.shape, "| units:", panel.iso3.nunique(),
      "| historical polities:", panel[panel.historical_state].iso3.nunique(),
      "| missing names:", panel.country.isna().sum())

# ------------------------------------------------------------------ 7. Democratic transitions (V-Dem Regimes of the World)
# regime: 0 closed autocracy, 1 electoral autocracy, 2 electoral democracy, 3 liberal democracy
rg = panel[["iso3","country","year","regime"]].dropna(subset=["regime"]).copy()
rg["dem"] = (rg.regime >= 2).astype(int)
ev = []
for iso, g in rg.groupby("iso3"):
    g = g.sort_values("year")
    g["lag"] = g.dem.shift(1)
    for _, r in g[(g.dem==1) & (g.lag==0)].iterrows():
        y = int(r.year)
        fut = g[(g.year>y) & (g.year<=y+10)]
        surv5  = int(fut[fut.year<=y+5].dem.min()==1)  if len(fut[fut.year<=y+5])>=5 else np.nan
        surv10 = int(fut.dem.min()==1)                 if len(fut)>=10 else np.nan
        ev.append({"iso3":iso,"country":r.country,"year":y,"surv5":surv5,"surv10":surv10})
tr = pd.DataFrame(ev)
tr = tr[tr.year>=1900]
# attach conditions in the transition year
cond = panel.set_index(["iso3","year"])
for c in ["gdppc_mad","mys","yr_sch_mf","lu_mf","lit_longrun","lit_adult","enr_sec","gdppc_ppp21","yr_sch_f","yr_sch_m"]:
    tr[c] = [cond[c].get((i,y), np.nan) for i,y in zip(tr.iso3, tr.year)]
tr.to_csv(os.path.join(CLEAN,"transitions.csv"), index=False)
print("transitions:", len(tr), "| since 1960:", (tr.year>=1960).sum(),
      "| w/ gdp&mys since 1960:", tr[(tr.year>=1960)].dropna(subset=["gdppc_mad","mys"]).shape[0])
