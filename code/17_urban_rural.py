"""
17_urban_rural.py -- The second divergence: urban and rural Morocco as two electorates.

The extended analysis split Moroccans by age. This splits them by place, which is the split
that shows up in the returns of every election the country has held this century. Tafra's
digitised results give turnout for 1,538 communes and 75 provinces; the 2014 census gives the
education distribution of the same units, separately for their urban and rural populations.

Reads   data/raw/tafra/*.xlsx
Writes  data/clean/ext/commune_panel.csv.gz, province_elections.csv.gz,
        key_numbers_urbanrural.json, tables/T33-T38
"""
import os, json, re, unicodedata, glob
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from tiers import tier_dir

HERE = os.path.dirname(os.path.abspath(__file__))
TAF = os.path.join(HERE, "..", "data", "raw", "tafra")
OUT = os.path.join(HERE, "..", "data", "clean", "ext")
TAB = os.path.join(HERE, "..", "tables")
os.makedirs(OUT, exist_ok=True)
KU = {}



def table(name, df, cap, fmt=".1f"):
    df.to_csv(os.path.join(tier_dir(TAB, name), f"{name}.csv"), index=False)
    open(os.path.join(tier_dir(TAB, name), f"{name}.md"), "w").write(f"**{cap}**\n\n" + df.to_markdown(index=False, floatfmt=fmt) + "\n")
    open(os.path.join(tier_dir(TAB, name), f"{name}.tex"), "w").write(
        df.to_latex(index=False, float_format=lambda x: f"{x:{fmt}}", caption=cap, label="tab:" + name, escape=True))
    print(f"  wrote {name}")


def xl(f, sheet=None):
    p = glob.glob(os.path.join(TAF, f))[0]
    if sheet is None:
        names = pd.ExcelFile(p).sheet_names
        sheet = "données" if "données" in names else "donnees"
    return pd.read_excel(p, sheet_name=sheet)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


# ============================================================ 1. the census: two populations in one country
CEN = xl("recensement-general-2014.xlsx")   # not C: patsy needs that name for C()
EDU = ["eduNo", "eduPresco", "eduPrimaire", "eduCollege", "eduLycee", "eduSup"]
KEEP = EDU + ["txAnalphabetisme", "txScolarisation", "txChomage", "txActivite", "nMenages",
              "actifsElec", "actifs2Internet", "distanceRoute", "ISF"]

strata = {s: CEN[CEN["sample"] == s].set_index("idCommune") for s in CEN["sample"].unique()}
ens, urb, rur = strata["ensemble"], strata["urbain"], strata["rural"]

# Only the commune as a whole has popLegale. Each stratum does report its active and inactive
# counts, so their sum - the adult population of that stratum - is the weight used throughout;
# households are not reported by sex and so cannot serve.
pop15 = lambda d: (d.nActifs.fillna(0) + d.nInactifs.fillna(0))
hu, hr = pop15(urb), pop15(rur)
com = ens[["region", "prefProv", "commune", "popLegale", "idRegion", "idPrefProv"] + KEEP].copy()
com["pop_urb"], com["pop_rur"] = hu, hr
com["urb_share"] = hu / (hu + hr).replace(0, np.nan)
com["milieu"] = np.where(com.urb_share == 0, "rural", np.where(com.urb_share == 1, "urbain", "mixte"))
for v in EDU + ["txAnalphabetisme", "txScolarisation", "txChomage"]:
    com[v + "_u"], com[v + "_r"] = urb[v], rur[v]
KU["n_communes"] = int(len(com))
KU["n_rural"], KU["n_urban"], KU["n_mixed"] = [int((com.milieu == m).sum()) for m in ("rural", "urbain", "mixte")]

# national urban / rural profile, households as weights
def wmean(df, v, w):
    m = df[v].notna() & df[w].notna() & (df[w] > 0)
    return float(np.average(df.loc[m, v], weights=df.loc[m, w])) if m.any() else np.nan

rows = []
LBL = {"eduNo": "No schooling at all", "eduPrimaire": "Primary", "eduCollege": "Lower secondary",
       "eduLycee": "Upper secondary", "eduSup": "Higher education",
       "txAnalphabetisme": "Illiterate (10+)", "txScolarisation": "Children 7–12 in school",
       "txChomage": "Unemployed"}
for v, lab in LBL.items():
    u_, r_ = 100 * wmean(com, v + "_u", "pop_urb"), 100 * wmean(com, v + "_r", "pop_rur")
    rows.append({"Indicator": lab, "Urban": u_, "Rural": r_, "Gap (pp)": u_ - r_,
                 "Ratio": (r_ / u_ if v != "txScolarisation" else u_ / r_)})
T33 = pd.DataFrame(rows)
table("T33_two_populations", T33,
      "Table 33. Two populations: urban and rural Morocco at the 2014 census "
      "(share of the population at each level, adult population as weights)", ".1f")
KU["edu_none_urb"], KU["edu_none_rur"] = float(T33.loc[0, "Urban"]), float(T33.loc[0, "Rural"])
KU["edu_sup_urb"], KU["edu_sup_rur"] = float(T33.loc[4, "Urban"]), float(T33.loc[4, "Rural"])
KU["illit_urb"], KU["illit_rur"] = float(T33.loc[5, "Urban"]), float(T33.loc[5, "Rural"])

# by sex: the four corners of the Moroccan education structure
corner = []
for s, lab in [("urbain - hommes", "Urban men"), ("urbain - femmes", "Urban women"),
               ("rural - hommes", "Rural men"), ("rural - femmes", "Rural women")]:
    d = strata[s]
    w = pop15(d)
    ok = w > 0
    corner.append({"Population": lab,
                   "No schooling": 100 * np.average(d.loc[ok, "eduNo"].fillna(0), weights=w[ok]),
                   "Higher education": 100 * np.average(d.loc[ok, "eduSup"].fillna(0), weights=w[ok]),
                   "Illiterate": 100 * np.average(d.loc[ok, "txAnalphabetisme"].fillna(0), weights=w[ok])})
T34 = pd.DataFrame(corner)
table("T34_four_corners", T34,
      "Table 34. The four corners of the Moroccan education structure, 2014 census", ".1f")
KU["none_rural_women"] = float(T34.loc[3, "No schooling"])
KU["none_urban_men"] = float(T34.loc[0, "No schooling"])

# ============================================================ 2. communal elections: turnout by milieu
comm = {}
for yr, f in [(2015, "communes-elections-2015-1-0.xlsx"), (2021, "communes-elections-2021-1-0.xlsx")]:
    e = xl(f).set_index("idCommune")
    keep = [c for c in ["txParticipation", "invalide", "pctNuls", "nSieges",
                        "repEduSans", "repEdu1aire", "repEdu2aire", "repEduSup"] if c in e.columns]
    comm[yr] = e[keep].rename(columns={"pctNuls": "invalide"})

P = com.join(comm[2015].add_suffix("_2015")).join(comm[2021].add_suffix("_2021"))
P.to_csv(os.path.join(OUT, "commune_panel.csv.gz"), index=True, compression="gzip")

# ============================================================ 3. legislative elections 2002-2021 by province
# 2002 and 2007 predate the 2009/2015 redistricting, so their constituencies carry the old codes;
# they are matched on the province name instead. The eighteen 2002 units with no modern namesake are
# the arrondissement-prefectures of the big cities, mapped here to the prefecture that absorbed them.
OLD2NEW = {
    "alfidamerssultan": "Casablanca", "ainchockhayhassani": "Casablanca",
    "ainsebaahaymohammadi": "Casablanca", "benmsickmediouana": "Casablanca",
    "casablancaanfa": "Casablanca", "moulayrachidsidiothmane": "Casablanca",
    "sidibernoussizenata": "Casablanca",
    "alismailia": "Meknès", "meknneselmenzah": "Meknès", "meknseselmenzah": "Meknès",
    "feseljadiddardbibagh": "Fès", "fesmedina": "Fès", "zouaghamoulayyacoub": "Fès",
    "marrakechmedina": "Marrakech", "marrakechmenara": "Marrakech", "sidiyoussefbenali": "Marrakech",
    "salealjadida": "Salé", "salemedina": "Salé", "fahsbnimakada": "Tanger - Assilah",
}
prov = ens.groupby("idPrefProv").agg(prefProv=("prefProv", "first"), region=("region", "first"),
                                     pop_tot=("popLegale", "sum"))
pu = pop15(urb).groupby(urb.idPrefProv).sum()
pr = pop15(rur).groupby(rur.idPrefProv).sum()
prov["urb_share"] = pu / (pu + pr)
for v in ["eduNo", "eduSup", "txAnalphabetisme", "txChomage"]:
    num = (ens[v] * ens.popLegale).groupby(ens.idPrefProv).sum()
    prov[v] = num / ens.groupby("idPrefProv").popLegale.sum()
BYNAME = {norm(r.prefProv): i for i, r in prov.iterrows()}

leg = []
for yr in [2002, 2007, 2011, 2016, 2021]:
    d = xl(f"parlement-elections-{yr}-*.xlsx")
    if "typeListe" in d.columns:
        d = d[d.typeListe == "locale"]
    d = d.dropna(subset=["txParticipation"]).copy()
    if yr <= 2007:                                       # pre-redistricting codes: match on the name
        d["pid"] = [BYNAME.get(OLD2NEW.get(norm(n), ""), BYNAME.get(norm(n), np.nan))
                    if isinstance(n, str) else np.nan
                    for n in d.prefProv]
        d["pid"] = [BYNAME.get(norm(OLD2NEW[norm(n)]), BYNAME.get(norm(n), np.nan))
                    if norm(n) in OLD2NEW else BYNAME.get(norm(n), np.nan) for n in d.prefProv]
    else:
        d["pid"] = pd.to_numeric(d.idPrefProv, errors="coerce")
    d = d.dropna(subset=["pid"])
    w = d.nInscrits if d.nInscrits.notna().all() else None
    g = d.groupby("pid").apply(
        lambda x: pd.Series({
            "turnout": np.average(x.txParticipation, weights=x.nInscrits) if x.nInscrits.notna().all()
            else x.txParticipation.mean(),
            "n_circ": len(x)}), include_groups=False)
    g["year"], g["election"] = yr, "Legislative"
    leg.append(g.join(prov, how="inner"))
    print(f"  legislative {yr}: {len(d)} constituencies -> {len(g)} provinces matched")

L = pd.concat(leg).reset_index(names="pid")

# the communal elections, aggregated to the same provinces for one comparable series
for yr in (2015, 2021):
    t = P.dropna(subset=[f"txParticipation_{yr}"])
    g = t.groupby("idPrefProv").apply(
        lambda x: pd.Series({"turnout": np.average(x[f"txParticipation_{yr}"], weights=x.popLegale),
                             "n_circ": len(x)}), include_groups=False)
    g["year"], g["election"] = yr, "Communal"
    L = pd.concat([L, g.join(prov, how="inner").reset_index(names="pid")], ignore_index=True)

L.to_csv(os.path.join(OUT, "province_elections.csv.gz"), index=False, compression="gzip")

# ---- T35: the turnout gap at every election
L["urban_prov"] = L.urb_share > 0.5
rows = []
for (el, yr), g in L.groupby(["election", "year"]):
    u = g[g.urban_prov]; r = g[~g.urban_prov]
    rows.append({"Election": f"{el} {yr}", "Provinces": len(g),
                 "Urban turnout": 100 * np.average(u.turnout, weights=u["pop_tot"]),
                 "Rural turnout": 100 * np.average(r.turnout, weights=r["pop_tot"]),
                 "Gap (pp)": 100 * (np.average(u.turnout, weights=u["pop_tot"]) - np.average(r.turnout, weights=r["pop_tot"])),
                 "corr(turnout, % no schooling)": g[["turnout", "eduNo"]].corr().iloc[0, 1]})
T35 = pd.DataFrame(rows).sort_values(["Election"]).reset_index(drop=True)
table("T35_turnout_every_election", T35,
      "Table 35. Turnout in urban and rural provinces at every national election since 2002 "
      "(provinces classed by whether most adults live in town; turnout weighted by population)", ".1f")
KU["turnout_table"] = T35.to_dict("records")
KU["gap_mean"] = float(T35["Gap (pp)"].mean())
KU["corr_mean"] = float(T35["corr(turnout, % no schooling)"].mean())

# ---- T36: commune-level gradient, the sharpest version of the same fact
rows = []
for yr in (2015, 2021):
    d = P.dropna(subset=[f"txParticipation_{yr}", "eduNo"]).copy()
    d["turnout"] = 100 * d[f"txParticipation_{yr}"]
    d["none"] = 100 * d.eduNo; d["sup"] = 100 * d.eduSup; d["urb"] = 100 * d.urb_share.fillna(0)
    for lab, rhs in [("% with no schooling", "none"), ("% with higher education", "sup"),
                     ("% of adults living in town", "urb")]:
        m = smf.ols(f"turnout ~ {rhs}", data=d).fit(cov_type="HC1")
        mf = smf.ols(f"turnout ~ {rhs} + C(region)", data=d).fit(cov_type="HC1")
        rows.append({"Election": f"Communal {yr}", "Regressor": lab,
                     "Coefficient": m.params[rhs], "SE": m.bse[rhs],
                     "With region FE": mf.params[rhs], "SE (FE)": mf.bse[rhs],
                     "R²": m.rsquared, "N": int(m.nobs)})
T36 = pd.DataFrame(rows)
table("T36_turnout_gradient", T36,
      "Table 36. One point more of a commune's population with no schooling buys this many points "
      "of turnout (OLS across the 1,538 communes, HC1 standard errors)", ".3f")
KU["grad_2021"] = float(T36[(T36.Election == "Communal 2021") & (T36.Regressor == "% with no schooling")].Coefficient.iloc[0])
KU["grad_2015"] = float(T36[(T36.Election == "Communal 2015") & (T36.Regressor == "% with no schooling")].Coefficient.iloc[0])

# ---- T37: deciles of schooling against turnout
d = P.dropna(subset=["txParticipation_2021", "eduNo"]).copy()
d["dec"] = pd.qcut(d.eduNo, 10, labels=False) + 1
g = d.groupby("dec").apply(lambda x: pd.Series({
    "Communes": len(x),
    "Population (m)": x.popLegale.sum() / 1e6,
    "% no schooling": 100 * np.average(x.eduNo, weights=x.popLegale),
    "% urban": 100 * np.average(x.urb_share.fillna(0), weights=x.popLegale),
    "Turnout 2015": 100 * np.average(x.txParticipation_2015, weights=x.popLegale),
    "Turnout 2021": 100 * np.average(x.txParticipation_2021, weights=x.popLegale)}), include_groups=False)
T37 = g.reset_index().rename(columns={"dec": "Decile of communes by % with no schooling"})
table("T37_schooling_deciles", T37,
      "Table 37. Turnout by decile of commune schooling, communal elections 2015 and 2021", ".1f")
KU["dec1_turnout21"], KU["dec10_turnout21"] = float(T37.iloc[0]["Turnout 2021"]), float(T37.iloc[-1]["Turnout 2021"])
KU["dec1_none"], KU["dec10_none"] = float(T37.iloc[0]["% no schooling"]), float(T37.iloc[-1]["% no schooling"])

# ---- T38: who is elected, and for whom people vote
rows = []
for lab, sel in [("Urban communes", P.milieu == "urbain"), ("Mixed", P.milieu == "mixte"),
                 ("Rural communes", P.milieu == "rural")]:
    s = P[sel]
    rows.append({"Communes": lab, "N": int(len(s)),
                 "Councillors with no formal schooling": 100 * wmean(s, "repEduSans_2021", "popLegale"),
                 "Councillors with higher education": 100 * wmean(s, "repEduSup_2021", "popLegale"),
                 "Adults with no schooling": 100 * wmean(s, "eduNo", "popLegale"),
                 "Turnout 2021": 100 * wmean(s, "txParticipation_2021", "popLegale")})
T38 = pd.DataFrame(rows)
table("T38_who_is_elected", T38,
      "Table 38. The schooling of the people elected, 2021 communal elections", ".1f")
KU["councillors_sup_urban"] = float(T38.loc[0, "Councillors with higher education"])
KU["councillors_sup_rural"] = float(T38.loc[2, "Councillors with higher education"])

json.dump(KU, open(os.path.join(OUT, "key_numbers_urbanrural.json"), "w"), indent=1, default=float)
print(f"\n  {len(KU)} key numbers -> data/clean/ext/key_numbers_urbanrural.json")
print("T33-T38 done")
