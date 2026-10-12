"""
10_cohorts.py -- Cohort, gender and projection analysis on the Wittgenstein Centre v3.3
population by 5-year age x sex x education (SSP1/2/3), plus the V-Dem v16 reference class of
monarchies that became democracies while keeping the monarch.

Reads   data/raw/ext/wcde_ssp{1,2,3}_{epop,bmys,bprop}.rds, data/raw/ext/vdem_v16_subset.csv,
        data/clean/{panel,transitions}.csv
Writes  data/clean/ext/*.csv, data/clean/ext/key_numbers_ext.json, tables/T14-T19
"""
import os, json
import numpy as np, pandas as pd, pyreadr

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw"); EXT = os.path.join(RAW, "ext")
CLEAN = os.path.join(HERE, "..", "data", "clean"); OUT = os.path.join(CLEAN, "ext")
TAB = os.path.join(HERE, "..", "tables")
os.makedirs(OUT, exist_ok=True)
KX = {}                                                   # headline numbers for the write-up

def rds(f): return list(pyreadr.read_r(os.path.join(EXT, f)).values())[0]
iso = pd.read_csv(os.path.join(RAW, "iso_m49.csv"))
M49 = dict(zip(pd.to_numeric(iso["country-code"], errors="coerce"), iso["alpha-3"])); M49[158] = "TWN"
p = pd.read_csv(os.path.join(CLEAN, "panel.csv"), low_memory=False)
NAME = p.dropna(subset=["country"]).drop_duplicates("iso3").set_index("iso3")["country"].to_dict()

def table(name, df, cap, fmt=".1f"):
    df.to_csv(os.path.join(TAB, f"{name}.csv"), index=False)
    open(os.path.join(TAB, f"{name}.md"), "w").write(f"**{cap}**\n\n" + df.to_markdown(index=False, floatfmt=fmt) + "\n")
    open(os.path.join(TAB, f"{name}.tex"), "w").write(
        df.to_latex(index=False, float_format=lambda x: f"{x:{fmt}}", caption=cap, label="tab:" + name, escape=True))
    print(f"  wrote {name}")

# ============================================================ 1. WCDE population by age x sex x education
# "Post Secondary" is already the total of the detailed tertiary categories (Short post-secondary,
# Bachelor, Master+), which WCDE reports only for some countries: using it alone avoids double counting.
LEV = {"No Education": "none", "Incomplete Primary": "incpri", "Primary": "pri",
       "Lower Secondary": "losec", "Upper Secondary": "upsec", "Post Secondary": "post"}
ORDER = ["none", "incpri", "pri", "losec", "upsec", "post"]

def load_epop(s):
    e = rds(f"wcde_ssp{s}_epop.rds")
    e = e[e.education.isin(LEV) & (e.age != "All")].copy()
    e["iso3"] = pd.to_numeric(e.country_code, errors="coerce").map(M49)
    e = e[e.iso3.notna()]
    e["a0"] = e.age.str.split("--").str[0].str.replace("+", "", regex=False).astype(int)
    e = e[e.a0 >= 15]
    e["lev"] = e.education.map(LEV); e["year"] = e.year.astype(int)
    g = (e.groupby(["iso3", "year", "sex", "a0", "lev"])["epop"].sum()
           .unstack("lev").reindex(columns=ORDER).fillna(0.0))
    g["ssp"] = int(s)
    return g.reset_index()

E = pd.concat([load_epop(s) for s in "123"], ignore_index=True)
E.to_csv(os.path.join(OUT, "wcde_epop_5yr.csv.gz"), index=False, compression="gzip")
print(f"WCDE 5-year panel: {E.shape}, {E.iso3.nunique()} countries, {E.year.min()}-{E.year.max()}")

BANDS = {"20-39": (20, 39), "40-64": (40, 64), "65+": (65, 200), "20+": (20, 200),
         "25+": (25, 200), "20-64": (20, 64), "15-24": (15, 24), "30-34": (30, 34)}

def shares(df):
    tot = df[ORDER].sum(axis=1)
    out = pd.DataFrame({"pop": tot})
    out["none"] = df["none"] / tot * 100
    out["below_pri"] = (df["none"] + df["incpri"]) / tot * 100
    out["pri_plus"] = df[["pri", "losec", "upsec", "post"]].sum(axis=1) / tot * 100
    out["losec_plus"] = df[["losec", "upsec", "post"]].sum(axis=1) / tot * 100
    out["upsec_plus"] = df[["upsec", "post"]].sum(axis=1) / tot * 100
    out["post"] = df["post"] / tot * 100
    cum = df[ORDER].cumsum(axis=1).div(tot, axis=0)               # median attainment (0..5)
    out["median_level"] = (cum.values < 0.5).sum(axis=1)
    return out

rows = []
for band, (lo, hi) in BANDS.items():
    b = E[(E.a0 >= lo) & (E.a0 <= hi)].groupby(["ssp", "iso3", "year", "sex"])[ORDER].sum()
    s = shares(b); s["band"] = band; rows.append(s.reset_index())
C = pd.concat(rows, ignore_index=True)

# mean years of schooling by broad band (WCDE's own calculation, which uses national durations)
AG = {"20--39": "20-39", "40--64": "40-64", "25+": "25+", "15+": "15+", "65+": "65+", "20--64": "20-64"}
my = []
for s in "123":
    b = rds(f"wcde_ssp{s}_bmys.rds")
    b = b[b.age.isin(AG)].copy()
    b["iso3"] = pd.to_numeric(b.country_code, errors="coerce").map(M49)
    b = b[b.iso3.notna()]; b["band"] = b.age.map(AG); b["ssp"] = int(s); b["year"] = b.year.astype(int)
    my.append(b[["ssp", "iso3", "year", "sex", "band", "bmys"]].rename(columns={"bmys": "mys"}))
C = C.merge(pd.concat(my), on=["ssp", "iso3", "year", "sex", "band"], how="left")
C.to_csv(os.path.join(OUT, "cohort_panel.csv.gz"), index=False, compression="gzip")
print(f"cohort panel: {C.shape}")

C2 = C[C.ssp == 2]
def val(iso3, yr, band, col, sex="Both", ssp=2):
    d = C[(C.ssp == ssp) & (C.iso3 == iso3) & (C.year == yr) & (C.band == band) & (C.sex == sex)]
    return float(d[col].iloc[0]) if len(d) else np.nan

# ============================================================ 2. The generational gap across the world, 2025
W = (C2[(C2.year == 2025) & (C2.sex == "Both") & C2.band.isin(["20-39", "40-64"])]
       .pivot_table(index="iso3", columns="band", values=["mys", "none", "losec_plus"]))
W.columns = [f"{a}_{b}" for a, b in W.columns]
W = W.dropna(subset=["mys_20-39", "mys_40-64"])
W["gap_mys"] = W["mys_20-39"] - W["mys_40-64"]
W["gap_none"] = W["none_40-64"] - W["none_20-39"]
W["ratio_none"] = W["none_40-64"] / W["none_20-39"].clip(lower=0.5)
W["country"] = W.index.map(lambda i: NAME.get(i, i))
W = W.sort_values("gap_mys", ascending=False)
W["rank_gap_mys"] = np.arange(1, len(W) + 1)
W["rank_gap_none"] = W.gap_none.rank(ascending=False, method="min").astype(int)
W.reset_index().to_csv(os.path.join(OUT, "generational_gap_2025.csv"), index=False)
KX.update(MAR_gap_mys_2025=float(W.loc["MAR", "gap_mys"]), MAR_gap_mys_rank=int(W.loc["MAR", "rank_gap_mys"]),
          MAR_gap_none_2025=float(W.loc["MAR", "gap_none"]), MAR_gap_none_rank=int(W.loc["MAR", "rank_gap_none"]),
          N_gap_countries=int(len(W)), world_median_gap_mys=float(W.gap_mys.median()))
print(f"\nMorocco generational gap 2025: {W.loc['MAR','gap_mys']:.2f} yrs (rank {W.loc['MAR','rank_gap_mys']}/{len(W)}), "
      f"no-schooling gap {W.loc['MAR','gap_none']:.1f} pts (rank {W.loc['MAR','rank_gap_none']}/{len(W)})")

COMP = ["MAR", "DZA", "TUN", "EGY", "JOR", "TUR", "IRN", "SAU", "KOR", "TWN", "VNM", "IDN", "ESP", "PRT", "BTN", "SEN"]
t14 = W.head(12).index.tolist() + [c for c in COMP if c not in W.head(12).index and c in W.index]
T14 = W.loc[t14, ["country", "mys_20-39", "mys_40-64", "gap_mys", "rank_gap_mys", "none_20-39", "none_40-64", "gap_none", "rank_gap_none"]]
T14.columns = ["Country", "MYS 20–39", "MYS 40–64", "Gap (yrs)", "Rank", "% none 20–39", "% none 40–64", "Gap (pts)", "Rank (pts)"]
table("T14_generational_gap", T14.reset_index(drop=True),
      f"Table 14. The generational schooling gap in 2025: the 12 largest of {len(W)} countries, and comparators")

# ============================================================ 3. Birth-cohort expansion curves
# attainment of each birth cohort observed at age 30-34 (completed schooling); cohort = year - 32
B = C2[(C2.band == "30-34") & (C2.year <= 2025)].copy()
B["birth"] = B.year - 32
B.to_csv(os.path.join(OUT, "birth_cohorts.csv"), index=False)

def cross_year(s, thr):
    """First birth year at which series s (index=birth year) reaches thr, linearly interpolated."""
    s = s.dropna().sort_index()
    if s.iloc[0] >= thr: return float("nan")   # already above at the first observed cohort
    for (b0, v0), (b1, v1) in zip(s.items(), list(s.items())[1:]):
        if v0 < thr <= v1: return b0 + (thr - v0) / (v1 - v0) * (b1 - b0)
    return float("nan")

CL = ["MAR", "KOR", "TWN", "JPN", "ESP", "PRT", "TUN", "TUR", "DZA", "EGY", "JOR", "IRN", "IDN", "VNM", "BRA", "BTN"]
rows = []
for c in CL:
    for sex in ("Both", "Female"):
        s = B[(B.iso3 == c) & (B.sex == sex)].set_index("birth")
        rows.append({"iso3": c, "sex": sex,
                     "none<25%": cross_year(-s["none"], -25), "losec+≥50%": cross_year(s["losec_plus"], 50),
                     "upsec+≥50%": cross_year(s["upsec_plus"], 50)})
BC = pd.DataFrame(rows)
BC.to_csv(os.path.join(OUT, "birth_cohort_crossings.csv"), index=False)
mar = BC[(BC.iso3 == "MAR") & (BC.sex == "Both")].iloc[0]
first_b, last_b = int(B.birth.min()), int(B.birth.max())
def lab(iso3, sex, col, thr, below=False):
    """Readable crossing year: '<1918' if already past at the first cohort, 'not yet (x%)' if never."""
    y = BC[(BC.iso3 == iso3) & (BC.sex == sex)][col].iloc[0]
    if not np.isnan(y): return f"{y:.0f}"
    var = {"none<25%": "none", "losec+≥50%": "losec_plus", "upsec+≥50%": "upsec_plus"}[col]
    s = B[(B.iso3 == iso3) & (B.sex == sex)].set_index("birth")[var].sort_index()
    first, last = s.iloc[0], s.iloc[-1]
    done = (first <= thr) if below else (first >= thr)
    return f"<{first_b}" if done else f"not yet ({last:.0f}%)"
T15 = pd.DataFrame({"Country": [NAME.get(c, c) for c in CL]})
T15["No schooling < 25%"] = [lab(c, "Both", "none<25%", 25, below=True) for c in CL]
T15["≥ lower sec. ≥ 50%"] = [lab(c, "Both", "losec+≥50%", 50) for c in CL]
T15["Women: ≥ lower sec. ≥ 50%"] = [lab(c, "Female", "losec+≥50%", 50) for c in CL]
T15["≥ upper sec. ≥ 50%"] = [lab(c, "Both", "upsec+≥50%", 50) for c in CL]
lag = mar["losec+≥50%"] - BC[BC.sex == "Both"].set_index("iso3")["losec+≥50%"]
T15["Lag vs Morocco (yrs)"] = [f"{lag[c]:.0f}" if not np.isnan(lag[c]) else f">{mar['losec+≥50%']-first_b:.0f}" for c in CL]
table("T15_birth_cohort_timing", T15,
      "Table 15. When did each country's schooling revolution happen? First birth cohort to reach each "
      "threshold (attainment observed at age 30–34; cohorts born 1918–1993; WCDE v3.3)")
KX.update(MAR_birth_losec50=float(mar["losec+≥50%"]),
          KOR_birth_losec50=float(BC[(BC.iso3 == "KOR") & (BC.sex == "Both")]["losec+≥50%"].iloc[0]),
          TUN_birth_losec50=float(BC[(BC.iso3 == "TUN") & (BC.sex == "Both")]["losec+≥50%"].iloc[0]),
          MAR_birth_none25=float(mar["none<25%"]))

# ============================================================ 4. Transitions in cohort space
t = pd.read_csv(os.path.join(CLEAN, "transitions.csv"))
ts = t[t.year >= 1960].copy()
ts["y5"] = (ts.year / 5).round().astype(int) * 5          # same rule as 05_vintage.py
T2 = (C2[C2.sex == "Both"].pivot_table(index=["iso3", "year"], columns="band",
                                         values=["mys", "none", "losec_plus", "median_level"]))
T2.columns = [f"{a}_{b}" for a, b in T2.columns]
keep = ([f"{v}_{b}" for v in ("mys", "none", "losec_plus") for b in ("20-39", "40-64", "25+")]
        + ["none_20+", "losec_plus_20+", "median_level_20+"])            # WCDE has no mean years for 20+
ts = ts.merge(T2[keep].reset_index().rename(columns={"year": "y5"}), on=["iso3", "y5"], how="left")
# gender gap in primary attainment (Barro 1999): male minus female share with at least primary, 25+
G = C2[C2.band == "25+"].pivot_table(index=["iso3", "year"], columns="sex", values="pri_plus")
G["gender_gap_pri"] = G["Male"] - G["Female"]
ts = ts.merge(G[["gender_gap_pri"]].reset_index().rename(columns={"year": "y5"}), on=["iso3", "y5"], how="left")
ts["gap_mys"] = ts["mys_20-39"] - ts["mys_40-64"]
ts["gap_none"] = ts["none_40-64"] - ts["none_20-39"]
ts["lgdp"] = np.log(ts.gdppc_mad)
ts.to_csv(os.path.join(OUT, "transitions_cohorts.csv"), index=False)
tc = ts.dropna(subset=["mys_20-39", "mys_40-64"])
print(f"transitions with cohort data: {len(tc)}")

MAR25 = {k: val("MAR", 2025, b, v) for k, (b, v) in {
    "mys_20-39": ("20-39", "mys"), "mys_40-64": ("40-64", "mys"), "none_20-39": ("20-39", "none"),
    "none_40-64": ("40-64", "none"), "losec_plus_20-39": ("20-39", "losec_plus"),
    "losec_plus_40-64": ("40-64", "losec_plus"), "mys_25+": ("25+", "mys"), "none_25+": ("25+", "none"),
    "losec_plus_20+": ("20+", "losec_plus"), "none_20+": ("20+", "none"), "median_level_20+": ("20+", "median_level")}.items()}
MAR25["gap_mys"] = MAR25["mys_20-39"] - MAR25["mys_40-64"]; MAR25["gap_none"] = MAR25["none_40-64"] - MAR25["none_20-39"]
MAR25["gender_gap_pri"] = val("MAR", 2025, "25+", "pri_plus", "Male") - val("MAR", 2025, "25+", "pri_plus", "Female")
MAR25["lgdp"] = np.log(8400.127)                          # Maddison 2022, the last Maddison year
pct = lambda col, higher_is_worse=False: float((tc[col].dropna() < MAR25[col]).mean() * 100)
for col in ["gap_mys", "gap_none", "gender_gap_pri", "mys_20-39", "mys_40-64", "none_20-39", "none_40-64"]:
    KX[f"MAR_pct_{col}"] = pct(col); KX[f"med_trans_{col}"] = float(tc[col].median())
    print(f"  {col:15s} Morocco {MAR25[col]:6.2f} | median at transition {tc[col].median():6.2f} | Morocco pctile {pct(col):5.1f}")
KX["MAR25"] = MAR25; KX["N_trans_cohort"] = int(len(tc))

# nearest historical twins in (log GDP, schooling of the young, schooling of the old)
F = ["lgdp", "mys_20-39", "mys_40-64"]
tw = tc.dropna(subset=F).copy()
sd = tw[F].std()
tw["distance"] = np.sqrt((((tw[F] - pd.Series({f: MAR25[f] for f in F})) / sd) ** 2).sum(axis=1))
tw = tw.sort_values("distance")
tw.to_csv(os.path.join(OUT, "twins.csv"), index=False)
T16 = tw.head(12)[["country", "year", "gdppc_mad", "mys_20-39", "mys_40-64", "gap_mys", "none_40-64", "surv10", "distance"]].copy()
T16.columns = ["Country", "Transition", "GDP pc (Maddison)", "MYS 20–39", "MYS 40–64", "Gap (yrs)", "% none 40–64", "Survived 10y", "Distance"]
T16 = pd.concat([pd.DataFrame([{"Country": "MOROCCO 2025", "Transition": np.nan, "GDP pc (Maddison)": 8400.1,
        "MYS 20–39": MAR25["mys_20-39"], "MYS 40–64": MAR25["mys_40-64"], "Gap (yrs)": MAR25["gap_mys"],
        "% none 40–64": MAR25["none_40-64"], "Survived 10y": np.nan, "Distance": 0.0}]), T16], ignore_index=True)
table("T16_historical_twins", T16.round(2),
      f"Table 16. Morocco's nearest historical twins: the democratic transitions closest to Morocco 2025 in "
      f"income and in the schooling of both generations (standardised distance, N={len(tw)})", fmt=".2f")
tw_s = tw.head(12).surv10.dropna()
KX.update(twins=tw.head(12)[["country", "year"]].values.tolist(), twins_surv10=float(tw_s.mean()), twins_n_surv=int(len(tw_s)))

# ============================================================ 5. Gender x cohort
rows = []
for band in ["20-39", "40-64", "65+", "25+"]:
    r = {"Band": band}
    for sex in ("Female", "Male"):
        r[f"MAR % none, {sex.lower()}"] = val("MAR", 2025, band, "none", sex)
        r[f"MAR MYS, {sex.lower()}"] = val("MAR", 2025, band, "mys", sex)
    fm = C2[(C2.band == band)].pivot_table(index=["iso3", "year"], columns="sex", values="none")
    fm = fm.reset_index().rename(columns={"year": "y5"})
    z = ts[["iso3", "y5"]].merge(fm, on=["iso3", "y5"], how="inner")
    r["Transitions: median % none, women"] = z.Female.median(); r["Transitions: median % none, men"] = z.Male.median()
    r["MAR women pctile"] = (z.Female < r["MAR % none, female"]).mean() * 100
    rows.append(r)
T17 = pd.DataFrame(rows)
table("T17_gender_cohort", T17.round(1),
      "Table 17. Where the unschooled stock sits: Morocco 2025 by sex and age, against the median democratic transition")
KX.update(MAR_none_f_4064=float(T17.loc[1, "MAR % none, female"]), MAR_none_m_4064=float(T17.loc[1, "MAR % none, male"]),
          MAR_none_f_2039=float(T17.loc[0, "MAR % none, female"]), MAR_none_f_65=float(T17.loc[2, "MAR % none, female"]),
          MAR_none_f_4064_pct=float(T17.loc[1, "MAR women pctile"]))

# ============================================================ 6. Demographic metabolism: projections to 2060
bench = {"% no schooling, 25+": ("25+", "none", float(ts["none_25+"].median()), "below"),
         "Mean years, 25+": ("25+", "mys", float(ts["mys_25+"].median()), "above"),
         "% ≥ lower secondary, 20+": ("20+", "losec_plus", float(ts["losec_plus_20+"].median()), "above"),
         "% no schooling, 40–64": ("40-64", "none", float(ts["none_40-64"].median()), "below")}
rows = []
for lab, (band, col, thr, side) in bench.items():
    r = {"Benchmark (median at transition)": lab, "Threshold": thr, "Morocco 2020": val("MAR", 2020, band, col)}
    for s in (1, 2, 3):
        d = C[(C.ssp == s) & (C.iso3 == "MAR") & (C.sex == "Both") & (C.band == band) & (C.year >= 2020)].set_index("year")[col].sort_index()
        sgn = -1 if side == "below" else 1
        yr = cross_year(sgn * d, sgn * thr) if (sgn * d.iloc[0]) < sgn * thr else 2020.0
        r[f"SSP{s}"] = yr
    rows.append(r)
T18 = pd.DataFrame(rows)
# replacement arithmetic: adults in year Y who are under 20 today (aged 20..(20+Y-2025-1) in Y)
pop = E[(E.ssp == 2) & (E.iso3 == "MAR") & (E.sex == "Both")].copy(); pop["n"] = pop[ORDER].sum(axis=1)
rep = {}
for Y in (2030, 2035, 2040, 2050):
    d = pop[pop.year == Y]; adults = d[d.a0 >= 20].n.sum(); new = d[(d.a0 >= 20) & (d.a0 < 20 + (Y - 2025))].n.sum()
    rep[Y] = new / adults * 100
KX.update(replacement_share=rep, metabolism=T18.to_dict("records"))
T18[["SSP1", "SSP2", "SSP3"]] = T18[["SSP1", "SSP2", "SSP3"]].round(0)
table("T18_demographic_metabolism", T18.round(1),
      "Table 18. Demographic metabolism: the year Morocco's adult population reaches the median democratic "
      "transition on each margin, under three Wittgenstein Centre scenarios")
print("replacement share of the adult population (SSP2):", {k: round(v, 1) for k, v in rep.items()})

# electorate composition 1950-2060 (Morocco, adults 20+), three scenarios
EC = C[(C.iso3 == "MAR") & (C.band == "20+") & (C.sex == "Both") & (C.year <= 2060)]
EC.to_csv(os.path.join(OUT, "morocco_electorate.csv"), index=False)
ec_lev = E[(E.iso3 == "MAR") & (E.sex == "Both") & (E.a0 >= 20) & (E.year <= 2060)].groupby(["ssp", "year"])[ORDER].sum()
ec_lev.div(ec_lev.sum(axis=1), axis=0).mul(100).reset_index().to_csv(os.path.join(OUT, "morocco_electorate_levels.csv"), index=False)

# ============================================================ 7. Monarchies that became democracies keeping the monarch
v = pd.read_csv(os.path.join(EXT, "vdem_v16_subset.csv")).sort_values(["country_text_id", "year"])
v["mon"] = v.v2expathhs.round().isin([3, 4])                # HOS by hereditary succession or royal council
v["ruling"] = v.mon & (v.v2ex_hosw >= 0.5)                   # ... and at least equal power over the cabinet
g = v.groupby("country_text_id"); v["row_l"] = g.v2x_regime.shift(1)
ev = v[(v.row_l < 2) & (v.v2x_regime >= 2) & v.mon].copy()
# Norway 1906: Haakon VII was offered the throne by the Storting after the 1905 referendum, which
# V-Dem codes as HOS path "other" (8); the monarchy was hereditary from then on, so it belongs here.
# Its 1946 entry is a restoration after occupation and is superseded by the rule "first event only".
ev = pd.concat([ev, v[(v.country_text_id == "NOR") & (v.year == 1906)]]).sort_values("year")
ev = ev[~ev.duplicated("country_text_id", keep="first")]     # first democratisation under a monarch
ev = ev.rename(columns={"country_text_id": "iso3"})
# schooling at the event: long-run series (Lee & Lee 2016 via OWID) for pre-1950 events, WCDE 25+ after
lr = pd.read_csv(os.path.join(RAW, "owid_mys_longrun.csv"))
lrcol = [c for c in lr.columns if c not in ("entity", "code", "year", "owid_region")][0]
lr = lr.rename(columns={"code": "iso3", lrcol: "mys_lr"})[["iso3", "year", "mys_lr"]].dropna()
def lr_at(i, y):
    d = lr[lr.iso3 == i].set_index("year").mys_lr.sort_index()
    return float(np.interp(y, d.index, d.values)) if len(d) and d.index.min() <= y <= d.index.max() else np.nan
lit = pd.read_csv(os.path.join(RAW, "owid_literacy.csv"))
litcol = [c for c in lit.columns if c not in ("entity", "code", "year", "owid_region")][0]
lit = lit.rename(columns={"code": "iso3", litcol: "lit"})[["iso3", "year", "lit"]].dropna()
def lit_at(i, y):
    d = lit[(lit.iso3 == i) & (lit.year.between(y - 15, y + 15))]
    return float(d.iloc[(d.year - y).abs().argsort().iloc[0]].lit) if len(d) else np.nan
gm = p[["iso3", "year", "gdppc_mad"]].dropna()
def gdp_at(i, y):
    d = gm[(gm.iso3 == i) & (gm.year.between(y - 3, y))]
    return float(d.sort_values("year").gdppc_mad.iloc[-1]) if len(d) else np.nan
ev["mys_longrun"] = [lr_at(i, y) for i, y in zip(ev.iso3, ev.year)]
ev.loc[ev.iso3 == "LUX", "mys_longrun"] = np.nan          # long-run series gives 0.2-0.6 yrs in 1900-30: not credible
ev["mys_wcde"] = [val(i, int(round(y / 5) * 5), "25+", "mys") if y >= 1950 else np.nan for i, y in zip(ev.iso3, ev.year)]
ev["none_wcde"] = [val(i, int(round(y / 5) * 5), "25+", "none") if y >= 1950 else np.nan for i, y in zip(ev.iso3, ev.year)]
ev["literacy"] = [lit_at(i, y) for i, y in zip(ev.iso3, ev.year)]
ev["gdppc_mad"] = [gdp_at(i, y) for i, y in zip(ev.iso3, ev.year)]
ev["mys"] = ev.mys_wcde.combine_first(ev.mys_longrun)
ev.to_csv(os.path.join(OUT, "royal_democratisations.csv"), index=False)
T19 = ev[["country_name", "year", "v2x_polyarchy", "gdppc_mad", "mys", "none_wcde", "literacy"]].copy()
T19.columns = ["Country", "Year", "Polyarchy", "GDP pc (Maddison)", "Mean years, 25+", "% none, 25+", "Adult literacy %"]
mar_lit = p[(p.iso3 == "MAR")].dropna(subset=["lit_adult"]).sort_values("year").lit_adult.iloc[-1]
T19 = pd.concat([T19.sort_values("Year"), pd.DataFrame([{"Country": "MOROCCO (2025)", "Year": 2025,
        "Polyarchy": 0.259, "GDP pc (Maddison)": 8400.1, "Mean years, 25+": val("MAR", 2025, "25+", "mys"),
        "% none, 25+": val("MAR", 2025, "25+", "none"), "Adult literacy %": mar_lit}])], ignore_index=True)
table("T19_royal_democratisations", T19.round(2),
      "Table 19. Monarchies that became democracies while keeping the monarch (V-Dem v16), and Morocco. "
      "Mean years: WCDE 25+ from 1950, Lee-Lee long-run 15–64 before", fmt=".2f")
KX.update(royal_n=int(len(ev)), royal_med_mys=float(ev.mys.median()), royal_med_gdp=float(ev.gdppc_mad.median()),
          royal_pct_mys_below_MAR=float((ev.mys.dropna() < val("MAR", 2025, "25+", "mys")).mean() * 100),
          royal_pct_gdp_below_MAR=float((ev.gdppc_mad.dropna() < 8400.1).mean() * 100))
rm = v[(v.year == 2025) & v.ruling][["country_text_id", "country_name", "v2x_polyarchy", "v2x_regime"]]
rm.to_csv(os.path.join(OUT, "ruling_monarchies_2025.csv"), index=False)
KX["ruling_monarchies_2025"] = rm.country_name.tolist()

json.dump(KX, open(os.path.join(OUT, "key_numbers_ext.json"), "w"), indent=1, default=float)
print("\nwrote key_numbers_ext.json with", len(KX), "entries")
