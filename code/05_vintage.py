"""
05_vintage.py -- Reconcile Barro-Lee v3 against Wittgenstein Centre v3 (WCDE), UIS, UNDP and
the Moroccan census, and re-run the transition benchmark on the second dataset.
"""
import os, json
import numpy as np, pandas as pd, pyreadr
from tiers import tier_dir

HERE=os.path.dirname(os.path.abspath(__file__))
RAW=os.path.join(HERE,"..","data","raw"); CLEAN=os.path.join(HERE,"..","data","clean")

# ---- WCDE v3, SSP2 (central scenario) ------------------------------------------------
def rds(f):
    return list(pyreadr.read_r(os.path.join(RAW,f)).values())[0]
bprop, bmys = rds("wcde_bprop.rds"), rds("wcde_bmys.rds")

iso = pd.read_csv(os.path.join(RAW,"iso_m49.csv"))
m49 = dict(zip(pd.to_numeric(iso["country-code"], errors="coerce"), iso["alpha-3"]))
m49[158]="TWN"   # Taiwan is absent from ISO-3166 main table

def prep(df, val, agecol):
    d = df[df.sex=="Both"].copy()
    d["iso3"] = pd.to_numeric(d.country_code, errors="coerce").map(m49)
    d = d[d.iso3.notna() & d.age.isin(["25+","20--39","40--64","15+"])]
    d["year"] = d.year.astype(int)
    return d

ne = prep(bprop,"bprop","age")
ne = ne[ne.education=="No Education"].rename(columns={"bprop":"noed"})[["iso3","name","year","age","noed"]]
my = prep(bmys,"bmys","age").rename(columns={"bmys":"mys"})[["iso3","year","age","mys"]]
w  = ne.merge(my, on=["iso3","year","age"], how="outer")
w.to_csv(os.path.join(CLEAN,"wcde.csv"), index=False)
print(f"WCDE panel: {w.shape} | countries {w.iso3.nunique()} | years {w.year.min()}-{w.year.max()}")

W25 = w[w.age=="25+"].set_index(["iso3","year"])
def wval(iso3, yr, col):
    return W25[col].get((iso3, int(round(yr/5)*5)), np.nan)

# ---- 1. Do the two datasets agree? (common year 2015, 25+ vs 25-64) ------------------
p = pd.read_csv(os.path.join(CLEAN,"panel.csv"))
bl15 = p[(p.year==2015)][["iso3","country","lu_mf","yr_sch_mf"]].dropna(subset=["lu_mf"])
wc15 = w[(w.age=="25+")&(w.year==2015)][["iso3","noed","mys"]]
cmp15 = bl15.merge(wc15, on="iso3", how="inner")
r_ne = cmp15[["lu_mf","noed"]].corr().iloc[0,1]; r_my = cmp15[["yr_sch_mf","mys"]].corr().iloc[0,1]
print(f"\n2015 cross-source agreement (N={len(cmp15)}):")
print(f"  % no schooling : r = {r_ne:.3f} | mean abs diff = {(cmp15.lu_mf-cmp15.noed).abs().mean():.1f} pp")
print(f"  mean yrs school: r = {r_my:.3f} | mean abs diff = {(cmp15.yr_sch_mf-cmp15.mys).abs().mean():.2f} yrs")
print(f"  Morocco        : BL {cmp15[cmp15.iso3=='MAR'].lu_mf.iloc[0]:.1f}% vs WCDE {cmp15[cmp15.iso3=='MAR'].noed.iloc[0]:.1f}%")
cmp15.to_csv(os.path.join(CLEAN,"source_compare_2015.csv"), index=False)

# ---- 2. Morocco today, every source --------------------------------------------------
mar = []
mar.append(("Barro-Lee v3",        "25–64", 2015, 5.109, 42.40))
mar.append(("UNESCO UIS",          "25+",   2017, 4.943, np.nan))
mar.append(("UNDP HDR",            "25+",   2023, 6.198, np.nan))
mar.append(("HCP, RGPH census",    "25+",   2024, 6.300, np.nan))
for yr in (2015, 2020, 2025):
    mar.append(("Wittgenstein v3", "25+", yr, wval("MAR",yr,"mys"), wval("MAR",yr,"noed")))
M = pd.DataFrame(mar, columns=["Source","Age group","Year","Mean years","% no schooling"])
print("\nMOROCCO — mean years of schooling & unschooled share, by source:")
print(M.round(2).to_string(index=False))
M.to_csv(os.path.join(CLEAN,"morocco_by_source.csv"), index=False)

# ---- 3. Morocco by cohort (WCDE 2025) ------------------------------------------------
coh = w[(w.iso3=="MAR")&(w.year==2025)][["age","mys","noed"]].set_index("age")
print("\nMOROCCO 2025 by cohort (WCDE v3):"); print(coh.round(2).to_string())

# ---- 4. Re-run the transition benchmark on WCDE --------------------------------------
t = pd.read_csv(os.path.join(CLEAN,"transitions.csv"))
ts = t[t.year>=1960].copy()
ts["w_noed"] = [wval(i,y,"noed") for i,y in zip(ts.iso3, ts.year)]
ts["w_mys"]  = [wval(i,y,"mys")  for i,y in zip(ts.iso3, ts.year)]
out=[]
for lab, col, mval in [
    ("Barro-Lee v3 · % no schooling", "lu_mf", 42.40),
    ("WCDE v3 · % no schooling",      "w_noed", float(coh.loc["25+","noed"])),
    ("Barro-Lee v3 · mean years",     "mys",   6.198),
    ("WCDE v3 · mean years",          "w_mys", float(coh.loc["25+","mys"])),
]:
    s = ts[col].dropna()
    out.append({"Benchmark":lab, "N":len(s), "Median at transition":s.median(),
                "Morocco":mval, "Morocco percentile":(s<mval).mean()*100})
R = pd.DataFrame(out)
print("\nTRANSITION BENCHMARK under each dataset:"); print(R.round(1).to_string(index=False))

# cohort percentiles on the WCDE benchmark
sne = ts["w_noed"].dropna(); smy = ts["w_mys"].dropna()
print("\nMOROCCO COHORTS vs the WCDE transition benchmark:")
for a in ["40--64","25+","20--39"]:
    n_, m_ = coh.loc[a,"noed"], coh.loc[a,"mys"]
    print(f"  {a:8s}  no-schooling {n_:5.1f}% -> pctile {(sne<n_).mean()*100:5.1f} | "
          f"mean yrs {m_:5.2f} -> pctile {(smy<m_).mean()*100:5.1f}")
ts.to_csv(os.path.join(CLEAN,"transitions_wcde.csv"), index=False)
R.to_csv(os.path.join(CLEAN,"benchmark_by_source.csv"), index=False)

# ---- 5. Tables T8–T10 ------------------------------------------------------------
TAB=os.path.join(HERE,"..","tables")

def out(name, df, cap):
    df.to_csv(os.path.join(tier_dir(TAB, name), f"{name}.csv"), index=False)
    open(os.path.join(tier_dir(TAB, name), f"{name}.md"),"w").write(f"**{cap}**\n\n"+df.to_markdown(index=False, floatfmt=".1f")+"\n")
    open(os.path.join(tier_dir(TAB, name), f"{name}.tex"),"w").write(df.to_latex(index=False, float_format=lambda x:"%.1f"%x,
                                                              caption=cap, label="tab:"+name, escape=True))
out("T8_source_contrast", M.round(2), "Table 8. Morocco's schooling stock measured by five independent sources")
out("T9_benchmark_robustness", R.round(1), "Table 9. The transition benchmark re-run on a second dataset (Wittgenstein Centre v3.3)")
rows=[]
for a,lab in [("40--64","Aged 40–64"),("25+","All adults 25+"),("20--39","Aged 20–39"),("15+","All adults 15+")]:
    n_=float(coh.loc[a,"noed"]); m_=float(coh.loc[a,"mys"])
    rows.append({"Moroccan cohort (2025)":lab, "% no schooling":n_, "pctile (no schooling)":(sne<n_).mean()*100,
                 "Mean years of schooling":m_, "pctile (mean years)":(smy<m_).mean()*100})
out("T10_cohorts", pd.DataFrame(rows).round(1),
    "Table 10. Morocco's two electorates: schooling by cohort, benchmarked against 138 democratic transitions")

# every WCDE country code must map to ISO; report any that do not
unm = sorted(set(pd.to_numeric(bprop.country_code, errors="coerce").dropna().astype(int)) - set(m49))
print("\nWCDE M49 codes without an ISO mapping (regions/aggregates expected):", unm[:40])
