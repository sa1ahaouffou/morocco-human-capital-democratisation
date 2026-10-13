"""
18_figures_urban_rural.py -- Figures 29-32: the urban/rural divergence.

Reads   data/clean/ext/commune_panel.csv.gz, province_elections.csv.gz,
        key_numbers_urbanrural.json, tables/T33-T38
Writes  figures/F29-F32 (pdf + png), in the house style of fab_style.py
"""
import os, json, sys
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fab_style import *          # noqa: F401,F403
from tiers import tier_dir, tpath
apply()

OUT = os.path.join(HERE, "..", "data", "clean", "ext")
FIG = os.path.join(HERE, "..", "figures"); TAB = os.path.join(HERE, "..", "tables")
P = pd.read_csv(os.path.join(OUT, "commune_panel.csv.gz"))
L = pd.read_csv(os.path.join(OUT, "province_elections.csv.gz"))
K = json.load(open(os.path.join(OUT, "key_numbers_urbanrural.json")))
T33 = pd.read_csv(tpath(TAB, "T33_two_populations", "csv"))
T34 = pd.read_csv(tpath(TAB, "T34_four_corners", "csv"))
T37 = pd.read_csv(tpath(TAB, "T37_schooling_deciles", "csv"))
T38 = pd.read_csv(tpath(TAB, "T38_who_is_elected", "csv"))



def save(fig, n):
    for e in ("pdf", "png"):
        fig.savefig(os.path.join(tier_dir(FIG, n), f"{n}.{e}"))
    plt.close(fig); print("  wrote", n)


def note(ax, s, y=-0.19, x=0.0):
    ax.annotate(s, xy=(x, y), xycoords="axes fraction", fontsize=7.4, color=MUTED, va="top", ha="left")


# ============================================================ F29  the two populations
fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.4), gridspec_kw={"width_ratios": [1.15, 1]})

LEV = ["No schooling at all", "Primary", "Lower secondary", "Upper secondary", "Higher education"]
RAMP = [LEVELS["none"], LEVELS["pri"], LEVELS["losec"], LEVELS["upsec"], LEVELS["post"]]
rows = T33.set_index("Indicator").loc[LEV]
for i, (milieu, col) in enumerate([("Rural", "Rural"), ("Urban", "Urban")]):
    left = 0
    for lev, c in zip(LEV, RAMP):
        v = rows.loc[lev, col]
        a.barh(i, v, left=left, color=c, edgecolor="white", linewidth=0.8, height=0.52)
        if v > 5:
            a.text(left + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=8.4,
                   color="white" if lev in LEV[:2] else INK, fontweight="bold")
        left += v
a.set_yticks([0, 1]); a.set_yticklabels(["Rural\nMorocco", "Urban\nMorocco"], fontsize=9.5)
a.set_ylim(-0.55, 1.55)
a.set_xlim(0, 100); a.set_xlabel("% of the adult population")
a.set_title("$\\bf{a.}$  One country, two education structures", loc="left")
a.legend(handles=[Patch(facecolor=c, label=l) for l, c in zip(LEV, RAMP)],
         loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=8.2)
a.spines["left"].set_visible(False); a.tick_params(axis="y", length=0)

y = np.arange(len(T34))[::-1]
b.barh(y, T34["No schooling"], color=[NEUT, "#B5706F", FAB, FAB_DARK], height=0.56,
       edgecolor="white", linewidth=0.8)
for yy, v, lab in zip(y, T34["No schooling"], T34["Population"]):
    b.text(v + 1, yy, f"{v:.0f}%", va="center", fontsize=8.6, color=INK2)
b.set_yticks(y); b.set_yticklabels(T34["Population"], fontsize=9)
b.set_xlim(0, 72); b.set_xlabel("% who never went to school")
b.set_title("$\\bf{b.}$  The distance runs from urban men to rural women", loc="left")
b.spines["left"].set_visible(False); b.tick_params(axis="y", length=0)
b.annotate(f"{K['none_rural_women']:.0f}% against {K['none_urban_men']:.0f}%:\na factor of "
           f"{K['none_rural_women']/K['none_urban_men']:.1f}",
           xy=(T34["No schooling"].iloc[3], 0), xytext=(43, 2.5), fontsize=8.6, color=FAB,
           fontweight="bold", ha="left",
           arrowprops=dict(arrowstyle="-", color=FAB, lw=0.8, shrinkA=0, shrinkB=6))
note(a, "Source: RGPH 2014 (Haut-Commissariat au Plan), commune tables compiled by Tafra; "
        "each stratum weighted by its adult population.", y=-0.42)
fig.suptitle("$\\bf{Figure\\ 29.}$  Morocco's second divergence: where you live decides how much school you had",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.02)
fig.tight_layout(); save(fig, "F29_two_populations")

# ============================================================ F30  turnout against schooling, 1,538 communes
fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6), sharey=True)
for ax, yr in zip(axes, (2015, 2021)):
    d = P.dropna(subset=[f"txParticipation_{yr}", "eduNo"]).copy()
    d["x"] = 100 * d.eduNo; d["y"] = 100 * d[f"txParticipation_{yr}"]
    urb = d.milieu == "urbain"
    ax.scatter(d.loc[~urb, "x"], d.loc[~urb, "y"], s=9, color=NEUT, alpha=.75, lw=0, label="rural / mixed commune")
    ax.scatter(d.loc[urb, "x"], d.loc[urb, "y"], s=14, color=FAB, alpha=.85, lw=0, label="urban commune")
    z = np.polyfit(d.x, d.y, 1); xs = np.linspace(d.x.min(), d.x.max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=INK, lw=1.2, ls="--")
    r = d[["x", "y"]].corr().iloc[0, 1]
    ax.annotate(f"slope {z[0]:+.2f} points of turnout\nper point of no schooling   (r = {r:.2f})",
                xy=(0.03, 0.05), xycoords="axes fraction", fontsize=8.4, color=INK, va="bottom")
    for nm, dx, dy in [("Casablanca", -6, 7), ("Rabat", 5, -10), ("Marrakech", 5, 6)]:
        s = d[d.commune.astype(str).str.startswith(nm)]
        if len(s):
            s = s.nlargest(1, "popLegale").iloc[0]
            ax.annotate(nm, xy=(s.x, s.y), xytext=(dx, dy), textcoords="offset points",
                        fontsize=7.8, color=FAB_DARK,
                        ha="right" if dx < 0 else "left")
    ax.set_title(f"$\\bf{{{'a' if yr == 2015 else 'b'}.}}$  Communal election {yr}", loc="left")
    ax.set_xlabel("% of the commune's adults who never went to school")
axes[0].set_ylabel("turnout (%)")
axes[0].legend(loc="upper left", fontsize=8.4)
note(axes[0], "Each dot is one of the 1,538 communes. Turnout: Tafra from the Ministry of the Interior; "
              "schooling: RGPH 2014. Dashed line: OLS.", y=-0.19)
fig.suptitle("$\\bf{Figure\\ 30.}$  The less a commune went to school, the more of it turns out to vote",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.0)
fig.tight_layout(); save(fig, "F30_turnout_schooling")

# ============================================================ F31  the gap at every election
fig, ax = plt.subplots(figsize=(9.4, 5.0))
T35 = pd.read_csv(tpath(TAB, "T35_turnout_every_election", "csv"))
T35["yr"] = T35.Election.str.extract(r"(\d{4})").astype(int)
T35["kind"] = np.where(T35.Election.str.startswith("Legislative"), "Legislative", "Communal")
for kind, ls, mk in [("Legislative", "-", "o"), ("Communal", "--", "s")]:
    s = T35[T35.kind == kind].sort_values("yr")
    ax.plot(s.yr, s["Rural turnout"], ls=ls, marker=mk, ms=5, color=FAB, lw=1.5,
            label=f"{kind}: rural provinces")
    ax.plot(s.yr, s["Urban turnout"], ls=ls, marker=mk, ms=5, color=INK2, lw=1.5, mfc="white",
            label=f"{kind}: urban provinces")
    for _, r in s.iterrows():
        ax.annotate(f"{r['Gap (pp)']:.0f}", xy=(r.yr + (0.45 if kind == "Communal" else -0.45),
                                 (r["Rural turnout"] + r["Urban turnout"]) / 2),
                    fontsize=7.6, color=MUTED, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
ax.scatter([2026], [38.0], marker="*", s=150, color=FAB_DARK, zorder=6)
ax.annotate("23 September 2026\nnational turnout 38.0%\n(no breakdown published yet)",
            xy=(2026, 38.0), xytext=(2022.3, 25.5), fontsize=8.4, color=FAB_DARK, ha="left",
            arrowprops=dict(arrowstyle="-", color=FAB_DARK, lw=0.8, shrinkA=0, shrinkB=8))
ax.set_xlabel("year"); ax.set_ylabel("turnout (%)"); ax.set_ylim(18, 72)
ax.grid(axis="y", alpha=.6); ax.set_axisbelow(True)
ax.legend(loc="upper right", ncol=1, fontsize=8.4, frameon=False)
ax.set_title("$\\bf{Figure\\ 31.}$  Rural provinces have out-voted urban ones at every election since 2002\n"
             "the number between the lines is the gap, in points", loc="left", fontsize=11.5, pad=10)
note(ax, "Provinces are classed urban when most adults live in town (RGPH 2014); turnout weighted by population. "
         "2002 and 2007 constituencies matched to 2014 provinces by name.\n"
         "Sources: Tafra; Ministry of the Interior for the 2026 national figure.", y=-0.15)
fig.tight_layout(); save(fig, "F31_turnout_every_election")

# ============================================================ F32  deciles and who gets elected
fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
x = T37["Decile of communes by % with no schooling"]
a.plot(x, T37["Turnout 2021"], marker="o", ms=5, color=FAB, lw=1.6, label="communal 2021")
a.plot(x, T37["Turnout 2015"], marker="s", ms=4.5, color=INK2, lw=1.4, ls="--", mfc="white",
       label="communal 2015")
a2 = a.twinx()
a2.bar(x, T37["% no schooling"], color=NEUT, alpha=.35, width=.6, zorder=0)
a2.set_ylabel("% with no schooling (bars)", color=MUTED, fontsize=9)
a2.tick_params(axis="y", colors=MUTED); a2.set_ylim(0, 100); a2.spines["right"].set_visible(True)
a2.spines["right"].set_color(NEUT)
a.set_zorder(a2.get_zorder() + 1); a.patch.set_visible(False)
a.set_xticks(x)
a.set_xlabel("decile of communes by the share of adults with no schooling\n(1 = best schooled, almost all urban   →   10 = least schooled, almost all rural)")
a.set_ylabel("turnout (%)"); a.legend(loc="upper left", fontsize=8.4)
a.set_title("$\\bf{a.}$  Turnout rises with every step away from school", loc="left")
a.annotate(f"{K['dec10_turnout21']:.0f}%", xy=(10, K["dec10_turnout21"]), xytext=(0, 8),
           textcoords="offset points", ha="center", fontsize=8.6, color=FAB, fontweight="bold")
a.annotate(f"{K['dec1_turnout21']:.0f}%", xy=(1, K["dec1_turnout21"]), xytext=(0, -14),
           textcoords="offset points", ha="center", fontsize=8.6, color=FAB, fontweight="bold")

w = 0.36; yy = np.arange(len(T38))
b.barh(yy - w/2, T38["Adults with no schooling"], height=w, color=FAB, label="adults with no schooling")
b.barh(yy + w/2, T38["Councillors with higher education"], height=w, color="#B9AE9C",
       label="councillors with higher education")
for i, r in T38.iterrows():
    b.text(r["Adults with no schooling"] + 1, i - w/2, f"{r['Adults with no schooling']:.0f}%",
           va="center", fontsize=8.2, color=INK2)
    b.text(r["Councillors with higher education"] + 1, i + w/2,
           f"{r['Councillors with higher education']:.0f}%", va="center", fontsize=8.2, color=INK2)
b.set_yticks(yy); b.set_yticklabels(T38["Communes"], fontsize=9); b.invert_yaxis()
b.set_xlabel("% "); b.set_xlim(0, 70)
b.legend(loc="lower right", fontsize=8.2)
b.set_title("$\\bf{b.}$  Who is elected, 2021", loc="left")
b.spines["left"].set_visible(False); b.tick_params(axis="y", length=0)
note(a, "Deciles of the 1,538 communes by the share of adults with no schooling, population-weighted. "
        "Sources: Tafra; RGPH 2014.", y=-0.2)
fig.suptitle("$\\bf{Figure\\ 32.}$  The schooled abstain, and the councils they stay away from are the schooled ones",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.02)
fig.tight_layout(); save(fig, "F32_deciles_and_elected")
print("F29-F32 done")
