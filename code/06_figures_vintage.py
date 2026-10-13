"""
06_figures_vintage.py -- Figures 11-12: dataset reconciliation and the cohort finding.
Palette: same validated reference instance as 04_figures.py.
"""
import os, json
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE=os.path.dirname(os.path.abspath(__file__))
CLEAN=os.path.join(HERE,"..","data","clean"); FIG=os.path.join(HERE,"..","figures")
# ---- house style: FAB burgundy, Times New Roman (see fab_style.py) ----
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fab_style import *
from tiers import tier_dir
apply()

def save(fig,n):
    for e in ("pdf","png"): fig.savefig(os.path.join(tier_dir(FIG, n),f"{n}.{e}"))
    plt.close(fig); print("  wrote",n)
def note(ax,s,y=-0.19):
    ax.annotate(s, xy=(0,y), xycoords="axes fraction", fontsize=7.4, color=MUTED, va="top", ha="left")

cmp15=pd.read_csv(os.path.join(CLEAN,"source_compare_2015.csv"))
M    =pd.read_csv(os.path.join(CLEAN,"morocco_by_source.csv"))
w    =pd.read_csv(os.path.join(CLEAN,"wcde.csv"))
ts   =pd.read_csv(os.path.join(CLEAN,"transitions_wcde.csv"))
p    =pd.read_csv(os.path.join(CLEAN,"panel.csv"))
coh  =w[(w.iso3=="MAR")&(w.year==2025)].set_index("age")

# ================================================= F11  dataset reconciliation
fig, ax = plt.subplots(1,2, figsize=(10.6,4.6))

a=ax[0]
a.plot([0,95],[0,95], color=NEUT, lw=1.2, zorder=1)
o=cmp15[cmp15.iso3!="MAR"]
a.scatter(o.lu_mf, o.noed, s=20, c=NEUT, edgecolors="none", zorder=2)
r=cmp15[cmp15.iso3=="MAR"].iloc[0]
a.scatter([r.lu_mf],[r.noed], s=130, c=BLUE, marker="D", edgecolors="white", linewidths=1.5, zorder=4)
a.annotate("Morocco", xy=(r.lu_mf,r.noed), xytext=(-9,2), textcoords="offset points",
           fontsize=9, fontweight="bold", color=BLUE, ha="right")
rho=cmp15[["lu_mf","noed"]].corr().iloc[0,1]
a.annotate(f"r = {rho:.2f}\nmean |difference| = {(cmp15.lu_mf-cmp15.noed).abs().mean():.1f} pp\nN = {len(cmp15)} countries",
           xy=(0.04,0.96), xycoords="axes fraction", va="top", fontsize=8.4, color=INK2)
a.set_xlabel("Barro-Lee v3, ages 25–64 (%)"); a.set_ylabel("Wittgenstein Centre v3, ages 25+ (%)")
a.set_xlim(-2,95); a.set_ylim(-2,95); a.grid(True); a.set_axisbelow(True)
a.set_title("$\\bf{a.}$  The two reconstructions agree\n     adults with no schooling, 2015", loc="left", fontweight="normal")

b=ax[1]
wm=w[(w.iso3=="MAR")&(w.age=="25+")&(w.year.between(1990,2025))].sort_values("year")
b.plot(wm.year, wm.mys, color=BLUE, lw=2.2, zorder=3)
wmid = wm[wm.year==2005].iloc[0]
b.annotate("Wittgenstein v3\n(25+, modelled 1950–2025)", xy=(wmid.year, wmid.mys), xytext=(6,-30),
           textcoords="offset points", fontsize=8, color=BLUE, fontweight="bold", ha="left")
pts=[("Barro-Lee v3\n25–64",2015,5.109),("UNESCO UIS\n25+ (survey)",2017,4.943),
     ("UNDP HDR\n25+",2023,6.198),("HCP census\nRGPH 2024, 25+",2024,6.300)]
offs=[(-8,10),(6,-22),(-10,12),(7,-6)]
for (lab,y,v),(dx,dy) in zip(pts,offs):
    b.scatter([y],[v], s=62, c=ORANGE, edgecolors="white", linewidths=1.3, zorder=5)
    b.annotate(lab, xy=(y,v), xytext=(dx,dy), textcoords="offset points", fontsize=7.6,
               color=ORANGE, fontweight="bold", ha="right" if dx<0 else "left")
b.set_xlabel("Year"); b.set_ylabel("Mean years of schooling, adults")
b.set_xlim(1990,2029); b.set_ylim(2.5,7.5); b.grid(axis="y"); b.set_axisbelow(True)
b.set_title("$\\bf{b.}$  …and every source converges on ~6 years today\n     Morocco, mean years of schooling", loc="left", fontweight="normal")
fig.suptitle("$\\bf{Figure\\ 11.}$  Is the answer an artefact of old data?  No.",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.04)
note(a, "Barro-Lee stops in 2015; the Wittgenstein Centre reconstructs and projects the same attainment distribution to 2025 and beyond.\n"
        "Sources: Barro-Lee v3 (2021); Wittgenstein Centre WCDE v3.3 (SSP2); UNESCO UIS (Feb-2026 release); UNDP HDR; HCP, RGPH 2024.", y=-0.20)
save(fig,"F11_source_reconciliation")

# ================================================= F12  the cohort finding
fig, ax = plt.subplots(figsize=(9.0,5.9))
s=ts["w_noed"].dropna()
bins=np.linspace(0, max(s.max(), 95), 28)
ax.hist(s, bins=bins, color=NEUT, edgecolor="white", linewidth=0.8, zorder=2)
ymax=ax.get_ylim()[1]; ax.set_ylim(0, ymax*1.42)

marks=[("40--64", "Moroccans aged 40–64",  ORANGE, 1.28),
       ("25+",    "ALL Moroccan adults 25+", BLUE,  1.05),
       ("20--39", "Moroccans aged 20–39",  AQUA,   0.82)]
for age,lab,col,h in marks:
    v=float(coh.loc[age,"noed"]); pct=(s<v).mean()*100
    ax.axvline(v, color=col, lw=2.4, zorder=5)
    ax.annotate(f"{lab}\n{v:.0f}%  ·  {pct:.0f}th percentile",
                xy=(v, ymax*h), xytext=(8,0), textcoords="offset points",
                fontsize=8.8, fontweight="bold", color=col, va="top", zorder=6)
ax.annotate("Vintage check:  Barro-Lee's 2015 snapshot put all Moroccan adults\n"
            "at 42 %  (80th percentile).  Ten years of data revision and cohort\n"
            "turnover move that to 34 %  (72nd).  The verdict does not turn on it.",
            xy=(0.985, 0.60), xycoords="axes fraction", ha="right", va="top",
            fontsize=7.8, color=MUTED, linespacing=1.5, zorder=6)
ax.set_xlabel("Share of adults with no schooling at all, in the year of transition (%)")
ax.set_ylabel("number of democratic transitions")
ax.grid(axis="y"); ax.set_axisbelow(True)
ax.set_title("$\\bf{Figure\\ 12.}$  Morocco does not have one electorate — it has two\n"
             "Moroccans today placed in the distribution of 138 democratic transitions, 1960–2025",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Morocco's under-40s are better schooled than roughly six of every ten countries at the moment they democratised; its over-40s are worse\n"
         "schooled than four of every five. Attainment for all countries and all years on one source (Wittgenstein Centre WCDE v3.3, SSP2, ages as shown).", y=-0.135)
save(fig,"F12_two_electorates")
