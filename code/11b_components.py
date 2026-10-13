"""
11b_components.py -- The institutional anatomy of Morocco's democracy deficit, and the
schooling-versus-opportunity squeeze (Campante & Chor 2012, 2014) on current data.

  T25  Morocco's five Polyarchy components against transitions, autocracies, monarchies and prediction
  T26  Exact counterfactuals on V-Dem's aggregation formula (the parliamentary-monarchy switch)
  T27  Campante-Chor updated: schooling growth, income growth and pro-democracy mobilisation
  T28  Educated unemployment: Morocco against the world

v2x_polyarchy = .5*MPI + .5*API, with MPI the product of the five components and
API = 1/8 elecoff + 1/4 frefair + 1/4 frassoc + 1/8 suffr + 1/4 freexp (V-Dem codebook v15/v16, 2.1.1).
"""
import os, json, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy.optimize import brentq
from tiers import tier_dir
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw"); EXT = os.path.join(RAW, "ext")
CLEAN = os.path.join(HERE, "..", "data", "clean"); OUT = os.path.join(CLEAN, "ext")
TAB = os.path.join(HERE, "..", "tables")
KXF = os.path.join(OUT, "key_numbers_ext.json"); KX = json.load(open(KXF))


def table(name, df, cap, fmt=".3f"):
    df.to_csv(os.path.join(tier_dir(TAB, name), f"{name}.csv"), index=False)
    open(os.path.join(tier_dir(TAB, name), f"{name}.md"), "w").write(f"**{cap}**\n\n" + df.to_markdown(index=False, floatfmt=fmt) + "\n")
    open(os.path.join(tier_dir(TAB, name), f"{name}.tex"), "w").write(
        df.to_latex(index=False, float_format=lambda x: f"{x:{fmt}}", caption=cap, label="tab:" + name, escape=True))
    print(f"  wrote {name}")

v = pd.read_csv(os.path.join(EXT, "vdem_v16_subset.csv")).rename(columns={"country_text_id": "iso3"})
v["ruling"] = v.v2expathhs.round().isin([3, 4]) & (v.v2ex_hosw >= 0.5)
COMP = {"v2x_elecoff": "Elected officials", "v2x_suffr": "Suffrage", "v2xel_frefair": "Clean elections",
        "v2x_frassoc_thick": "Freedom of association", "v2x_freexp_altinf": "Freedom of expression"}
EXTRA = {"v2x_jucon": "Judicial constraints on the executive", "v2xlg_legcon": "Legislative constraints on the executive",
         "v2x_cspart": "Civil society participation", "v2xcl_rol": "Equality before the law, individual liberty",
         "v2xca_academ": "Academic freedom", "v2x_liberal": "Liberal component"}

def polyarchy(e, s, f, a, x):
    return 0.5 * (e * f * a * s * x) + 0.5 * (e / 8 + f / 4 + a / 4 + s / 8 + x / 4)
def poly_row(r): return polyarchy(r.v2x_elecoff, r.v2x_suffr, r.v2xel_frefair, r.v2x_frassoc_thick, r.v2x_freexp_altinf)

# ============================================================ formula check
y25 = v[v.year == 2025].dropna(subset=list(COMP) + ["v2x_polyarchy"]).copy()
y25["formula"] = y25.apply(poly_row, axis=1)
err = (y25.formula - y25.v2x_polyarchy)
KX.update(formula_r=float(np.corrcoef(y25.formula, y25.v2x_polyarchy)[0, 1]), formula_mae=float(err.abs().mean()),
          formula_maxerr=float(err.abs().max()), formula_n=int(len(y25)))
print(f"formula check 2025: r={KX['formula_r']:.5f}, MAE={KX['formula_mae']:.4f}, max |err|={KX['formula_maxerr']:.4f}, N={len(y25)}")

M = v[(v.iso3 == "MAR") & (v.year == 2025)].iloc[0]
print(f"Morocco 2025: published {M.v2x_polyarchy:.3f}, formula {poly_row(M):.3f}")

# ============================================================ T25: components in comparison
t = pd.read_csv(os.path.join(CLEAN, "transitions.csv"))
tt = t[t.year >= 1960][["iso3", "year"]].merge(v, on=["iso3", "year"], how="left")
tprev = t[t.year >= 1960][["iso3", "year"]].assign(year=lambda d: d.year - 1).merge(v, on=["iso3", "year"], how="left")
ea = y25[y25.v2x_regime == 1]
rm = y25[y25.ruling & (y25.iso3 != "MAR")]
# income + schooling prediction, same predictors as Table 5 (2019-23 averages)
xs = pd.read_csv(os.path.join(CLEAN, "crosssection.csv"))[["iso3", "gdp", "mys"]]
vav = v[v.year.between(2019, 2023)].groupby("iso3")[list(COMP) + list(EXTRA)].mean().reset_index()
cs = xs.merge(vav, on="iso3").dropna()
cs["lgdp"] = np.log(cs.gdp)
pred = {}
for c in list(COMP) + list(EXTRA):
    m = smf.ols(f"{c} ~ lgdp + mys", cs).fit()
    pred[c] = float(m.predict(cs[cs.iso3 == "MAR"]).iloc[0])
def row_of(iso3, yr):
    d = v[(v.iso3 == iso3) & (v.year == yr)]
    return d.iloc[0] if len(d) else None
refs = {"Tunisia 2012": row_of("TUN", 2012), "Spain 1978": row_of("ESP", 1978), "Bhutan 2009": row_of("BTN", 2009),
        "Jordan 2025": row_of("JOR", 2025)}
rows = []
for c, lab in list(COMP.items()) + list(EXTRA.items()):
    r = {"Component": lab, "Morocco 2025": M[c], "Predicted from income & schooling": pred[c],
         "Median, year before transition": tprev[c].median(), "Median, transition year": tt[c].median(),
         "Median, electoral autocracies 2025": ea[c].median(), "Median, other ruling monarchies 2025": rm[c].median()}
    for k, rr in refs.items(): r[k] = rr[c] if rr is not None else np.nan
    rows.append(r)
T25 = pd.DataFrame(rows)
T25.loc[len(T25)] = ["Electoral democracy index", M.v2x_polyarchy, np.nan, tprev.v2x_polyarchy.median(),
                     tt.v2x_polyarchy.median(), ea.v2x_polyarchy.median(), rm.v2x_polyarchy.median()] + \
                    [rr.v2x_polyarchy if rr is not None else np.nan for rr in refs.values()]
table("T25_components", T25.round(3),
      f"Table 25. The anatomy of Morocco's democracy deficit: V-Dem v16 components, 2025, against the "
      f"median democratic transition (N={tt.v2x_elecoff.notna().sum()}), electoral autocracies, the other ruling "
      f"monarchies and the level predicted by income and schooling", fmt=".2f")
KX["components"] = T25.round(4).to_dict("records")

# ============================================================ T26: exact counterfactuals
e, s, f, a, x = (M.v2x_elecoff, M.v2x_suffr, M.v2xel_frefair, M.v2x_frassoc_thick, M.v2x_freexp_altinf)
med = {c: float(tt[c].median()) for c in COMP}
def row_class(pv):
    # RoW: electoral democracy needs polyarchy > .5 plus multiparty and free-and-fair elections > 2
    ok = (M.v2elmulpar_osp > 2) and (M.v2elfrfair_osp > 2)
    return "Electoral democracy" if (pv > 0.5 and ok) else ("Electoral autocracy" if pv > 0 else "—")
need = brentq(lambda d: polyarchy(1, s, min(f + d, 1), min(a + d, 1), min(x + d, 1)) - 0.5, 0, 1)
steps = [("Observed (2025)", polyarchy(e, s, f, a, x), "Closed autocracy (as coded)"),
         ("1. Chief executive accountable to the elected parliament (elected officials = 1)", polyarchy(1, s, f, a, x), None),
         ("2. + clean elections at the median transition", polyarchy(1, s, med["v2xel_frefair"], a, x), None),
         ("3. + association and expression at the median transition", polyarchy(1, s, med["v2xel_frefair"], med["v2x_frassoc_thick"], med["v2x_freexp_altinf"]), None),
         ("Alt. 2. + all three at the income-and-schooling prediction", polyarchy(1, s, pred["v2xel_frefair"], pred["v2x_frassoc_thick"], pred["v2x_freexp_altinf"]), None),
         (f"Alt. 3. + a uniform +{need:.3f} on the three freedoms (just reaches 0.5)", 0.5, None)]
T26 = pd.DataFrame([{"Scenario": k, "Electoral democracy index": pv, "RoW category": rc or row_class(pv + 1e-9 if "reaches" in k else pv)}
                    for k, pv, rc in steps])
table("T26_counterfactuals", T26.round(3),
      "Table 26. Exact counterfactuals on V-Dem's aggregation formula: what a parliamentary monarchy would "
      f"score (Morocco's multiparty {M.v2elmulpar_osp:.2f} and free-and-fair {M.v2elfrfair_osp:.2f} election "
      "indicators already clear RoW's threshold of 2)", fmt=".3f")
KX.update(cf_obs=float(steps[0][1]), cf_elecoff=float(steps[1][1]), cf_plus_frefair=float(steps[2][1]),
          cf_plus_all_median=float(steps[3][1]), cf_plus_pred=float(steps[4][1]), cf_uniform_need=float(need),
          MAR_mulpar=float(M.v2elmulpar_osp), MAR_frfair_osp=float(M.v2elfrfair_osp),
          MAR_comp={c: float(M[c]) for c in COMP}, med_trans_comp=med,
          MAR_pred_poly=float(KX.get("MAR_pred", 0.4248)))
print(T26.round(3).to_string(index=False))

# ============================================================ T27: Campante-Chor updated
p = pd.read_csv(os.path.join(CLEAN, "panel.csv"), low_memory=False)
C = pd.read_csv(os.path.join(OUT, "cohort_panel.csv.gz"))
C = C[(C.ssp == 2) & (C.sex == "Both")]
meta = json.load(open(os.path.join(RAW, "wb_country_meta.json")))[1]
REG = {d["id"]: d["region"]["value"].strip() for d in meta}
def mys_at(yr, band): return C[(C.year == yr) & (C.band == band)].set_index("iso3").mys
g = p[p.year.isin([2000, 2020])].pivot_table(index="iso3", columns="year", values="gdppc_ppp21")
cc = pd.DataFrame({"dmys": mys_at(2020, "25+") - mys_at(2000, "25+"),
                   "dmys_y": mys_at(2020, "20-39") - mys_at(2000, "20-39"),
                   "mys00": mys_at(2000, "25+"),
                   "dlgdp": np.log(g[2020]) - np.log(g[2000]), "lgdp00": np.log(g[2000])}).dropna()
mob = v[v.year.between(2011, 2025)].groupby("iso3").v2cademmob.mean().rename("mob")
aut00 = v[v.year == 2000].set_index("iso3").v2x_regime.le(1).astype(int).rename("aut00")
cc = cc.join(mob).join(aut00)
# the World Bank now files MENA as "Middle East, North Africa, Afghanistan & Pakistan": keep the classic MENA
MENA_LAB = {"Middle East & North Africa", "Middle East, North Africa, Afghanistan & Pakistan"}
is_mena = lambda i: int(REG.get(i, "") in MENA_LAB and i not in ("AFG", "PAK", "MLT"))
cc["region"] = cc.index.map(REG); cc["mena"] = [is_mena(i) for i in cc.index]
fit = smf.ols("dlgdp ~ dmys", cc).fit()
cc["opp_gap"] = -fit.resid                           # >0: income grew less than schooling growth would predict
cc["pct_dmys"] = cc.dmys.rank(pct=True) * 100; cc["pct_dlgdp"] = cc.dlgdp.rank(pct=True) * 100
cc["pct_gap"] = cc.opp_gap.rank(pct=True) * 100
cc.reset_index().rename(columns={"index": "iso3"}).to_csv(os.path.join(OUT, "campante_chor.csv"), index=False)
for c in ("dmys", "dlgdp"): cc[f"{c}_c"] = cc[c] - cc[c].mean()
mm = {"(1) All countries": smf.ols("mob ~ dmys_c * dlgdp_c + mys00 + lgdp00 + aut00", cc).fit(cov_type="HC1"),
      "(2) Autocracies in 2000": smf.ols("mob ~ dmys_c * dlgdp_c + mys00 + lgdp00", cc[cc.aut00 == 1]).fit(cov_type="HC1"),
      "(3) Young cohort, all": smf.ols("mob ~ dmys_y_c * dlgdp_c + mys00 + lgdp00 + aut00",
                                       cc.assign(dmys_y_c=cc.dmys_y - cc.dmys_y.mean())).fit(cov_type="HC1")}
def cell(m, k): return f"{m.params[k]:.3f}{'***' if m.pvalues[k]<.01 else '**' if m.pvalues[k]<.05 else '*' if m.pvalues[k]<.1 else ''} ({m.bse[k]:.3f})" if k in m.params else ""
lab = {"dmys_c": "Δ mean years 25+, 2000–20", "dmys_y_c": "Δ mean years 20–39, 2000–20", "dlgdp_c": "Δ log GDP pc, 2000–20",
       "dmys_c:dlgdp_c": "Δ schooling × Δ income", "dmys_y_c:dlgdp_c": "Δ schooling (young) × Δ income",
       "mys00": "Mean years 2000", "lgdp00": "log GDP pc 2000", "aut00": "Autocracy in 2000"}
T27 = pd.DataFrame({"Variable": list(lab.values())})
for k, m in mm.items(): T27[k] = [cell(m, x) for x in lab]
T27.loc[len(T27)] = ["N"] + [str(int(m.nobs)) for m in mm.values()]
T27.loc[len(T27)] = ["R²"] + [f"{m.rsquared:.3f}" for m in mm.values()]
table("T27_campante_chor", T27,
      "Table 27. Campante & Chor (2012, 2014) on current data: pro-democracy mass mobilisation (V-Dem "
      "v2cademmob, mean 2011–2025) on schooling growth, income growth and their interaction (HC1 SEs)")
mar = cc.loc["MAR"]
KX.update(cc_MAR_dmys=float(mar.dmys), cc_MAR_dlgdp=float(mar.dlgdp), cc_MAR_pct_dmys=float(mar.pct_dmys),
          cc_MAR_pct_dlgdp=float(mar.pct_dlgdp), cc_MAR_pct_gap=float(mar.pct_gap), cc_N=int(len(cc)),
          cc_slope=float(fit.params["dmys"]), cc_MAR_dmys_y=float(mar.dmys_y),
          cc_int=float(mm["(1) All countries"].params["dmys_c:dlgdp_c"]),
          cc_int_p=float(mm["(1) All countries"].pvalues["dmys_c:dlgdp_c"]),
          cc_int_aut=float(mm["(2) Autocracies in 2000"].params["dmys_c:dlgdp_c"]),
          cc_int_aut_p=float(mm["(2) Autocracies in 2000"].pvalues["dmys_c:dlgdp_c"]),
          cc_dmys_aut=float(mm["(2) Autocracies in 2000"].params["dmys_c"]),
          cc_dmys_aut_p=float(mm["(2) Autocracies in 2000"].pvalues["dmys_c"]))
print(f"Morocco: dMYS {mar.dmys:.2f} (pct {mar.pct_dmys:.0f}), dlogGDP {mar.dlgdp:.2f} (pct {mar.pct_dlgdp:.0f}), "
      f"opportunity gap pct {mar.pct_gap:.0f}, N={len(cc)}")

# ============================================================ T28: educated unemployment
w = pd.read_csv(os.path.join(EXT, "wdi_extra_long.csv"))
w = w[w.year >= 2015]
lastv = w.sort_values("year").groupby(["iso3", "indicator"]).tail(1).pivot_table(index="iso3", columns="indicator", values="value")
yrs = w.sort_values("year").groupby(["iso3", "indicator"]).tail(1).pivot_table(index="iso3", columns="indicator", values="year")
u = pd.DataFrame({"adv": lastv.get("SL.UEM.ADVN.ZS"), "int": lastv.get("SL.UEM.INTM.ZS"), "bas": lastv.get("SL.UEM.BASC.ZS"),
                  "youth": lastv.get("SL.UEM.1524.ZS"), "yr": yrs.get("SL.UEM.ADVN.ZS")}).dropna(subset=["adv", "bas"])
u = u[u.index.isin(REG) & (u.index.map(lambda i: REG.get(i, "")) != "Aggregates")]
u["ratio"] = u.adv / u.bas
u["region"] = u.index.map(REG); u["mena"] = [is_mena(i) for i in u.index]
u["pct_ratio"] = u.ratio.rank(pct=True) * 100
u.reset_index().rename(columns={"index": "iso3"}).to_csv(os.path.join(OUT, "educated_unemployment.csv"), index=False)
NAME = p.dropna(subset=["country"]).drop_duplicates("iso3").set_index("iso3")["country"].to_dict()
sel = ["MAR", "TUN", "EGY", "JOR", "DZA", "TUR", "IRN", "SAU", "KOR", "VNM", "IDN", "ESP", "PRT", "BRA", "MEX", "IND"]
T28 = u.loc[[i for i in sel if i in u.index], ["yr", "bas", "int", "adv", "ratio", "pct_ratio", "youth"]].copy()
T28.insert(0, "Country", [NAME.get(i, i) for i in T28.index])
T28 = pd.concat([T28, pd.DataFrame([{"Country": f"World median (N={len(u)})", "yr": np.nan, "bas": u.bas.median(),
                 "int": u["int"].median(), "adv": u.adv.median(), "ratio": u.ratio.median(), "pct_ratio": 50.0,
                 "youth": u.youth.median()}])])
T28.columns = ["Country", "Year", "Unemp., basic ed. %", "Unemp., intermediate %", "Unemp., advanced ed. %",
               "Ratio advanced / basic", "Percentile of ratio", "Youth unemp. 15–24 % (ILO)"]
table("T28_educated_unemployment", T28.reset_index(drop=True).round(2),
      "Table 28. The graduate squeeze: unemployment by level of education (latest year 2015–2025, ILO via WDI)", fmt=".1f")
KX.update(MAR_unemp_adv=float(u.loc["MAR", "adv"]), MAR_unemp_bas=float(u.loc["MAR", "bas"]),
          MAR_unemp_ratio=float(u.loc["MAR", "ratio"]), MAR_unemp_ratio_pct=float(u.loc["MAR", "pct_ratio"]),
          world_unemp_ratio=float(u.ratio.median()), N_unemp=int(len(u)), MAR_unemp_year=int(u.loc["MAR", "yr"]))
print(f"Morocco educated unemployment ratio {u.loc['MAR','ratio']:.2f} (pct {u.loc['MAR','pct_ratio']:.0f}, N={len(u)})")

json.dump(KX, open(KXF, "w"), indent=1, default=float)
print("updated key_numbers_ext.json:", len(KX), "entries")
