"""
13_figures_extended.py -- Figures 13-28 for the extended (cohort / disaggregated) analysis.
Same palette and typography as 04_figures.py (validated reference instance: slots 1-3 clear the
all-pairs CVD gates); ordinal education ramps run warm (no schooling) to cool (post-secondary).
"""
import os, json
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(HERE, "..", "data", "clean"); OUT = os.path.join(CLEAN, "ext")
FIG = os.path.join(HERE, "..", "figures"); TAB = os.path.join(HERE, "..", "tables")
# ---- house style: FAB burgundy, Times New Roman (see fab_style.py) ----
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fab_style import *
apply()
LEVC = dict(LEVELS)
LEVN = {"none": "No schooling", "incpri": "Incomplete primary", "pri": "Primary", "losec": "Lower secondary",
        "upsec": "Upper secondary", "post": "Post-secondary"}
ORDER = list(LEVC)

def save(fig, n):
    for e in ("pdf", "png"): fig.savefig(os.path.join(FIG, f"{n}.{e}"))
    plt.close(fig); print("  wrote", n)
def note(ax, s, y=-0.19, x=0):
    ax.annotate(s, xy=(x, y), xycoords="axes fraction", fontsize=7.4, color=MUTED, va="top", ha="left")
def title(fig, s, y=1.03): fig.suptitle(s, x=0.005, ha="left", fontsize=12, fontweight="normal", y=y)

K = json.load(open(os.path.join(OUT, "key_numbers_ext.json")))
p = pd.read_csv(os.path.join(CLEAN, "panel.csv"), low_memory=False)
NAME = p.dropna(subset=["country"]).drop_duplicates("iso3").set_index("iso3")["country"].to_dict()
NAME.update({"KOR": "South Korea", "TWN": "Taiwan", "TUR": "Türkiye"})
C = pd.read_csv(os.path.join(OUT, "cohort_panel.csv.gz"))
E = pd.read_csv(os.path.join(OUT, "wcde_epop_5yr.csv.gz"))
W = pd.read_csv(os.path.join(OUT, "generational_gap_2025.csv")).set_index("iso3")
TS = pd.read_csv(os.path.join(OUT, "transitions_cohorts.csv"))
M25 = K["MAR25"]

# ============================================================ F13  the generational gap, world and transitions
fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharex=True, sharey=True)
for ax in axes:
    ax.plot([0, 15], [0, 15], color=NEUT, lw=1.0, zorder=1)
    for g_, ls in ((2, (0, (4, 3))), (4, (0, (1, 2)))):
        ax.plot([0, 15 - g_], [g_, 15], color=MUTED, lw=0.8, ls=ls, zorder=1)
    ax.legend(handles=[Line2D([], [], color=NEUT, lw=1.0, label="same schooling in both cohorts"),
                       Line2D([], [], color=MUTED, lw=0.8, ls=(0, (4, 3)), label="20–39s two years ahead"),
                       Line2D([], [], color=MUTED, lw=0.8, ls=(0, (1, 2)), label="20–39s four years ahead")],
              loc="lower right", fontsize=7.4)
    ax.set_xlim(0, 14.2); ax.set_ylim(0, 14.2); ax.set_aspect("equal"); ax.grid(True); ax.set_axisbelow(True)
    ax.set_xlabel("Mean years of schooling, aged 40–64")
a = axes[0]
o = W.drop(index="MAR")
a.scatter(o["mys_40-64"], o["mys_20-39"], s=15, c=NEUT, edgecolors="none", zorder=2)
LB = {"BTN": (-5, 3), "YEM": (4, 3), "NPL": (-5, -10), "TUN": (5, -2), "SLE": (4, 3), "IND": (4, -9), "EGY": (-5, 2),
      "KOR": (-4, -10), "VNM": (4, -9), "DZA": (5, 2), "JOR": (5, -6)}
boxes_a = []
r = W.loc["MAR"]
a.scatter(r["mys_40-64"], r["mys_20-39"], s=120, c=BLUE, marker="D", edgecolors="white", linewidths=1.5, zorder=5)
reserve_point(a, (r["mys_40-64"], r["mys_20-39"]), boxes_a, r=10)
reserve(halo(a.annotate(f"Morocco\ngap {r.gap_mys:.1f} yrs · rank {int(r.rank_gap_mys)} of {len(W)}",
                        xy=(r["mys_40-64"], r["mys_20-39"]), xytext=(0, 72), textcoords="offset points",
                        fontsize=8.6, fontweight="bold", color=BLUE, ha="center", zorder=6,
                        arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8, shrinkA=2, shrinkB=6))), boxes_a, pad=2.5)
for iso, (dx, dy) in LB.items():
    rr = W.loc[iso]
    a.scatter(rr["mys_40-64"], rr["mys_20-39"], s=22, c=INK2, edgecolors="none", zorder=3)
    halo(place_label(a, (rr["mys_40-64"], rr["mys_20-39"]), NAME.get(iso, iso), boxes_a,
                     cands=[(dx, dy, "right" if dx < 0 else "left", "baseline")] + list(CANDIDATES),
                     fontsize=7.2, color=INK2, zorder=4), lw=2.2)
a.set_ylabel("Mean years of schooling, aged 20–39")
a.set_title(f"$\\bf{{a.}}$  {len(W)} countries in 2025", loc="left", fontweight="normal")
b = axes[1]
tc = TS.dropna(subset=["mys_20-39", "mys_40-64"])
b.scatter(tc["mys_40-64"], tc["mys_20-39"], s=22, facecolors="white", edgecolors=MUTED, linewidths=0.8, zorder=2)
boxes_b = []
b.scatter(M25["mys_40-64"], M25["mys_20-39"], s=230, marker="*", c=BLUE, edgecolors="white", linewidths=1.4, zorder=5)
reserve_point(b, (M25["mys_40-64"], M25["mys_20-39"]), boxes_b, r=10)
reserve(halo(b.annotate(f"Morocco 2025\nyoung: {K['MAR_pct_mys_20-39']:.0f}th pct · old: {K['MAR_pct_mys_40-64']:.0f}th pct\n"
                        f"gap: {K['MAR_pct_gap_mys']:.0f}th pct of transitions",
                        xy=(M25["mys_40-64"], M25["mys_20-39"]), xytext=(-62, 52), textcoords="offset points",
                        fontsize=8.4, fontweight="bold", color=BLUE, ha="center", zorder=6,
                        arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8, shrinkA=2, shrinkB=8))), boxes_b, pad=2.5)
for iso, yr, dx, dy in (("KOR", 1988, 5, -6), ("TWN", 1996, -5, 5), ("ESP", 1978, -5, -10), ("PRT", 1976, 5, -3),
                        ("TUN", 2012, 5, 2), ("IDN", 1999, 5, -4), ("CYP", 1975, -5, 4), ("MEX", 1996, -5, -6),
                        ("BTN", 2009, 5, 0)):
    rr = tc[(tc.iso3 == iso) & (tc.year == yr)]
    if not len(rr): continue
    rr = rr.iloc[0]
    b.scatter(rr["mys_40-64"], rr["mys_20-39"], s=26, c=ORANGE, edgecolors="none", zorder=3)
    halo(place_label(b, (rr["mys_40-64"], rr["mys_20-39"]), f"{NAME.get(iso, iso)} {yr}", boxes_b,
                     cands=[(dx, dy, "right" if dx < 0 else "left", "baseline")] + list(CANDIDATES),
                     fontsize=7.2, color=ORANGE, zorder=4), lw=2.2)
b.set_title(f"$\\bf{{b.}}$  {len(tc)} democratic transitions, at the moment of transition", loc="left", fontweight="normal")
title(fig, "$\\bf{Figure\\ 13.}$  Few countries have ever carried a generational schooling gap as wide as Morocco's")
note(a, "Distance above the diagonal = how much better schooled the 20–39 cohort is than the 40–64 cohort. Panel b places each transition\n"
        "since 1960 at the nearest 5-year Wittgenstein point. Source: Wittgenstein Centre v3.3 (SSP2; 2025 values are projections from 2020); V-Dem v16.", y=-0.14)
save(fig, "F13_generational_gap")

# ============================================================ F14  education pyramids
def pyramid(ax, iso, yr, ssp=2, lab=None):
    d = E[(E.ssp == ssp) & (E.iso3 == iso) & (E.year == yr) & (E.sex != "Both") & (E.a0 >= 20)]
    d = d.copy(); d.loc[d.a0 >= 80, "a0"] = 80                        # top bar = 80+
    d = d.groupby(["sex", "a0"])[ORDER].sum()
    tot = d.values.sum()
    ages = sorted(d.index.get_level_values(1).unique())
    for sex, sgn in (("Male", -1), ("Female", 1)):
        left = np.zeros(len(ages))
        for lev in ORDER:
            vals = np.array([d.loc[(sex, a_), lev] if (sex, a_) in d.index else 0 for a_ in ages]) / tot * 100
            ax.barh(ages, sgn * vals, left=sgn * left, height=4.3, color=LEVC[lev], edgecolor="white", linewidth=0.25)
            left += vals
    ax.axvline(0, color=INK2, lw=0.6)
    ax.set_yticks([20, 30, 40, 50, 60, 70, 80]); ax.set_yticklabels(["20", "30", "40", "50", "60", "70", "80+"])
    ax.set_xlim(-PYLIM, PYLIM); ax.set_xticks([-8, -4, 0, 4, 8]); ax.set_xticklabels(["8", "4", "0", "4", "8"])
    none_share = d["none"].sum() / tot * 100
    head, _, tail = (lab or NAME.get(iso, iso)).partition(" (")
    sub = f"({tail}  ·  " if tail else ""
    ax.set_title(f"{head}\n{sub}{none_share:.0f}% of adults unschooled" + (")" if tail else ""), loc="left", fontsize=9.4,
                 fontweight="bold")
    ax.annotate("men", xy=(0.03, 0.96), xycoords="axes fraction", fontsize=7.4, color=MUTED, va="top")
    ax.annotate("women", xy=(0.97, 0.96), xycoords="axes fraction", fontsize=7.4, color=MUTED, va="top", ha="right")
PY = [("MAR", 2025, "Morocco 2025"), ("MAR", 2050, "Morocco 2050 (SSP2 projection"), ("KOR", 1985, "South Korea 1985 (3 yrs before transition"),
      ("ESP", 1975, "Spain 1975 (3 yrs before transition"), ("TUN", 2010, "Tunisia 2010 (2 yrs before transition"),
      ("BTN", 2005, "Bhutan 2005 (4 yrs before transition")]
def _maxshare(iso, yr):
    d = E[(E.ssp == 2) & (E.iso3 == iso) & (E.year == yr) & (E.sex != "Both") & (E.a0 >= 20)]
    return (d[ORDER].sum(axis=1) / d[ORDER].values.sum() * 100).max()
PYLIM = np.ceil(max(_maxshare(i, y) for i, y, _ in PY) + 0.5)
fig, axes = plt.subplots(2, 3, figsize=(11.4, 7.4), sharey=True)
for ax, (iso, yr, lab) in zip(axes.flat, PY): pyramid(ax, iso, yr, lab=lab)
for ax in axes[1]: ax.set_xlabel("% of the adult population (20+)")
for ax in axes[:, 0]: ax.set_ylabel("Age")
fig.legend(handles=[Patch(color=LEVC[l], label=LEVN[l]) for l in ORDER], loc="lower center", ncol=6,
           bbox_to_anchor=(0.5, -0.035), fontsize=8.2)
title(fig, "$\\bf{Figure\\ 14.}$  Education pyramids: Morocco's unschooled adults are older and mostly women — the shape Korea had\n"
           "in 1985 and Tunisia in 2010, but twice Korea's size; Bhutan democratised with twice Morocco's share", y=1.045)
fig.text(0.005, -0.075, "Adults 20+ by 5-year age group, sex and highest level completed, as % of all adults in each panel. Source: Wittgenstein Centre v3.3 "
         "(SSP2); transition years from V-Dem v16 Regimes of the World.", fontsize=7.4, color=MUTED)
fig.tight_layout(h_pad=2.2)
save(fig, "F14_education_pyramids")

# ============================================================ F15  birth-cohort expansion curves
B = pd.read_csv(os.path.join(OUT, "birth_cohorts.csv"))
BX = pd.read_csv(os.path.join(OUT, "birth_cohort_crossings.csv"))
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))
HL = {"KOR": ORANGE, "TUN": AQUA, "ESP": INK2}
GR = ["TWN", "PRT", "TUR", "DZA", "EGY", "JOR", "IRN", "IDN", "VNM", "BRA"]
for ax, var, sex, ttl in ((axes[0], "losec_plus", "Both", "a.  % with at least lower secondary schooling"),
                          (axes[1], "none", "Female", "b.  Women: % who never went to school")):
    for iso in GR:
        d = B[(B.iso3 == iso) & (B.sex == sex)].sort_values("birth")
        ax.plot(d.birth, d[var], color=NEUT, lw=0.9, zorder=1)
    stagger = {"TUN": 10, "ESP": 0, "KOR": -10} if var == "none" else {}
    for iso, col in HL.items():
        d = B[(B.iso3 == iso) & (B.sex == sex)].sort_values("birth")
        ax.plot(d.birth, d[var], color=col, lw=1.7, zorder=2)
        yy = d[var].iloc[-1]
        ax.annotate(NAME[iso], xy=(d.birth.iloc[-1], yy), xytext=(4, stagger.get(iso, 0)), textcoords="offset points", fontsize=7.8,
                    color=col, va="center", fontweight="bold")
    d = B[(B.iso3 == "MAR") & (B.sex == sex)].sort_values("birth")
    ax.plot(d.birth, d[var], color=BLUE, lw=2.6, zorder=3)
    ax.annotate("Morocco", xy=(d.birth.iloc[-1], d[var].iloc[-1]), xytext=(4, 0), textcoords="offset points",
                fontsize=8.6, color=BLUE, va="center", fontweight="bold")
    ax.set_xlim(1918, 2003); ax.set_ylim(0, 100); ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_xlabel("Year of birth"); ax.set_title(ttl, loc="left", fontweight="normal")
a = axes[0]
a.axhline(50, color=MUTED, lw=0.8, ls=(0, (3, 3)))
kb, mb = K["KOR_birth_losec50"], K["MAR_birth_losec50"]
a.annotate("", xy=(mb, 50), xytext=(kb, 50), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.3))
a.annotate(f"{mb - kb:.0f} years:\nKorea's cohort of {kb:.0f},\nMorocco's of {mb:.0f}", xy=((kb + mb) / 2, 50), xytext=(0, 8),
           textcoords="offset points", ha="center", fontsize=8, color=BLUE, fontweight="bold")
a.set_ylabel("% of the birth cohort (observed at age 30–34)")
title(fig, "$\\bf{Figure\\ 15.}$  Morocco's schooling revolution began half a century after Korea's and a generation after Tunisia's")
note(a, "Each line follows one birth cohort's completed attainment, read at age 30–34 (cohort born 1918 observed in 1950 … born 1993 observed in 2025, projected).\n"
        "Grey: Taiwan, Portugal, Türkiye, Algeria, Egypt, Jordan, Iran, Indonesia, Vietnam, Brazil. Source: Wittgenstein Centre v3.3 (SSP2).", y=-0.17)
save(fig, "F15_birth_cohorts")

# ============================================================ F16  historical twins
tw = pd.read_csv(os.path.join(OUT, "twins.csv")).head(12)
fig, ax = plt.subplots(figsize=(8.6, 5.4))
rows = [("Morocco 2025", M25["mys_40-64"], M25["mys_20-39"], np.nan, True)] + \
       [(f"{NAME.get(r.iso3, r.country)} {int(r.year)}", r["mys_40-64"], r["mys_20-39"], r.surv10, False) for _, r in tw.iterrows()]
for i, (lab, o_, y_, s_, mar) in enumerate(rows):
    yy = len(rows) - 1 - i
    ax.plot([o_, y_], [yy, yy], color=BLUE if mar else NEUT, lw=2.4 if mar else 1.8, zorder=1)
    ax.scatter([o_], [yy], s=60 if mar else 38, c=ORANGE, edgecolors="white", linewidths=0.8, zorder=2)
    ax.scatter([y_], [yy], s=60 if mar else 38, c=BLUE, edgecolors="white", linewidths=0.8, zorder=2)
    tag = "" if mar else ("   survived 10 yrs" if s_ == 1 else "   reverted within 10 yrs" if s_ == 0 else "")
    ax.annotate(lab + tag, xy=(y_, yy), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8.2,
                color=BLUE if mar else (INK2 if s_ != 0 else ORANGE), fontweight="bold" if mar else "normal")
ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.set_xlim(3.5, 13.5)
ax.set_xlabel("Mean years of schooling")
ax.legend(handles=[Line2D([], [], marker="o", ls="", color=ORANGE, label="aged 40–64"),
                   Line2D([], [], marker="o", ls="", color=BLUE, label="aged 20–39")], loc="upper right")
ax.grid(axis="x"); ax.set_axisbelow(True)
ax.set_title(f"$\\bf{{Figure\\ 16.}}$  Morocco's nearest historical twins: {int(K['twins_surv10']*K['twins_n_surv'])} of the {K['twins_n_surv']} "
             f"democracies born\nin its image survived at least ten years", loc="left", fontweight="normal", fontsize=11.5, pad=10)
note(ax, "The 12 transitions (of 117 with complete data) closest to Morocco 2025 in log GDP per capita and the schooling of both cohorts\n"
         "(standardised Euclidean distance). Sources: Wittgenstein Centre v3.3; Maddison Project 2023; V-Dem v16.", y=-0.13)
save(fig, "F16_historical_twins")

# ============================================================ F17  gender x age
def none_by_age(iso, yr, sex):
    d = E[(E.ssp == 2) & (E.iso3 == iso) & (E.year == yr) & (E.sex == sex) & (E.a0 >= 20) & (E.a0 <= 80)].set_index("a0")
    return d["none"] / d[ORDER].sum(axis=1) * 100
tr_f = []
for _, r in TS.iterrows():
    s_ = none_by_age(r.iso3, int(r.y5), "Female")
    if len(s_): tr_f.append(s_)
TF = pd.concat(tr_f, axis=1)
fig, ax = plt.subplots(figsize=(8.8, 5.0))
ages = TF.index.values
ax.fill_between(ages, TF.quantile(0.25, axis=1), TF.quantile(0.75, axis=1), color=GRID, zorder=1)
ax.plot(ages, TF.median(axis=1), color=MUTED, lw=1.6, ls=(0, (4, 2)), zorder=2)
ax.annotate("women in the median democratic\ntransition (band: middle half)", xy=(70, TF.median(axis=1).loc[70]), xytext=(71, 30),
            textcoords="data", fontsize=7.8, color=MUTED, ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
for sex, col, lab in (("Female", ORANGE, "Moroccan women, 2025"), ("Male", BLUE, "Moroccan men, 2025")):
    s_ = none_by_age("MAR", 2025, sex)
    ax.plot(s_.index, s_.values, color=col, lw=2.4, marker="o", ms=4, zorder=3)
    ax.annotate(lab, xy=(s_.index[-1], s_.values[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8.4,
                color=col, fontweight="bold", va="center")
s_ = none_by_age("MAR", 2050, "Female")
ax.plot(s_.index, s_.values, color=ORANGE, lw=1.4, ls=(0, (1, 1.5)), zorder=3)
ax.annotate("Moroccan women, 2050 (SSP2)", xy=(57.5, float(np.interp(57.5, s_.index, s_.values))), xytext=(62, 12), textcoords="data",
            fontsize=7.8, color=ORANGE, ha="left", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
ax.set_xticks(range(20, 85, 10)); ax.set_xticklabels([f"{a_}–{a_+4}" if a_ < 80 else "80+" for a_ in range(20, 85, 10)])
ax.set_xlim(19, 92); ax.set_ylim(0, 100); ax.grid(axis="y"); ax.set_axisbelow(True)
ax.set_xlabel("Age group"); ax.set_ylabel("% who never went to school")
T17 = pd.read_csv(os.path.join(TAB, "T17_gender_cohort.csv")).set_index("Band")
ax.set_title(f"$\\bf{{Figure\\ 17.}}$  The unschooled stock is overwhelmingly women over forty: {K['MAR_none_f_4064']:.0f}% of Moroccan women\n"
             f"aged 40–64 never went to school, against {K['MAR_none_m_4064']:.0f}% of men and "
             f"{T17.loc['40-64', 'Transitions: median % none, women']:.0f}% of women in the median transition",
             loc="left", fontweight="normal", fontsize=11.2, pad=10)
note(ax, f"Median and interquartile range across the {TF.shape[1]} democratic transitions since 1960 (women, at the transition's 5-year point). Source: Wittgenstein Centre v3.3.", y=-0.12)
save(fig, "F17_gender_age")

# ============================================================ F18  demographic metabolism
fig = plt.figure(figsize=(11.6, 4.6)); gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1, 1], wspace=0.28)
a = fig.add_subplot(gs[0])
d = E[(E.ssp == 2) & (E.iso3 == "MAR") & (E.sex == "Both") & (E.a0 >= 25) & (E.year <= 2060)].groupby("year")[ORDER].sum()
sh = d.div(d.sum(axis=1), axis=0) * 100
a.stackplot(sh.index, [sh[l] for l in ORDER], colors=[LEVC[l] for l in ORDER], linewidth=0)
a.axvline(2020, color="white", lw=1.2); a.axvline(2020, color=INK2, lw=0.6, ls=(0, (2, 2)))
a.annotate("projection", xy=(2021.5, 3), fontsize=7.6, color="white", va="bottom", fontweight="bold")
a.set_xlim(1950, 2060); a.set_ylim(0, 100); a.set_ylabel("% of adults 25+")
a.set_title("$\\bf{a.}$  Adults 25+ by schooling, 1950–2060", loc="left", fontweight="normal")
a.annotate("no schooling", xy=(1985, 72), fontsize=8, color="white", fontweight="bold")
a.annotate("post-secondary", xy=(2031, 92), fontsize=7.6, color="white", fontweight="bold")
T18 = pd.read_csv(os.path.join(TAB, "T18_demographic_metabolism.csv"))
for ax, (lab, band, col, thr_key) in zip([fig.add_subplot(gs[1]), fig.add_subplot(gs[2])],
                                         [("% no schooling, 25+", "25+", "none", 0), ("Mean years, 25+", "25+", "mys", 1)]):
    thr = float(T18.iloc[thr_key].Threshold)
    for s_, col_, ls in ((1, AQUA, "-"), (2, BLUE, "-"), (3, ORANGE, "-")):
        d = C[(C.ssp == s_) & (C.iso3 == "MAR") & (C.sex == "Both") & (C.band == band) & C.year.between(2000, 2060)].sort_values("year")
        ax.plot(d.year, d[col], color=col_, lw=1.9 if s_ == 2 else 1.3, ls=ls, label=f"SSP{s_}")
    ax.axhline(thr, color=MUTED, lw=0.9, ls=(0, (4, 2)))
    yr = float(T18.iloc[thr_key].SSP2)
    ax.axvline(yr, color=BLUE, lw=0.8, ls=(0, (1, 2)))
    if col == "none":
        ax.annotate(f"median democratiser: {thr:.1f}%\nreached ≈ {yr:.0f} (SSP2)", xy=(yr, thr), xytext=(2023, 50),
                    textcoords="data", fontsize=7.8, color=BLUE, fontweight="bold", ha="left",
                    arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    else:
        ax.annotate(f"median democratiser: {thr:.1f} yrs\nreached ≈ {yr:.0f} (SSP2)", xy=(yr, thr), xytext=(8, -42),
                    textcoords="offset points", fontsize=7.8, color=BLUE, fontweight="bold", ha="left")
    ax.set_xlim(2000, 2060); ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_title(("$\\bf{b.}$  " if col == "none" else "$\\bf{c.}$  ") + lab, loc="left", fontweight="normal")
    if col == "none": ax.legend(loc="upper right", fontsize=7.6)
title(fig, "$\\bf{Figure\\ 18.}$  Demographic metabolism: the unschooled share will fall to the democratisers' median around 2045\n"
           "whatever the education policy — it is already written in the age structure", y=1.07)
note(a, "Panel b's three scenarios are almost indistinguishable because the unschooled adults of 2045 have long left school age; only mortality and\n"
        "cohort replacement move the curve. Source: Wittgenstein Centre v3.3, SSP1 (rapid), SSP2 (central), SSP3 (stalled) scenarios.", y=-0.13)
save(fig, "F18_demographic_metabolism")

# ============================================================ F19  cohort trajectories and the timing of transition
TR = {"MAR": None, "KOR": 1988, "TWN": 1996, "ESP": 1978, "PRT": 1976, "TUN": 2012, "IDN": 1999, "BTN": 2009, "VNM": None}
fig, axes = plt.subplots(3, 3, figsize=(11.2, 8.2), sharex=True, sharey=True)
PEAK = {}
for ax, (iso, yr) in zip(axes.flat, TR.items()):
    d = C[(C.ssp == 2) & (C.iso3 == iso) & (C.sex == "Both") & C.band.isin(["20-39", "40-64"]) & C.year.between(1950, 2050)]
    y_ = d[d.band == "20-39"].set_index("year").mys.sort_index(); o_ = d[d.band == "40-64"].set_index("year").mys.sort_index()
    ax.fill_between(y_.index, o_.values, y_.values, color="#EFDCDD" if iso != "MAR" else "#E3C9CB", zorder=1)
    ax.plot(y_.index, y_.values, color=BLUE, lw=2.0, zorder=2); ax.plot(o_.index, o_.values, color=ORANGE, lw=2.0, zorder=2)
    if yr:
        ax.axvline(yr, color=INK2, lw=0.9, ls=(0, (3, 2)))
        g_ = float(np.interp(yr, y_.index, y_.values) - np.interp(yr, o_.index, o_.values))
        ax.annotate(f"transition {yr}\ngap {g_:.1f} yrs", xy=(yr, 0.6), xytext=(3, 0), textcoords="offset points",
                    fontsize=7.4, color=INK2)
    else:
        ax.axvline(2025, color=BLUE if iso == "MAR" else MUTED, lw=0.9, ls=(0, (1, 2)))
        g_ = float(np.interp(2025, y_.index, y_.values) - np.interp(2025, o_.index, o_.values))
        ax.annotate(f"no transition\n2025 gap {g_:.1f} yrs", xy=(2025, 0.6), xytext=(-3, 0), textcoords="offset points",
                    fontsize=7.4, color=BLUE if iso == "MAR" else INK2, ha="right")
    gap = (y_ - o_).dropna(); pk = int(gap.idxmax()); PEAK[iso] = pk
    ax.annotate(f"gap peaks {pk}" + (" (projected)" if pk > 2020 else ""), xy=(0.02, 0.97), xycoords="axes fraction",
                fontsize=7.4, color=MUTED, va="top")
    ax.set_title(NAME.get(iso, iso) if iso != "MAR" else "Morocco", loc="left", fontweight="normal",
                 color=BLUE if iso == "MAR" else INK)
    ax.set_xlim(1950, 2050); ax.set_ylim(0, 15.5); ax.grid(axis="y"); ax.set_axisbelow(True)
for ax in axes[:, 0]: ax.set_ylabel("Mean years of schooling")
axes[0, 0].legend(handles=[Line2D([], [], color=BLUE, lw=2, label="aged 20–39"), Line2D([], [], color=ORANGE, lw=2, label="aged 40–64")],
                  loc="upper left", bbox_to_anchor=(0, 0.9), fontsize=7.6)
print("  gap peak years:", PEAK)
before = [NAME[i] for i, y in TR.items() if y and y < PEAK[i]]
after = [NAME[i] for i, y in TR.items() if y and y >= PEAK[i]]
title(fig, f"$\\bf{{Figure\\ 19.}}$  Democratisation has come on both sides of the generational-gap peak — before it ({', '.join(before)})\n"
           f"and after it ({', '.join(after)}). Morocco's gap is still widening and peaks around {PEAK['MAR']}", y=1.05)
fig.text(0.005, -0.02, "Shaded area = generational gap. Source: Wittgenstein Centre v3.3 (SSP2; values after 2020 projected); transition years from V-Dem v16.",
         fontsize=7.4, color=MUTED)
fig.tight_layout()
save(fig, "F19_cohort_trajectories")

# ============================================================ F20  which margin of education predicts democracy?
cf = pd.read_csv(os.path.join(OUT, "margin_coefs.csv"))
MN = {"mys": "Mean years, 25+", "none": "% no schooling, 25+", "pri": "% ≥ primary", "losec": "% ≥ lower secondary",
      "upsec": "% ≥ upper secondary", "post": "% post-secondary", "mys_young": "Mean years, aged 20–39 †", "mys_old": "Mean years, aged 40–64 †"}
SP = [("Pooled, year FE", BLUE, "Across countries (year FE)"), ("Two-way FE", ORANGE, "Within countries (country + year FE)")]
fig, ax = plt.subplots(figsize=(8.8, 5.0))
for j, (sp, col, lab) in enumerate(SP):
    d = cf[cf.spec == sp].set_index("measure").reindex(list(MN))
    yy = np.arange(len(MN))[::-1] + (0.17 if j == 0 else -0.17)
    ax.errorbar(d.b, yy, xerr=1.96 * d.se, fmt="o", color=col, ms=5.5, lw=1.4, capsize=0, label=lab, zorder=3)
ax.axvline(0, color=INK2, lw=0.7)
ax.axhspan(-0.6, 1.5, color=GRID, zorder=0)
ax.set_yticks(np.arange(len(MN))[::-1]); ax.set_yticklabels(list(MN.values()))
ax.set_xlabel("Effect of one standard deviation (lagged 5 years) on the electoral democracy index")
ax.legend(loc="lower right", fontsize=8); ax.grid(axis="x"); ax.set_axisbelow(True)
ax.set_title("$\\bf{Figure\\ 20.}$  Which margin of education predicts democracy?  Across countries: the bottom of the\n"
             "distribution, and the older cohort's schooling.  Within countries over time: no positive effect",
             loc="left", fontweight="normal", fontsize=11.2, pad=10)
note(ax, f"OLS of V-Dem's electoral democracy index on each education measure and log GDP pc, 5-yearly panel {int(cf.n.max())} obs., 162 countries,\n"
         "1965–2025; 95% CIs clustered by country. † Young and old entered jointly. Sources: Wittgenstein Centre v3.3; V-Dem v16; Maddison 2023.", y=-0.13)
save(fig, "F20_which_margin")

# ============================================================ F21  hazard: what stands between Morocco and a transition
mh = pd.read_csv(os.path.join(OUT, "morocco_hazard.csv"))
T23 = pd.read_csv(os.path.join(TAB, "T23_morocco_hazard.csv"))
T22a = pd.read_csv(os.path.join(TAB, "T22a_risk_set.csv"))
fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.6), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.62})
a = axes[0]
rs = T22a.set_index(T22a.columns[0])
labs = ["Electoral autocracy", "Closed autocracy, non-monarchical", "Ruling monarchy"]
vals = [rs.loc[l, "Transitions per 100 years"] for l in labs]
cols = [BLUE, NEUT, ORANGE]
a.barh(range(3)[::-1], vals, color=cols, height=0.6)
for i, l in enumerate(labs):
    r = rs.loc[l]
    a.annotate(f"{r['Transitions per 100 years']:.2f}\n{int(r.Transitions)} transitions in {int(r['At-risk years']):,} years",
               xy=(r["Transitions per 100 years"], 2 - i), xytext=(5, 0), textcoords="offset points", va="center", fontsize=8,
               color=ORANGE if l == "Ruling monarchy" else INK2, fontweight="bold" if l == "Ruling monarchy" else "normal")
a.set_yticks(range(3)[::-1]); a.set_yticklabels(["Electoral autocracy", "Closed autocracy,\nno monarch", "Ruling monarchy\n(Morocco's category)"])
a.set_xlim(0, 7.5); a.set_xlabel("Democratic transitions per 100 country-years, 1961–2025")
a.set_title("$\\bf{a.}$  Who ever becomes a democracy?", loc="left", fontweight="normal")
b = axes[1]
lab_short = ["As observed:\nclosed autocracy", "Electoral rather\nthan closed", "…and the young\nschooled like the old",
             "…whole population at the\nmedian transition's schooling", "Average non-monarchical\nautocracy, 2016–25"]
v10 = T23["P(transition within 10 years) (%)"].values
cl = [NEUT, BLUE, ORANGE, AQUA, MUTED]
b.barh(range(len(v10))[::-1], v10, color=cl, height=0.6)
for i, v_ in enumerate(v10):
    b.annotate(f"{v_:.0f}%", xy=(v_, len(v10) - 1 - i), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.4, color=INK2)
b.set_yticks(range(len(v10))[::-1]); b.set_yticklabels(lab_short, fontsize=8)
b.set_xlabel("Predicted probability of a democratic transition within 10 years (%)")
b.set_xlim(0, 40)
b.set_title("$\\bf{b.}$  Morocco's structural odds if the monarch were not the chief executive", loc="left", fontweight="normal")
title(fig, "$\\bf{Figure\\ 21.}$  In 621 ruling-monarchy years since 1961 there has not been a single direct transition to democracy;\n"
           "lift that constraint and Morocco's income and schooling predict odds of about one in five per decade", y=1.07)
note(b, "Panel b: discrete-time logit hazard estimated on non-monarchical autocracies (Table 22, models 2–3), applied to Morocco's 2025 covariates.\n"
        "The young-cohort scenario rests on the generational-gap effect, which is not robust to decade fixed effects (Table 22c).", y=-0.15)
save(fig, "F21_hazard")

# ============================================================ F22  structural expectation vs actual
pj = pd.read_csv(os.path.join(OUT, "expectation_projection.csv"))
fig, ax = plt.subplots(figsize=(9.0, 5.0))
for iso, col, lw in (("JOR", NEUT, 1.2),):
    d = pj[(pj.iso3 == iso) & (pj.ssp == 2)].sort_values("year")
    ax.plot(d.year, d.v2x_polyarchy, color=col, lw=lw)
    last = d.dropna(subset=["v2x_polyarchy"]).iloc[-1]
    ax.annotate(f"{NAME[iso]} (actual)", xy=(last.year, last.v2x_polyarchy), xytext=(4, 0), textcoords="offset points",
                fontsize=7.4, color=MUTED, va="center")
d2 = pj[(pj.iso3 == "MAR") & (pj.ssp == 2)].sort_values("year")
lo = pj[pj.iso3 == "MAR"].groupby("year")[["exp_poly", "exp_poly_mys"]].min().min(axis=1)
hi = pj[pj.iso3 == "MAR"].groupby("year")[["exp_poly", "exp_poly_mys"]].max().max(axis=1)
ax.fill_between(lo.index, lo.values, hi.values, color="#E2E7E4", zorder=1)
ax.plot(d2.year, (d2.exp_poly + d2.exp_poly_mys) / 2, color=AQUA, lw=2.2, zorder=2)
act = d2.dropna(subset=["v2x_polyarchy"])
ax.plot(act.year, act.v2x_polyarchy, color=BLUE, lw=2.6, marker="o", ms=3.5, zorder=3)
ax.fill_between(act.year, act.v2x_polyarchy, ((act.exp_poly + act.exp_poly_mys) / 2), color="#E3C9CB", alpha=0.6, zorder=1)
ax.annotate("Morocco, actual", xy=(2025, act.v2x_polyarchy.iloc[-1]), xytext=(6, -8), textcoords="offset points",
            fontsize=8.6, color=BLUE, fontweight="bold")
e40 = float(d2[d2.year == 2040][["exp_poly", "exp_poly_mys"]].mean(axis=1).iloc[0])
ax.annotate("expected from schooling, the gender gap\nand age structure (SSP1–3 range)", xy=(2040, e40), xytext=(-10, 24),
            textcoords="offset points", fontsize=8.2, color=AQUA, fontweight="bold", ha="right")
ax.annotate("institutional\ndeficit", xy=(2000, 0.29), fontsize=8, color=BLUE, ha="center", va="center")
ax.axhline(0.5, color=MUTED, lw=0.8, ls=(0, (4, 2)))
ax.annotate("0.5 — minimum for an electoral democracy (RoW)", xy=(1971, 0.505), fontsize=7.4, color=MUTED, va="bottom")
ax.axvline(2025, color=INK2, lw=0.6, ls=(0, (2, 2)))
ax.set_xlim(1970, 2062); ax.set_ylim(0, 0.75); ax.grid(axis="y"); ax.set_axisbelow(True)
ax.set_ylabel("V-Dem electoral democracy index")
ax.set_title("$\\bf{Figure\\ 22.}$  Morocco has been below its demographic-educational expectation every year since 1970,\n"
             "and the expectation keeps rising: unless institutions change, the deficit will widen",
             loc="left", fontweight="normal", fontsize=11.2, pad=10)
note(ax, "Expectation: pooled 5-yearly regressions of the index on % ≥ lower secondary (or mean years), the male–female primary gap and the youth share,\n"
         "with year effects (Table 24), fed with Wittgenstein Centre projections; year effect held at 2025 thereafter. Sources: V-Dem v16; WCDE v3.3.", y=-0.12)
save(fig, "F22_structural_expectation")

# ============================================================ F23  component anatomy
T25 = pd.read_csv(os.path.join(TAB, "T25_components.csv"))
T25 = T25[T25.Component != "Electoral democracy index"].iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(9.2, 5.6))
yy = np.arange(len(T25))
for i, r in T25.iterrows():
    ax.plot([r["Median, other ruling monarchies 2025"], r["Median, transition year"]], [i, i], color=GRID, lw=5, zorder=1, solid_capstyle="round")
ax.scatter(T25["Median, other ruling monarchies 2025"], yy, s=36, c=NEUT, zorder=2, label="Median of the other ruling monarchies, 2025")
ax.scatter(T25["Predicted from income & schooling"], yy, s=58, facecolors="white", edgecolors=AQUA, linewidths=1.6, zorder=3,
           label="Predicted for Morocco from income and schooling")
ax.scatter(T25["Median, transition year"], yy, s=40, c=ORANGE, zorder=3, label="Median democracy in its transition year")
ax.scatter(T25["Morocco 2025"], yy, s=90, marker="D", c=BLUE, edgecolors="white", linewidths=1.2, zorder=4, label="Morocco 2025")
ax.set_yticks(yy); ax.set_yticklabels(T25.Component)
eo = T25.index[T25.Component == "Elected officials"][0]
ax.axhspan(eo - 0.45, eo + 0.45, color="#F6EDEE", zorder=0)
ax.annotate("the one component where Morocco is\nat the floor: the chief executive is not\nchosen through elections", xy=(0.02, eo), xytext=(0.18, eo - 1.3),
            fontsize=8, color=ORANGE, fontweight="bold", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
ax.set_xlim(-0.03, 1.03); ax.set_xlabel("V-Dem index (0–1)")
ax.legend(loc="lower center", bbox_to_anchor=(0.42, -0.24), ncol=2, fontsize=7.8)
ax.grid(axis="x"); ax.set_axisbelow(True)
ax.set_title("$\\bf{Figure\\ 23.}$  The anatomy of the deficit: on judicial and legislative constraints Morocco already matches the\n"
             "typical new democracy and beats its own development-based prediction; it scores zero only on elected officials",
             loc="left", fontweight="normal", fontsize=11, pad=10)
save(fig, "F23_component_anatomy")

# ============================================================ F24  the waterfall
T26 = pd.read_csv(os.path.join(TAB, "T26_counterfactuals.csv"))
fig, ax = plt.subplots(figsize=(9.2, 4.8))
ax.axhspan(0, 0.5, color="#FBFAF8", zorder=0); ax.axhspan(0.5, 0.8, color="#FAF2F2", zorder=0)
ax.annotate("autocracy", xy=(4.35, 0.03), fontsize=8, color=MUTED, ha="right")
ax.annotate("electoral democracy", xy=(4.35, 0.52), fontsize=8, color=BLUE, ha="right")
st = T26["Electoral democracy index"].values[:4]
labs = ["Observed\n2025", "Chief executive\naccountable to the\nelected parliament", "+ clean elections\nat the median\ntransition",
        "+ association and\nexpression at the\nmedian transition"]
prev = 0
for i, v_ in enumerate(st):
    if i == 0:
        ax.bar(i, v_, color=NEUT, width=0.62, zorder=2)
    else:
        ax.bar(i, v_ - prev, bottom=prev, color=[ORANGE, AQUA, BLUE][i - 1], width=0.62, zorder=2)
        ax.plot([i - 1 + 0.31, i - 0.31], [prev, prev], color=INK2, lw=0.6, zorder=1)
    ax.annotate(f"{v_:.3f}" if i == 0 else f"{v_:.3f}\n(+{v_ - prev:.3f})", xy=(i, v_), xytext=(0, 4), textcoords="offset points",
                ha="center", fontsize=8.4, color=INK2, fontweight="bold")
    prev = v_
ax.axhline(0.5, color=BLUE, lw=0.9, ls=(0, (4, 2)))
ax.axhline(K["MAR_pred_poly"], color=AQUA, lw=0.9, ls=(0, (1, 2)))
ax.annotate(f"level predicted by income\nand schooling ({K['MAR_pred_poly']:.2f})", xy=(4.38, K["MAR_pred_poly"]), xytext=(0, -4),
            textcoords="offset points", fontsize=7.6, color=AQUA, ha="right", va="top")
ax.set_xticks(range(4)); ax.set_xticklabels(labs, fontsize=8.2); ax.set_xlim(-0.5, 4.4); ax.set_ylim(0, 0.72)
ax.set_ylabel("V-Dem electoral democracy index")
ax.set_title("$\\bf{Figure\\ 24.}$  The parliamentary-monarchy arithmetic: one institutional change takes Morocco from 0.26 to 0.40;\n"
             "freedoms at the level typical of new democracies take it past the 0.5 democracy threshold",
             loc="left", fontweight="normal", fontsize=11, pad=10)
note(ax, "Exact recomputation of V-Dem's formula, index = ½·(product of the five components) + ½·(⅛ elected officials + ¼ clean elections + ¼ association\n"
         f"+ ⅛ suffrage + ¼ expression); it reproduces the published 2025 index at r = {K['formula_r']:.4f}. Morocco's multiparty ({K['MAR_mulpar']:.2f}) and free-and-fair "
         f"({K['MAR_frfair_osp']:.2f})\nelection indicators already clear the RoW threshold of 2. Source: V-Dem v16.", y=-0.24)
save(fig, "F24_waterfall")

# ============================================================ F25  schooling vs opportunity
cc = pd.read_csv(os.path.join(OUT, "campante_chor.csv")).set_index("iso3")
un = pd.read_csv(os.path.join(OUT, "educated_unemployment.csv")).set_index("iso3")
gd = p[p.year.between(2019, 2024)].groupby("iso3").gdppc_ppp21.mean()
fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7))
a = axes[0]
o = cc[cc.mena == 0]; mn = cc[(cc.mena == 1) & (cc.index != "MAR")]
a.scatter(o.dmys, o.dlgdp, s=16, c=NEUT, edgecolors="none")
a.scatter(mn.dmys, mn.dlgdp, s=26, c=ORANGE, edgecolors="none")
xx = np.linspace(cc.dmys.min(), cc.dmys.max(), 50)
a.plot(xx, cc.dlgdp.mean() + K["cc_slope"] * (xx - cc.dmys.mean()), color=INK2, lw=1.0, ls=(0, (4, 2)))
boxes_a = []
r = cc.loc["MAR"]
a.scatter(r.dmys, r.dlgdp, s=120, marker="D", c=BLUE, edgecolors="white", linewidths=1.4, zorder=5)
reserve_point(a, (r.dmys, r.dlgdp), boxes_a, r=10)
reserve(halo(a.annotate("Morocco", xy=(r.dmys, r.dlgdp), xytext=(7, -10), textcoords="offset points",
                        fontsize=8.8, fontweight="bold", color=BLUE, zorder=6)), boxes_a, pad=2.5)
for iso in mn.index:
    if iso in ("TUN", "EGY", "JOR", "DZA", "SYR", "LBN", "SAU", "IRN", "YEM", "IRQ", "LBY"):
        halo(place_label(a, (mn.loc[iso, "dmys"], mn.loc[iso, "dlgdp"]), NAME.get(iso, iso), boxes_a,
                         fontsize=7, color=ORANGE, zorder=4), lw=2.2)
a.axhline(0, color=INK2, lw=0.5)
a.set_xlabel("Change in mean years of schooling, adults 25+, 2000–2020"); a.set_ylabel("Change in log GDP per capita (PPP), 2000–2020")
a.grid(True); a.set_axisbelow(True)
a.set_title("$\\bf{a.}$  Schooling growth vs income growth", loc="left", fontweight="normal")
b = axes[1]
u = un.join(gd.rename("gdp")).dropna(subset=["gdp"])
um = u[u.mena == 1]
b.scatter(np.log(u.gdp), u.ratio, s=16, c=NEUT, edgecolors="none")
b.scatter(np.log(um.gdp), um.ratio, s=26, c=ORANGE, edgecolors="none")
SHORT = {"ARE": "UAE", "PSE": "Palestine", "SAU": "Saudi Arabia"}
OFFB = {"TUN": (5, 5), "JOR": (-5, -9), "IRN": (5, 2), "IRQ": (5, -7), "ARE": (5, -2), "EGY": (5, 2), "OMN": (5, 0),
        "QAT": (5, 0), "SAU": (5, 0), "ISR": (5, 0), "PSE": (5, 0), "DJI": (5, 0), "LBN": (-6, -10)}
boxes_b = []
r = u.loc["MAR"]
b.scatter(np.log(r.gdp), r.ratio, s=120, marker="D", c=BLUE, edgecolors="white", linewidths=1.4, zorder=5)
reserve_point(b, (np.log(r.gdp), r.ratio), boxes_b, r=10)
reserve(halo(b.annotate(f"Morocco: graduates {r.ratio:.1f}× as likely\nto be unemployed as the least educated",
                        xy=(np.log(r.gdp), r.ratio), xytext=(np.log(3200), 13), textcoords="data",
                        fontsize=8.2, fontweight="bold", color=BLUE, ha="center", zorder=6,
                        arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8, shrinkB=7))), boxes_b, pad=2.5)
reserve_span(b, (np.log(3200), 13), (np.log(r.gdp), r.ratio), boxes_b, w=2.5)   # keep names off the leader
for iso in um.index:
    if iso != "MAR":
        dx, dy = OFFB.get(iso, (4, 2))
        halo(place_label(b, (np.log(um.loc[iso, "gdp"]), um.loc[iso, "ratio"]),
                         SHORT.get(iso, NAME.get(iso, iso)), boxes_b,
                         cands=[(dx, dy, "right" if dx < 0 else "left", "baseline")] + list(CANDIDATES),
                         fontsize=7, color=ORANGE, zorder=4), lw=2.2)
b.axhline(1, color=INK2, lw=0.8, ls=(0, (4, 2)))
b.annotate("equal unemployment", xy=(np.log(1100), 1.03), fontsize=7.4, color=MUTED)
tk = [1000, 3000, 10000, 30000, 100000]; b.set_xticks(np.log(tk)); b.set_xticklabels([f"{v:,}" for v in tk])
b.set_yscale("log"); b.set_yticks([0.125, 0.25, 0.5, 1, 2, 4, 8]); b.set_yticklabels(["⅛", "¼", "½", "1", "2", "4", "8"])
b.minorticks_off()
b.set_xlabel("GDP per capita, PPP 2021 $, 2019–24 average (log)"); b.set_ylabel("Unemployment rate, advanced ÷ basic education")
b.grid(True); b.set_axisbelow(True)
b.set_title("$\\bf{b.}$  The graduate squeeze", loc="left", fontweight="normal")
title(fig, "$\\bf{Figure\\ 25.}$  Campante & Chor revisited: Morocco's income kept pace with its schooling in aggregate —\n"
           "the squeeze is concentrated on graduates, as across the Middle East and North Africa", y=1.07)
note(a, f"Orange: Middle East & North Africa (World Bank). Dashed line: OLS fit across {K['cc_N']} countries. Sources: Wittgenstein Centre v3.3; World Bank WDI (ILO).", y=-0.15)
save(fig, "F25_schooling_opportunity")

# ============================================================ F26  the royal reference class
rd = pd.read_csv(os.path.join(OUT, "royal_democratisations.csv"))
fig, ax = plt.subplots(figsize=(8.6, 5.2))
rr = rd.dropna(subset=["mys", "gdppc_mad"])
ax.scatter(rr.mys, np.log(rr.gdppc_mad), s=48, c=ORANGE, edgecolors="white", linewidths=0.8, zorder=3)
OFF = {"DNK": (6, -3), "NOR": (6, -9), "NLD": (6, 2), "GBR": (-6, 5), "BEL": (6, -9), "SWE": (6, 3), "JPN": (6, -3),
       "ESP": (6, 3), "LSO": (6, -3), "THA": (6, -3), "MYS": (-6, -3)}
for _, r in rr.iterrows():
    dx, dy = OFF.get(r.iso3, (6, 0))
    ax.annotate(f"{r.country_name} {int(r.year)}", xy=(r.mys, np.log(r.gdppc_mad)), xytext=(dx, dy), textcoords="offset points",
                fontsize=7.8, color=INK2, ha="right" if dx < 0 else "left")
bt = rd[rd.iso3 == "BTN"].iloc[0]
ax.axvline(bt.mys, color=ORANGE, lw=0.8, ls=(0, (1, 2)))
ax.annotate(f"Bhutan 2009: {bt.mys:.1f} yrs,\n{bt.none_wcde:.0f}% unschooled\n(no Maddison GDP)", xy=(bt.mys, np.log(2300)), xytext=(4, 0),
            textcoords="offset points", fontsize=7.6, color=ORANGE)
mm = float(C[(C.ssp == 2) & (C.iso3 == "MAR") & (C.year == 2025) & (C.band == "25+") & (C.sex == "Both")].mys.iloc[0])
ax.scatter(mm, np.log(8400.1), s=260, marker="*", c=BLUE, edgecolors="white", linewidths=1.4, zorder=5)
ax.annotate(f"Morocco 2025\nmore schooled than {K['royal_pct_mys_below_MAR']:.0f}% and richer than\n{K['royal_pct_gdp_below_MAR']:.0f}% of these cases at their transition",
            xy=(mm, np.log(8400.1)), xytext=(10, 16), textcoords="offset points", fontsize=8.6, fontweight="bold", color=BLUE)
tk = [2000, 4000, 8000, 16000, 32000]; ax.set_yticks(np.log(tk)); ax.set_yticklabels([f"{v:,}" for v in tk])
ax.set_xlabel("Mean years of schooling at the transition"); ax.set_ylabel("GDP per capita at the transition (Maddison, 2011 $, log)")
ax.set_xlim(1.5, 13); ax.grid(True); ax.set_axisbelow(True)
ax.set_title("$\\bf{Figure\\ 26.}$  Every monarchy that became a democracy while keeping its monarch, 1900–2025:\n"
             "most did so poorer and less schooled than Morocco is today",
             loc="left", fontweight="normal", fontsize=11.2, pad=10)
note(ax, "First transition to electoral democracy (V-Dem RoW) with a hereditary head of state; Norway 1906 added by hand (king chosen by the Storting after a\n"
         "referendum). Luxembourg 1919 omitted (no credible schooling series). Mean years: WCDE 25+ from 1950; Lee & Lee (2016) long-run, ages 15–64, before.", y=-0.12)
save(fig, "F26_royal_reference_class")

# ============================================================ F27  Afrobarometer: Morocco's two electorates
cells = pd.read_csv(os.path.join(OUT, "afro_morocco_cells.csv"))
cells = cells[cells.Generation != "All"]
EDL = ["None/informal", "Primary", "Secondary", "Post-secondary"]
OUTS = [("Democracy always preferable", "a.  'Democracy is preferable to any\n     other kind of government'"),
        ("Rejects one-man rule", "b.  Rejects abolishing elections and\n     parliament for one-man rule"),
        ("Full demand for democracy", "c.  Full demand for democracy\n     (all four commitments)"),
        ("Voted in last election", "d.  Voted in the last\n     national election")]
fig, axes = plt.subplots(1, 4, figsize=(12.2, 4.0), sharey=True)
for ax, (col, ttl) in zip(axes, OUTS):
    for gen, c_, off in (("18–39", BLUE, -0.08), ("40+", ORANGE, 0.08)):
        d = cells[cells.Generation == gen].set_index("Schooling").reindex(EDL)
        pp = d[col].values / 100; n = d.N.values
        se = np.sqrt(pp * (1 - pp) / n) * 100 * 1.96
        ax.errorbar(np.arange(4) + off, d[col].values, yerr=se, color=c_, marker="o", ms=5, lw=1.8, capsize=0,
                    label=f"aged {gen}")
    ax.set_xticks(range(4)); ax.set_xticklabels(["None /\ninformal", "Primary", "Secondary", "Post-\nsecondary"], fontsize=7.8)
    ax.set_ylim(20, 95); ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_title(ttl, loc="left", fontweight="normal", fontsize=9)
axes[0].set_ylabel("% of respondents"); axes[0].legend(loc="lower left", fontsize=7.8)
title(fig, "$\\bf{Figure\\ 27.}$  In the survey data, schooling divides Moroccans on rejecting one-man rule — not on endorsing\n"
           "'democracy' in the abstract; once schooling is held constant, generation adds little", y=1.1)
note(axes[0], "Weighted shares with 95% intervals (cell N from 31 to 297). Source: Afrobarometer Round 9, Morocco 2022 (N = 1,200).", y=-0.24)
save(fig, "F27_afro_two_electorates")

# ============================================================ F28  Morocco among 39 African publics
g = pd.read_csv(os.path.join(OUT, "afro_country_gradients.csv"))
fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.4), gridspec_kw={"width_ratios": [1, 1.05]})
a = axes[0]
gg = g.sort_values("demand_edu").reset_index(drop=True)
for i, r in gg.iterrows():
    mar = r.iso3 == "MAR"
    a.plot([(r.demand_edu - 1.96 * r.demand_edu_se) * 100, (r.demand_edu + 1.96 * r.demand_edu_se) * 100], [i, i],
           color=BLUE if mar else NEUT, lw=1.6 if mar else 1.0)
    a.scatter(r.demand_edu * 100, i, s=46 if mar else 16, c=BLUE if mar else INK2, zorder=3, marker="D" if mar else "o")
a.set_yticks(range(len(gg))); a.set_yticklabels([("Morocco" if i_ == "MAR" else c_) for i_, c_ in zip(gg.iso3, gg.country)], fontsize=6.6)
for t_ in a.get_yticklabels():
    if t_.get_text() == "Morocco": t_.set_color(BLUE); t_.set_fontweight("bold")
a.axvline(0, color=INK2, lw=0.6); a.set_xlabel("Education gradient in full demand for democracy\n(no schooling to postgraduate, percentage points)")
a.set_title("$\\bf{a.}$  How much schooling raises democratic demand", loc="left", fontweight="normal")
b = axes[1]
b.scatter(g.demand_mean * 100, g.polyarchy_2022, s=22, c=NEUT, edgecolors="none")
for _, r in g.iterrows():
    if r.iso3 in ("TUN", "SEN", "GHA", "ZAF", "MUS", "SDN", "ETH", "SWZ", "CPV", "MLI", "NGA", "KEN", "BWA"):
        b.annotate(r.country, xy=(r.demand_mean * 100, r.polyarchy_2022), xytext=(4, 2), textcoords="offset points", fontsize=7, color=INK2)
r = g[g.iso3 == "MAR"].iloc[0]
b.scatter(r.demand_mean * 100, r.polyarchy_2022, s=120, marker="D", c=BLUE, edgecolors="white", linewidths=1.4, zorder=5)
b.annotate("Morocco\naverage demand, low supply", xy=(r.demand_mean * 100, r.polyarchy_2022), xytext=(-10, -26),
           textcoords="offset points", fontsize=8.4, fontweight="bold", color=BLUE, ha="right")
b.set_xlabel("Demand: % with full demand for democracy (Afrobarometer R9)"); b.set_ylabel("Supply: V-Dem electoral democracy index, 2022")
b.grid(True); b.set_axisbelow(True)
b.set_title("$\\bf{b.}$  Demand for and supply of democracy", loc="left", fontweight="normal")
title(fig, "$\\bf{Figure\\ 28.}$  Morocco among 39 African publics: an ordinary education gradient and ordinary democratic demand,\n"
           "met by one of the lowest supplies of democracy in the sample", y=1.06)
note(a, "Panel a: weighted LPM of full demand (DemandDemo = 4) on education (0–9 scale rescaled to 0–1), age < 40, sex and urban, country by country; 95% CIs.\n"
        "Sources: Afrobarometer Round 9 (2021–23); V-Dem v16.", y=-0.17)
save(fig, "F28_afro_comparative")
print("F13-F28 done")
