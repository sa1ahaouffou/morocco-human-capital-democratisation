"""
12_afrobarometer.py -- Micro evidence: do Morocco's two electorates want different things?
Afrobarometer Round 9 (2021-2023, 39 countries; Morocco fieldwork 2022, N = 1,200).

Outcomes follow Afrobarometer's own coding of the Demand for Democracy index:
  support    Q23: "Democracy is preferable to any other kind of government" (1) vs the two others (0); DK/refused missing
  elections  Q24: choose leaders through regular, open and honest elections (agree / agree strongly = 1)
  reject1    Q22c: disapprove of abolishing elections and parliament so one leader decides (DK = 0, as in the index)
  demand     DemandDemo == 4 (all four commitments)
  voted      Q13: voted in the last national election (1) vs did not (0); too young / cannot remember missing
  protest    Q10c: attended a demonstration or protest march in the past year
Items worded around a "president" (Q27-Q29, Q37a) are not used: Morocco has no president, and the
English codebook does not say how the item was adapted.

Writes  data/clean/ext/afro_*.csv, tables/T29-T31
"""
import os, json, warnings
import numpy as np, pandas as pd, pyreadstat
import statsmodels.formula.api as smf
from tiers import tier_dir
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "..", "data", "raw", "ext")
OUT = os.path.join(HERE, "..", "data", "clean", "ext"); TAB = os.path.join(HERE, "..", "tables")
KXF = os.path.join(OUT, "key_numbers_ext.json"); KX = json.load(open(KXF))


def table(name, df, cap, fmt=".3f"):
    df.to_csv(os.path.join(tier_dir(TAB, name), f"{name}.csv"), index=False)
    open(os.path.join(tier_dir(TAB, name), f"{name}.md"), "w").write(f"**{cap}**\n\n" + df.to_markdown(index=False, floatfmt=fmt) + "\n")
    open(os.path.join(tier_dir(TAB, name), f"{name}.tex"), "w").write(
        df.to_latex(index=False, float_format=lambda x: f"{x:{fmt}}", caption=cap, label="tab:" + name, escape=True))
    print(f"  wrote {name}")

COLS = ["COUNTRY", "URBRUR", "REGION", "Q1", "Q94", "Q100", "Q93A", "Q10C", "Q13", "Q22A", "Q22B", "Q22C",
        "Q23", "Q24", "Q30", "Q31", "DemandDemo", "LivedPoverty", "withinwt_hh"]
df, meta = pyreadstat.read_sav(os.path.join(EXT, "afrobarometer_r9_merged.sav"), usecols=COLS, apply_value_formats=False)
CN = meta.variable_value_labels["COUNTRY"]
ISO = {"Angola": "AGO", "Benin": "BEN", "Botswana": "BWA", "Burkina Faso": "BFA", "Cabo Verde": "CPV", "Cameroon": "CMR",
       "Congo-Brazzaville": "COG", "Côte d'Ivoire": "CIV", "Eswatini": "SWZ", "Ethiopia": "ETH", "Gabon": "GAB",
       "Gambia": "GMB", "Ghana": "GHA", "Guinea": "GIN", "Kenya": "KEN", "Lesotho": "LSO", "Liberia": "LBR",
       "Madagascar": "MDG", "Malawi": "MWI", "Mali": "MLI", "Mauritania": "MRT", "Mauritius": "MUS", "Morocco": "MAR",
       "Mozambique": "MOZ", "Namibia": "NAM", "Niger": "NER", "Nigeria": "NGA", "São Tomé and Príncipe": "STP",
       "Senegal": "SEN", "Seychelles": "SYC", "Sierra Leone": "SLE", "South Africa": "ZAF", "Sudan": "SDN",
       "Tanzania": "TZA", "Togo": "TGO", "Tunisia": "TUN", "Uganda": "UGA", "Zambia": "ZMB", "Zimbabwe": "ZWE"}
df["country"] = df.COUNTRY.map(CN); df["iso3"] = df.country.map(ISO)
assert df.iso3.notna().all(), df[df.iso3.isna()].country.unique()

# ---- recodes ------------------------------------------------------------------------------
df["age"] = df.Q1.where(df.Q1.between(18, 110))
df["agegrp"] = pd.cut(df.age, [17, 39, 64, 120], labels=["18–39", "40–64", "65+"])
df["young"] = (df.age <= 39).astype(float).where(df.age.notna())
df["edu"] = df.Q94.where(df.Q94.between(0, 9))
df["edu01"] = df.edu / 9
df["educ4"] = pd.cut(df.edu, [-1, 1, 3, 5, 9], labels=["None/informal", "Primary", "Secondary", "Post-secondary"])
df["female"] = (df.Q100 == 2).astype(float).where(df.Q100.isin([1, 2]))
df["urban"] = (df.URBRUR == 1).astype(float)
df["unemployed"] = (df.Q93A == 1).astype(float).where(df.Q93A.between(0, 3))
df["support"] = df.Q23.map({1: 0, 2: 0, 3: 1})
df["elections"] = df.Q24.map({1: 1, 2: 1, 3: 0, 4: 0, 5: 0})
df["reject1"] = df.Q22C.map({1: 1, 2: 1, 3: 0, 4: 0, 5: 0, 9: 0})
df["demand"] = (df.DemandDemo == 4).astype(float).where(df.DemandDemo.notna())
df["voted"] = df.Q13.map({0: 0, 3: 1})
df["protest"] = df.Q10C.map({0: 0, 1: 0, 2: 1, 3: 1, 4: 1})
df["w"] = df.withinwt_hh
OUTC = {"support": "Democracy always preferable", "elections": "Leaders by open elections",
        "reject1": "Rejects one-man rule", "demand": "Full demand for democracy",
        "voted": "Voted in last election", "protest": "Protested in past year"}
df.to_csv(os.path.join(OUT, "afro_r9_recoded.csv.gz"), index=False, compression="gzip")

def wmean(d, y):
    d = d.dropna(subset=[y, "w"]); return float(np.average(d[y], weights=d.w)) if len(d) else np.nan

# ============================================================ T29: Morocco, by generation and schooling
m = df[df.iso3 == "MAR"].copy()
m["gen"] = np.where(m.age <= 39, "18–39", "40+")
cells = []
for gen in ["18–39", "40+"]:
    for ed in ["None/informal", "Primary", "Secondary", "Post-secondary"]:
        d = m[(m.gen == gen) & (m.educ4 == ed)]
        r = {"Generation": gen, "Schooling": ed, "N": len(d), "Weighted share of adults (%)": d.w.sum() / m.w.sum() * 100}
        for y in OUTC: r[OUTC[y]] = wmean(d, y) * 100
        cells.append(r)
T29 = pd.DataFrame(cells)
tot = {"Generation": "All", "Schooling": "All", "N": len(m), "Weighted share of adults (%)": 100.0}
for y in OUTC: tot[OUTC[y]] = wmean(m, y) * 100
T29 = pd.concat([T29, pd.DataFrame([tot])], ignore_index=True)
T29.to_csv(os.path.join(OUT, "afro_morocco_cells.csv"), index=False)
table("T29_morocco_two_electorates", T29.round(1),
      "Table 29. Morocco's two electorates in the survey data: democratic attitudes and participation by "
      "generation and schooling, % (Afrobarometer R9, 2022; weighted; N = 1,200)", fmt=".1f")

# regression: which of age and schooling carries the gradient?
rhs = "C(educ4, Treatment('None/informal')) + C(agegrp) + female + urban + unemployed + LivedPoverty + C(REGION)"
REG = {}
for y in OUTC:
    d = m.dropna(subset=[y, "educ4", "agegrp", "female", "unemployed", "LivedPoverty"])
    REG[y] = smf.wls(f"{y} ~ {rhs}", d, weights=d.w).fit(cov_type="HC1")
lab = {"C(educ4, Treatment('None/informal'))[T.Primary]": "Primary (vs none/informal)",
       "C(educ4, Treatment('None/informal'))[T.Secondary]": "Secondary",
       "C(educ4, Treatment('None/informal'))[T.Post-secondary]": "Post-secondary",
       "C(agegrp)[T.40–64]": "Aged 40–64 (vs 18–39)", "C(agegrp)[T.65+]": "Aged 65+",
       "female": "Woman", "urban": "Urban", "unemployed": "Unemployed, looking", "LivedPoverty": "Lived poverty index"}
def cell(mm, k): return f"{mm.params[k]:.3f}{'***' if mm.pvalues[k]<.01 else '**' if mm.pvalues[k]<.05 else '*' if mm.pvalues[k]<.1 else ''} ({mm.bse[k]:.3f})" if k in mm.params else ""
T30 = pd.DataFrame({"Variable": list(lab.values())})
for y, mm in REG.items(): T30[OUTC[y]] = [cell(mm, k) for k in lab]
T30.loc[len(T30)] = ["N"] + [str(int(mm.nobs)) for mm in REG.values()]
table("T30_morocco_regressions", T30,
      "Table 30. Morocco: schooling and age as predictors of democratic attitudes and participation "
      "(weighted linear probability models, region fixed effects, HC1 SEs; Afrobarometer R9, 2022)")
KX["afro_MAR"] = {y: {"mean": wmean(m, y), **{lab[k]: [float(mm.params.get(k, np.nan)), float(mm.pvalues.get(k, np.nan))]
                                            for k in lab}} for y, mm in REG.items()}
KX["afro_MAR_cells"] = T29.round(2).to_dict("records")

# ============================================================ T31: Morocco among 39 countries
v = pd.read_csv(os.path.join(EXT, "vdem_v16_subset.csv")).rename(columns={"country_text_id": "iso3"})
poly = v[v.year == 2022].set_index("iso3").v2x_polyarchy
rows = []
for iso, d in df.groupby("iso3"):
    r = {"iso3": iso, "country": d.country.iloc[0], "polyarchy_2022": poly.get(iso, np.nan)}
    for y in ("support", "demand", "voted", "protest"):
        dd = d.dropna(subset=[y, "edu01", "young", "female"])
        if dd[y].nunique() < 2: continue
        f = smf.wls(f"{y} ~ edu01 + young + female + urban", dd, weights=dd.w).fit(cov_type="HC1")
        r[f"{y}_mean"] = wmean(d, y); r[f"{y}_edu"] = f.params["edu01"]; r[f"{y}_edu_se"] = f.bse["edu01"]
        r[f"{y}_young"] = f.params["young"]; r[f"{y}_young_se"] = f.bse["young"]
    rows.append(r)
CC = pd.DataFrame(rows)
CC.to_csv(os.path.join(OUT, "afro_country_gradients.csv"), index=False)
for y in ("support", "demand", "voted", "protest"):
    CC[f"{y}_edu_rank"] = CC[f"{y}_edu"].rank(ascending=False).astype(int)
mar = CC[CC.iso3 == "MAR"].iloc[0]
# pooled: is the education gradient weaker in less democratic countries? (Osterman & Robinson 2023)
P = df.merge(poly.rename("poly").reset_index(), on="iso3", how="left")
pooled = {}
for y in ("support", "demand", "voted", "protest"):
    d = P.dropna(subset=[y, "edu01", "young", "female", "poly"])
    pooled[y] = smf.wls(f"{y} ~ edu01 * poly + young + female + urban + C(iso3)", d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d.iso3)[0]})
T31 = pd.DataFrame({"Quantity": ["Morocco mean (%)", "39-country mean (%)",
                                 "Morocco: education gradient (none → postgraduate, pp)", "Rank of Morocco's gradient (of 39)",
                                 "39-country median gradient (pp)", "Morocco: 18–39 minus 40+ (pp)",
                                 "Pooled: education × V-Dem polyarchy (pp per 0.1)"]})
for y in ("support", "demand", "voted", "protest"):
    pm = pooled[y]
    T31[OUTC[y]] = [mar[f"{y}_mean"] * 100, np.average(CC[f"{y}_mean"]) * 100, mar[f"{y}_edu"] * 100,
                    float(mar[f"{y}_edu_rank"]), CC[f"{y}_edu"].median() * 100, mar[f"{y}_young"] * 100,
                    pm.params["edu01:poly"] * 100 * 0.1]
    KX[f"afro_pooled_{y}_int"] = float(pm.params["edu01:poly"]); KX[f"afro_pooled_{y}_int_p"] = float(pm.pvalues["edu01:poly"])
table("T31_afro_comparative", T31.round(1),
      "Table 31. Morocco among the 39 Afrobarometer R9 countries: levels, education gradients and the "
      "generational difference (weighted LPMs with age, sex and urban controls)", fmt=".1f")
KX["afro_MAR_rank"] = {y: int(mar[f"{y}_edu_rank"]) for y in ("support", "demand", "voted", "protest")}
KX["afro_MAR_grad"] = {y: float(mar[f"{y}_edu"]) for y in ("support", "demand", "voted", "protest")}
KX["afro_MAR_young"] = {y: float(mar[f"{y}_young"]) for y in ("support", "demand", "voted", "protest")}

# ---- regional means (small samples: descriptive only) ---------------------------------------
RL = meta.variable_value_labels["REGION"]
rg = m.assign(region=m.REGION.map(RL)).groupby("region").apply(
    lambda d: pd.Series({"N": len(d), "support": wmean(d, "support") * 100, "demand": wmean(d, "demand") * 100,
                         "voted": wmean(d, "voted") * 100, "post_sec": (d.educ4 == "Post-secondary").mean() * 100,
                         "none": (d.educ4 == "None/informal").mean() * 100}))
rg.reset_index().to_csv(os.path.join(OUT, "afro_morocco_regions.csv"), index=False)

# ============================================================ T32: post-stratification and projection
# The Morocco sample over-represents graduates. Re-weight it to the WCDE v3.3 population by
# generation x schooling x sex (adults 20+, 2022 interpolated between 2020 and 2025), then hold the
# within-cell attitudes of 2022 fixed and apply the projected composition of the adult population
# (education x sex; the age gradient in attitudes is nil in Table 30) under SSP1-3.
E = pd.read_csv(os.path.join(OUT, "wcde_epop_5yr.csv.gz"))
E = E[(E.iso3 == "MAR") & (E.sex != "Both") & (E.a0 >= 20)].copy()
E["None/informal"] = E["none"]; E["Primary"] = E.incpri + E.pri
E["Secondary"] = E.losec + E.upsec; E["Post-secondary"] = E.post
E["gen"] = np.where(E.a0 <= 35, "18–39", "40+")
ED = ["None/informal", "Primary", "Secondary", "Post-secondary"]
tg = E.melt(id_vars=["ssp", "year", "sex", "gen"], value_vars=ED, var_name="educ4", value_name="pop") \
      .groupby(["ssp", "year", "sex", "gen", "educ4"])["pop"].sum().reset_index()
def target(ssp, yr, by):
    if yr in tg.year.values:
        d = tg[(tg.ssp == ssp) & (tg.year == yr)]
    else:                                                   # linear interpolation between 5-year points
        y0, y1 = (yr // 5) * 5, (yr // 5) * 5 + 5
        a = tg[(tg.ssp == ssp) & (tg.year == y0)].set_index(["sex", "gen", "educ4"])["pop"]
        b = tg[(tg.ssp == ssp) & (tg.year == y1)].set_index(["sex", "gen", "educ4"])["pop"]
        d = (a + (b - a) * (yr - y0) / 5).rename("pop").reset_index()
    g = d.groupby(by)["pop"].sum(); return g / g.sum()
m["sexl"] = m.female.map({1.0: "Female", 0.0: "Male"})
ms = m.dropna(subset=["educ4", "sexl"]).copy(); ms = ms[ms.age.notna()]
ms["educ4"] = ms.educ4.astype(str)
t22 = target(2, 2022, ["sex", "gen", "educ4"])
cellw = ms.groupby(["sexl", "gen", "educ4"]).w.sum() / ms.w.sum()
ms["w_ps"] = [ms_w * t22.get((sx, g_, e_), np.nan) / cellw.get((sx, g_, e_), np.nan)
              for ms_w, sx, g_, e_ in zip(ms.w, ms.sexl, ms.gen, ms.educ4)]
def wm(d, y, wcol):
    d = d.dropna(subset=[y, wcol]); return float(np.average(d[y], weights=d[wcol])) * 100
rows = []
for y in ("support", "reject1", "demand", "voted", "protest"):
    r = {"Outcome": OUTC[y], "Survey-weighted 2022": wm(ms, y, "w"), "Post-stratified 2022": wm(ms, y, "w_ps")}
    # cell attitudes by education x sex, post-stratified
    att = ms.dropna(subset=[y]).groupby(["sexl", "educ4"]).apply(lambda d: np.average(d[y], weights=d.w_ps))
    for s_ in (1, 2, 3):
        for yr in (2040, 2060):
            comp = target(s_, yr, ["sex", "educ4"])
            r[f"SSP{s_} {yr}"] = float(sum(comp.get((sx, e_), 0) * att.get((sx, e_), np.nan) for sx, e_ in att.index)) * 100
    rows.append(r)
T32 = pd.DataFrame(rows)[["Outcome", "Survey-weighted 2022", "Post-stratified 2022", "SSP2 2040", "SSP2 2060",
                          "SSP1 2060", "SSP3 2060"]]
table("T32_poststratified_projection", T32.round(1),
      "Table 32. Morocco's democratic demand re-weighted to the true population structure (WCDE v3.3, "
      "adults 20+) and projected by demographic metabolism, holding 2022 attitudes within education × sex "
      "cells fixed, %", fmt=".1f")
comp22 = target(2, 2022, ["educ4"]); samp = ms.groupby("educ4").w.sum() / ms.w.sum()
KX.update(afro_ps=T32.round(2).to_dict("records"),
          afro_sample_post=float(samp.get("Post-secondary") * 100), afro_pop_post=float(comp22.get("Post-secondary") * 100),
          afro_sample_none=float(samp.get("None/informal") * 100), afro_pop_none=float(comp22.get("None/informal") * 100),
          afro_turnout_rank=int(CC.voted_mean.rank().loc[CC.iso3 == "MAR"].iloc[0]))
print(T32.round(1).to_string(index=False))

json.dump(KX, open(KXF, "w"), indent=1, default=float)
print(T29.round(1).to_string(index=False)); print(T31.round(1).to_string(index=False))
