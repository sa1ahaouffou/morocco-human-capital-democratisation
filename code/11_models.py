"""
11_models.py -- Replications and extensions on WCDE v3.3 x V-Dem v16.

  T20  Which margin of education predicts democracy? (levels, dynamic, two-way FE; young vs old)
  T21  Barro (1999) re-estimated: primary attainment and the male-female gap
  T22  Discrete-time hazard of democratic transition (annual, 1961-2025) with ruling monarchy
  T23  Morocco's predicted hazard: counterfactuals and a decomposition of the log-odds gap
  T24  Demographic-educational expectation of democracy (in the spirit of Lutz, Crespo Cuaresma
       & Abbasi-Shavazi 2010), projected to 2060 under SSP1/2/3

Reads   data/clean/ext/cohort_panel.csv.gz (10_cohorts.py), data/raw/ext/vdem_v16_subset.csv,
        data/clean/panel.csv, data/clean/transitions.csv
Writes  data/clean/ext/{panel5,hazard_panel,morocco_hazard,expectation_projection}.csv, tables/T20-T24
"""
import os, json, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw"); EXT = os.path.join(RAW, "ext")
CLEAN = os.path.join(HERE, "..", "data", "clean"); OUT = os.path.join(CLEAN, "ext")
TAB = os.path.join(HERE, "..", "tables")
KXF = os.path.join(OUT, "key_numbers_ext.json"); KX = json.load(open(KXF))

def table(name, df, cap, fmt=".3f"):
    df.to_csv(os.path.join(TAB, f"{name}.csv"), index=False)
    open(os.path.join(TAB, f"{name}.md"), "w").write(f"**{cap}**\n\n" + df.to_markdown(index=False, floatfmt=fmt) + "\n")
    open(os.path.join(TAB, f"{name}.tex"), "w").write(
        df.to_latex(index=False, float_format=lambda x: f"{x:{fmt}}", caption=cap, label="tab:" + name, escape=True))
    print(f"  wrote {name}")

def stars(p): return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
def cell(m, v): return f"{m.params[v]:.3f}{stars(m.pvalues[v])} ({m.bse[v]:.3f})" if v in m.params else ""
def clus(formula, d, logit=False):
    f = smf.logit if logit else smf.ols
    d = d.dropna(subset=[c for c in d.columns if c in formula_vars(formula)])
    kw = dict(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.iso3)[0]})
    return (f(formula, d).fit(disp=0, **kw) if logit else f(formula, d).fit(**kw)), d
def formula_vars(f):
    import re
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", f)) - {"C", "np", "log"}

# ============================================================ data
COH = pd.read_csv(os.path.join(OUT, "cohort_panel.csv.gz"))   # not "C": that name is patsy's C()
v = pd.read_csv(os.path.join(EXT, "vdem_v16_subset.csv")).rename(columns={"country_text_id": "iso3"})
v["ruling"] = (v.v2expathhs.round().isin([3, 4]) & (v.v2ex_hosw >= 0.5)).astype(float)
v.loc[v.v2expathhs.isna(), "ruling"] = np.nan
p = pd.read_csv(os.path.join(CLEAN, "panel.csv"), low_memory=False)

def wide(ssp=2):
    """Country x year (5-yearly) education covariates from the cohort panel."""
    d = COH[(COH.ssp == ssp) & (COH.sex == "Both")]
    w = d.pivot_table(index=["iso3", "year"], columns="band",
                      values=["mys", "none", "pri_plus", "losec_plus", "upsec_plus", "post", "pop"])
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    out = pd.DataFrame(index=w.index)
    out["mys"] = w["mys_25+"]; out["none"] = w["none_25+"]; out["pri"] = w["pri_plus_25+"]
    out["losec"] = w["losec_plus_25+"]; out["upsec"] = w["upsec_plus_25+"]; out["post"] = w["post_25+"]
    out["mys_y"] = w["mys_20-39"]; out["mys_o"] = w["mys_40-64"]
    out["none_y"] = w["none_20-39"]; out["none_o"] = w["none_40-64"]
    out["youth"] = w["pop_15-24"] / (w["pop_15-24"] + w["pop_25+"]) * 100       # Urdal (2006) youth bulge
    g = COH[(COH.ssp == ssp) & (COH.band == "25+")].pivot_table(index=["iso3", "year"], columns="sex", values="pri_plus")
    out["ggap"] = (g["Male"] - g["Female"]).reindex(out.index)                  # Barro (1999) gender gap
    return out.reset_index()

W2 = wide(2)
gdp = p[["iso3", "year", "gdppc_mad", "resrents"]].copy()
gdp["lgdp"] = np.log(gdp.gdppc_mad)
gdp = gdp.sort_values(["iso3", "year"])
gdp["lgdp"] = gdp.groupby("iso3").lgdp.ffill(limit=3)                     # Maddison ends 2022

# ============================================================ 5-year panel (democracy at t, covariates at t-5)
V5 = v[v.year.isin(range(1950, 2026, 5))][["iso3", "year", "v2x_polyarchy", "v2x_regime", "ruling"]]
P5 = V5.merge(W2, on=["iso3", "year"], how="inner").merge(gdp[["iso3", "year", "lgdp"]], on=["iso3", "year"], how="left")
P5 = P5.sort_values(["iso3", "year"])
lagc = ["v2x_polyarchy", "mys", "none", "pri", "losec", "upsec", "post", "mys_y", "mys_o", "none_y", "none_o",
        "youth", "ggap", "lgdp", "ruling"]
for c in lagc: P5[f"L_{c}"] = P5.groupby("iso3")[c].shift(1)
P5 = P5[P5.year >= 1965]
P5["dem"] = P5.v2x_polyarchy
EDU = {"mys": "Mean years, 25+", "none": "% no schooling, 25+", "pri": "% ≥ primary, 25+",
       "losec": "% ≥ lower secondary, 25+", "upsec": "% ≥ upper secondary, 25+", "post": "% post-secondary, 25+"}
base = P5.dropna(subset=["dem", "L_v2x_polyarchy", "L_lgdp"] + [f"L_{k}" for k in EDU]).copy()
for k in list(EDU) + ["mys_y", "mys_o"]:
    base[f"z_{k}"] = (base[f"L_{k}"] - base[f"L_{k}"].mean()) / base[f"L_{k}"].std()
base.to_csv(os.path.join(OUT, "panel5.csv"), index=False)
print(f"5-year panel: {len(base)} obs, {base.iso3.nunique()} countries, {base.year.min()}-{base.year.max()}")

SPEC = {"Pooled, year FE": "dem ~ {x} + L_lgdp + C(year)",
        "Dynamic (Barro)": "dem ~ L_v2x_polyarchy + {x} + L_lgdp + C(year)",
        "Two-way FE": "dem ~ {x} + L_lgdp + C(iso3) + C(year)",
        "Two-way FE, dynamic (AJRY)": "dem ~ L_v2x_polyarchy + {x} + L_lgdp + C(iso3) + C(year)"}
rows = []; coefs = []
for k, lab in list(EDU.items()) + [("young_old", "Young (20–39) and old (40–64) jointly")]:
    r = {"Education measure (lagged 5 yrs, standardised)": lab}
    for sname, f in SPEC.items():
        x = "z_mys_y + z_mys_o" if k == "young_old" else f"z_{k}"
        m, d = clus(f.format(x=x), base)
        if k == "young_old":
            r[sname] = f"young {cell(m,'z_mys_y')}; old {cell(m,'z_mys_o')}"
            for vv, who in (("z_mys_y", "young"), ("z_mys_o", "old")):
                coefs.append({"measure": f"mys_{who}", "spec": sname, "b": m.params[vv], "se": m.bse[vv], "n": int(m.nobs)})
        else:
            r[sname] = cell(m, f"z_{k}")
            coefs.append({"measure": k, "spec": sname, "b": m.params[f"z_{k}"], "se": m.bse[f"z_{k}"], "n": int(m.nobs)})
    rows.append(r)
T20 = pd.DataFrame(rows)
pd.DataFrame(coefs).to_csv(os.path.join(OUT, "margin_coefs.csv"), index=False)
table("T20_which_margin", T20,
      f"Table 20. Which margin of education predicts democracy? V-Dem electoral democracy index on the "
      f"5-year-lagged education measure (one SD), log GDP per capita and fixed effects; 5-yearly panel "
      f"{base.year.min()}–{base.year.max()}, {base.iso3.nunique()} countries, N={len(base)}. SEs clustered by country.")
cf = pd.DataFrame(coefs)
KX["margin_coefs"] = cf.to_dict("records")

# ============================================================ T21: Barro (1999) with modern data
bb = P5.dropna(subset=["dem", "L_v2x_polyarchy", "L_lgdp", "L_pri", "L_ggap"]).copy()
bb["L_pri10"] = bb.L_pri / 10; bb["L_ggap10"] = bb.L_ggap / 10
ur = pd.read_csv(os.path.join(EXT, "wdi_extra_long.csv"))
ur = ur[ur.indicator == "SP.URB.TOTL.IN.ZS"].rename(columns={"value": "urban"})[["iso3", "year", "urban"]]
bb = bb.merge(ur.assign(year=ur.year + 5), on=["iso3", "year"], how="left")        # lagged 5 yrs
bb = bb.merge(gdp[["iso3", "year", "resrents"]].assign(year=lambda d: d.year + 5), on=["iso3", "year"], how="left")
f1 = "dem ~ L_v2x_polyarchy + L_lgdp + L_pri10 + L_ggap10 + C(year)"
f2 = "dem ~ L_v2x_polyarchy + L_lgdp + L_pri10 + L_ggap10 + urban + resrents + C(year)"
f3 = "dem ~ L_v2x_polyarchy + L_lgdp + L_pri10 + L_ggap10 + C(iso3) + C(year)"
f4 = "dem ~ L_v2x_polyarchy + L_lgdp + L_pri10 + L_ggap10 + L_ruling + C(year)"
ms = [clus(f, bb)[0] for f in (f1, f2, f3, f4)]
lab = {"L_v2x_polyarchy": "Democracy, t−5", "L_lgdp": "log GDP pc, t−5", "L_pri10": "% ≥ primary, 25+ (per 10 pts), t−5",
       "L_ggap10": "Male − female gap, % ≥ primary (per 10 pts), t−5", "urban": "Urban share, t−5",
       "resrents": "Resource rents % GDP, t−5", "L_ruling": "Ruling monarchy, t−5"}
T21 = pd.DataFrame({"Variable": list(lab.values())})
for j, (m, nm) in enumerate(zip(ms, ["(1) Barro spec.", "(2) + urban, rents", "(3) + country FE", "(4) + ruling monarchy"])):
    T21[nm] = [cell(m, k) for k in lab]
T21.loc[len(T21)] = ["N / countries"] + [f"{int(m.nobs)} / {len(set(bb.dropna(subset=[c for c in formula_vars(f) if c in bb.columns]).iso3))}"
                                         for m, f in zip(ms, (f1, f2, f3, f4))]
T21.loc[len(T21)] = ["R²"] + [f"{m.rsquared:.3f}" for m in ms]
table("T21_barro_replication", T21,
      "Table 21. Barro (1999) re-estimated on WCDE v3.3 and V-Dem v16: dependent variable is the electoral "
      "democracy index at t; 5-yearly panel, year FE, SEs clustered by country")
KX.update(barro_ggap=float(ms[0].params["L_ggap10"]), barro_ggap_p=float(ms[0].pvalues["L_ggap10"]),
          barro_ggap_fe=float(ms[2].params["L_ggap10"]), barro_ggap_fe_p=float(ms[2].pvalues["L_ggap10"]),
          barro_pri=float(ms[0].params["L_pri10"]), barro_pri_p=float(ms[0].pvalues["L_pri10"]),
          barro_ruling=float(ms[3].params["L_ruling"]), barro_ruling_p=float(ms[3].pvalues["L_ruling"]))

# ============================================================ T22: discrete-time hazard, annual 1961-2025
def annual(df, cols):
    out = []
    for i, d in df.groupby("iso3"):
        d = d.set_index("year")[cols].reindex(range(1950, 2026)).interpolate(limit_area="inside")
        d["iso3"] = i; out.append(d.reset_index().rename(columns={"index": "year"}))
    return pd.concat(out, ignore_index=True)
A = annual(W2, ["mys", "none", "upsec", "mys_y", "mys_o", "none_y", "none_o", "youth", "ggap"])
# 2025 is the last WCDE point; nothing after it is used
H = v[(v.year >= 1950)][["iso3", "year", "v2x_regime", "v2x_polyarchy", "ruling", "e_regionpol_6C"]].sort_values(["iso3", "year"])
H["dem"] = (H.v2x_regime >= 2).astype(float); H.loc[H.v2x_regime.isna(), "dem"] = np.nan
grp = H.groupby(["e_regionpol_6C", "year"])
H["regdem"] = (grp.dem.transform("sum") - H.dem) / (grp.dem.transform("count") - 1) * 100   # leave-one-out
g = H.groupby("iso3")
for c in ("v2x_regime", "ruling", "regdem"): H[f"{c}_l"] = g[c].shift(1)
H = H.merge(A.assign(year=A.year + 1), on=["iso3", "year"], how="left")                   # covariates at t-1
H = H.merge(gdp[["iso3", "year", "lgdp", "resrents"]].assign(year=lambda d: d.year + 1), on=["iso3", "year"], how="left")
H = H[(H.year >= 1961) & (H.v2x_regime_l <= 1) & H.v2x_regime.notna()].copy()
H["event"] = (H.v2x_regime >= 2).astype(int)
H["closed"] = (H.v2x_regime_l == 0).astype(int)
# spell duration: consecutive at-risk years (a new spell starts after any democratic interlude)
H = H.sort_values(["iso3", "year"])
H["new"] = (H.groupby("iso3").year.diff() != 1).astype(int)
H["spell"] = H.groupby("iso3").new.cumsum()
H["dur"] = H.groupby(["iso3", "spell"]).cumcount() + 1
H["ldur"] = np.log(H.dur); H["trend"] = (H.year - 2000) / 10
H["gap"] = H.mys_y - H.mys_o
H.to_csv(os.path.join(OUT, "hazard_panel.csv"), index=False)
print(f"hazard panel: {len(H)} at-risk country-years, {H.event.sum()} transitions, {H.iso3.nunique()} countries")

# who is at risk, and who ever transitions
H["type"] = np.select([H.ruling_l == 1, H.closed == 1, H.closed == 0],
                      ["Ruling monarchy", "Closed autocracy, non-monarchical", "Electoral autocracy"], "Unclassified")
T22a = (H.groupby("type").agg(**{"At-risk years": ("event", "size"), "Transitions": ("event", "sum"),
                                 "Countries": ("iso3", "nunique")}).reset_index().rename(columns={"type": "Autocracy type (t−1)"}))
T22a["Transitions per 100 years"] = T22a["Transitions"] / T22a["At-risk years"] * 100
table("T22a_risk_set", T22a.round(2),
      "Table 22a. The risk set, 1961–2025: autocracy-years by type and the democratic transitions that followed", fmt=".2f")
KX.update(risk_set=T22a.to_dict("records"),
          ruling_countries=sorted(H[H.ruling_l == 1].iso3.unique().tolist()))

# A monarch who is the chief executive cannot coexist with an electoral democracy in V-Dem's coding
# (the chief executive must be elected), so ruling-monarchy years never end in a same-year transition:
# the monarch must first cede executive power. The hazard is therefore estimated on non-monarchical
# autocracies, and Morocco's "structural" hazard asks what its income, schooling and regime type
# would predict once that constraint is lifted.
HN = H[H.ruling_l == 0].copy()
HS = {"(1) Income + schooling": "event ~ lgdp + mys + ldur + trend",
      "(2) + regime type, diffusion": "event ~ lgdp + mys + closed + regdem_l + ldur + trend",
      "(3) Young vs old": "event ~ lgdp + mys_y + mys_o + closed + regdem_l + ldur + trend",
      "(4) Level + generational gap": "event ~ lgdp + mys + gap + closed + regdem_l + ldur + trend",
      "(5) Distribution": "event ~ lgdp + none + upsec + closed + regdem_l + ldur + trend",
      "(6) + resource rents": "event ~ lgdp + mys + closed + regdem_l + resrents + ldur + trend"}
HM = {k: clus(f, HN, logit=True) for k, f in HS.items()}
hl = {"lgdp": "log GDP pc", "mys": "Mean years, 25+", "mys_y": "Mean years, 20–39", "mys_o": "Mean years, 40–64",
      "gap": "Generational gap (20–39 minus 40–64, yrs)", "none": "% no schooling, 25+", "upsec": "% ≥ upper secondary, 25+",
      "closed": "Closed autocracy (no multiparty elections)", "regdem_l": "% democracies in region",
      "resrents": "Resource rents % GDP", "ldur": "log spell duration", "trend": "Trend (decades)"}
T22 = pd.DataFrame({"Variable (t−1)": list(hl.values())})
for k, (m, d) in HM.items(): T22[k] = [cell(m, x) for x in hl]
T22.loc[len(T22)] = ["At-risk years / transitions"] + [f"{int(m.nobs)} / {int(d.event.sum())}" for m, d in HM.values()]
T22.loc[len(T22)] = ["Pseudo-R²"] + [f"{m.prsquared:.3f}" for m, d in HM.values()]
table("T22_hazard", T22,
      "Table 22. Discrete-time hazard of democratic transition among non-monarchical autocracies (logit, "
      "log-odds; annual 1961–2025; event = V-Dem RoW ≥ 2 at t). SEs clustered by country.")
m2, d2 = HM["(2) + regime type, diffusion"]; m3, d3 = HM["(3) Young vs old"]; m4, _ = HM["(4) Level + generational gap"]
m5, _ = HM["(5) Distribution"]
OR = lambda m, x, s=1: float(np.exp(m.params[x] * s))
KX.update(haz_n=int(m2.nobs), haz_events=int(d2.event.sum()),
          haz_OR_closed=OR(m2, "closed"), haz_p_closed=float(m2.pvalues["closed"]),
          haz_OR_mys=OR(m2, "mys"), haz_p_mys=float(m2.pvalues["mys"]),
          haz_OR_mys_y=OR(m3, "mys_y"), haz_p_mys_y=float(m3.pvalues["mys_y"]),
          haz_OR_mys_o=OR(m3, "mys_o"), haz_p_mys_o=float(m3.pvalues["mys_o"]),
          haz_OR_gap=OR(m4, "gap"), haz_p_gap=float(m4.pvalues["gap"]),
          haz_OR_none10=OR(m5, "none", 10), haz_p_none=float(m5.pvalues["none"]),
          haz_OR_lgdp=OR(m2, "lgdp"), haz_p_lgdp=float(m2.pvalues["lgdp"]),
          haz_OR_regdem10=OR(m2, "regdem_l", 10), haz_p_regdem=float(m2.pvalues["regdem_l"]))

# robustness of the generational-gap effect (model 4)
HN["decade"] = (HN.year // 10) * 10
RB = {"Baseline (model 4)": ("event ~ lgdp + mys + gap + closed + regdem_l + ldur + trend", HN),
      "Decade fixed effects": ("event ~ lgdp + mys + gap + closed + regdem_l + ldur + C(decade)", HN),
      "Region fixed effects": ("event ~ lgdp + mys + gap + closed + regdem_l + ldur + trend + C(e_regionpol_6C)", HN),
      "Excluding sub-Saharan Africa": ("event ~ lgdp + mys + gap + closed + regdem_l + ldur + trend", HN[HN.e_regionpol_6C != 4]),
      "1990–2025 only": ("event ~ lgdp + mys + gap + closed + regdem_l + ldur + trend", HN[HN.year >= 1990]),
      "Gap measured in % no schooling (40–64 minus 20–39)": ("event ~ lgdp + mys + gapn + closed + regdem_l + ldur + trend",
                                                           HN.assign(gapn=HN.none_o - HN.none_y))}
rows = []
for k, (f, d) in RB.items():
    m, dd = clus(f, d, logit=True)
    x = "gapn" if "gapn" in f else "gap"
    rows.append({"Specification": k, "Gap coefficient (log-odds)": m.params[x], "SE": m.bse[x], "p": m.pvalues[x],
                 "Odds ratio": np.exp(m.params[x]), "At-risk years": int(m.nobs), "Transitions": int(dd.event.sum())})
T22c = pd.DataFrame(rows)
table("T22c_gap_robustness", T22c.round(3),
      "Table 22c. Robustness of the generational-gap effect on the hazard of democratic transition "
      "(non-monarchical autocracies, 1961–2025)", fmt=".3f")
KX["gap_robustness"] = T22c.to_dict("records")

# ============================================================ T23: Morocco's structural hazard
mar = H[H.iso3 == "MAR"].copy()
cw = pd.read_csv(os.path.join(OUT, "transitions_cohorts.csv"))
med_mys = float(cw["mys_25+"].median())
last = mar[mar.year == mar.year.max()].iloc[0]
cfs = [("As observed: closed autocracy", m3, {}),
       ("Electoral rather than closed autocracy", m3, {"closed": 0}),
       ("Electoral autocracy, young schooled like the old (no generational gain)", m3, {"closed": 0, "mys_y": float(last.mys_o)}),
       ("Electoral autocracy, whole population at the median transition's schooling", m2, {"closed": 0, "mys": med_mys})]
rows = []
for lab_, m, ch in cfs:
    d = mar[mar.year == mar.year.max()].copy()
    for kk, vv in ch.items(): d[kk] = vv
    h = float(m.predict(d).iloc[0])
    d10 = pd.concat([d] * 10, ignore_index=True)                 # covariates frozen, duration rising
    d10["dur"] = last.dur + np.arange(1, 11); d10["ldur"] = np.log(d10.dur)
    d10["trend"] = (last.year + np.arange(1, 11) - 2000) / 10
    hh = m.predict(d10).values
    rows.append({"Morocco, if the monarch were not the chief executive": lab_, "Annual hazard (%)": h * 100,
                 "P(transition within 10 years) (%)": (1 - np.prod(1 - hh)) * 100})
ref = d3[d3.year >= 2016]
rows.append({"Morocco, if the monarch were not the chief executive": "Reference: average non-monarchical autocracy, 2016–25",
             "Annual hazard (%)": float(m3.predict(ref).mean() * 100),
             "P(transition within 10 years) (%)": float((1 - (1 - m3.predict(ref).mean()) ** 10) * 100)})
T23 = pd.DataFrame(rows)
mar["h_struct_closed"] = m3.predict(mar)
mar["h_struct_electoral"] = m3.predict(mar.assign(closed=0))
mar.to_csv(os.path.join(OUT, "morocco_hazard.csv"), index=False)
xs = ["lgdp", "mys_y", "mys_o", "closed", "regdem_l", "ldur", "trend"]
dec = pd.DataFrame({"Component": [hl[x] for x in xs],
                    "Morocco": [float(last[x]) for x in xs], "Average 2016–25": [float(ref[x].mean()) for x in xs],
                    "Contribution to log-odds gap": [float(m3.params[x] * (last[x] - ref[x].mean())) for x in xs]})
dec.to_csv(os.path.join(OUT, "hazard_decomposition.csv"), index=False)
table("T23_morocco_hazard", T23.round(2),
      f"Table 23. Morocco's structural hazard of democratic transition in {int(last.year)}: what its income, "
      f"schooling and regime type would predict if the monarch were not the chief executive (models 2–3 of Table 22)", fmt=".2f")
table("T23b_hazard_decomposition", dec.round(3),
      f"Table 23b. Decomposing Morocco's structural hazard: contributions to the log-odds gap between Morocco "
      f"({int(last.year)}) and the average non-monarchical autocracy-year 2016–2025 (model 3)", fmt=".3f")
KX.update(MAR_hazard=T23.to_dict("records"), hazard_decomp=dec.to_dict("records"))
print(T23.round(2).to_string(index=False)); print(dec.round(3).to_string(index=False))

# ============================================================ T24: demographic-educational expectation, to 2060
# Pooled 5-yearly model in the spirit of Lutz et al. (2010): democracy on attainment, the gender gap and
# the youth share (all contemporaneous, so that WCDE projections can be fed in), with year effects.
L = V5.merge(W2, on=["iso3", "year"], how="inner")
L = L[(L.year >= 1970) & (L.year <= 2025)].dropna(subset=["v2x_polyarchy", "losec", "mys", "ggap", "youth"])
L["demb"] = (L.v2x_regime >= 2).astype(int)
FM = {"(1) OLS, index": ("v2x_polyarchy ~ losec + ggap + youth + C(year)", False),
      "(2) OLS, index, mean years": ("v2x_polyarchy ~ mys + ggap + youth + C(year)", False),
      "(3) Logit, P(democracy)": ("demb ~ losec + ggap + youth + C(year)", True)}
MM = {k: clus(f, L, logit=lg)[0] for k, (f, lg) in FM.items()}
vl = {"losec": "% ≥ lower secondary, 25+", "mys": "Mean years, 25+", "ggap": "Male − female gap, % ≥ primary",
      "youth": "Youth share (15–24 / 15+)"}
T24 = pd.DataFrame({"Variable": list(vl.values()) + ["N", "R² / pseudo-R²"]})
for k, m in MM.items():
    T24[k] = [cell(m, x) for x in vl] + [f"{int(m.nobs)}", f"{(m.prsquared if hasattr(m, 'prsquared') else m.rsquared):.3f}"]
table("T24_expectation_model", T24,
      "Table 24. A demographic-educational model of democracy (in the spirit of Lutz, Crespo Cuaresma & "
      "Abbasi-Shavazi 2010): 5-yearly pooled panel 1970–2025 with year effects; SEs clustered by country")
mo, mm, ml = MM["(1) OLS, index"], MM["(2) OLS, index, mean years"], MM["(3) Logit, P(democracy)"]
proj = []
for s in (1, 2, 3):
    Ws = wide(s)
    Ws = Ws[Ws.iso3.isin(["MAR", "JOR", "TUN", "DZA", "EGY"]) & Ws.year.between(1970, 2060)].copy()
    X = Ws.assign(year=Ws.year.clip(upper=2025))       # beyond 2025 hold the global year effect at its 2025 value
    Ws["exp_poly"] = mo.predict(X).values; Ws["exp_poly_mys"] = mm.predict(X).values
    Ws["exp_pdem"] = ml.predict(X).values; Ws["ssp"] = s
    proj.append(Ws[["iso3", "year", "ssp", "losec", "mys", "ggap", "youth", "exp_poly", "exp_poly_mys", "exp_pdem"]])
PJ = pd.concat(proj, ignore_index=True)
act = v[v.iso3.isin(PJ.iso3.unique())][["iso3", "year", "v2x_polyarchy"]]
PJ = PJ.merge(act, on=["iso3", "year"], how="left")
PJ.to_csv(os.path.join(OUT, "expectation_projection.csv"), index=False)
pm = PJ[(PJ.iso3 == "MAR") & (PJ.ssp == 2)].set_index("year")
KX.update(exp_MAR=pm[["exp_poly", "exp_poly_mys", "exp_pdem", "v2x_polyarchy"]].round(4).reset_index().to_dict("records"),
          exp_coefs={k: {x: float(m.params[x]) for x in vl if x in m.params} for k, m in MM.items()},
          exp_pvals={k: {x: float(m.pvalues[x]) for x in vl if x in m.params} for k, m in MM.items()})
print(pm.loc[[1970, 1990, 2010, 2025, 2040, 2060], ["exp_poly", "exp_poly_mys", "exp_pdem", "v2x_polyarchy"]].round(3))

json.dump(KX, open(KXF, "w"), indent=1, default=float)
print("updated key_numbers_ext.json:", len(KX), "entries")
