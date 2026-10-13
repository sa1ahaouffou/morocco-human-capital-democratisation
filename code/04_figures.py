"""
04_figures.py -- Figures for the Morocco democratization gap analysis.
Palette: validated reference instance (slots 1-3 clear the all-pairs CVD gates).
"""
import os, json
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from statsmodels.nonparametric.smoothers_lowess import lowess

HERE=os.path.dirname(os.path.abspath(__file__))
CLEAN=os.path.join(HERE,"..","data","clean"); FIG=os.path.join(HERE,"..","figures")
os.makedirs(FIG, exist_ok=True)
p=pd.read_csv(os.path.join(CLEAN,"panel.csv")); t=pd.read_csv(os.path.join(CLEAN,"transitions.csv"))
xs=pd.read_csv(os.path.join(CLEAN,"crosssection.csv"))
K=json.load(open(os.path.join(CLEAN,"key_numbers.json")))

# ---- house style: FAB burgundy, Times New Roman (see fab_style.py) ----
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fab_style import *
apply()

def save(fig, name):
    for ext in ("pdf","png"): fig.savefig(os.path.join(FIG,f"{name}.{ext}"))
    plt.close(fig); print("  wrote", name)

def note(ax, s, y=-0.19):
    ax.annotate(s, xy=(0,y), xycoords="axes fraction", fontsize=7.4, color=MUTED, va="top", ha="left")

NAME = p.dropna(subset=["country"]).drop_duplicates("iso3").set_index("iso3")["country"].to_dict()

# ============================================================ F1  modernization cloud
c = xs.set_index("iso3")
fig, axes = plt.subplots(1,2, figsize=(10.4,4.3))
LBLS = ["KOR","VNM","TWN","TUN","EGY","DZA","JOR","TUR","IDN","CHL","ESP","PRT","IND","SEN","GHA","SAU","CHN","BRA","MEX"]
for ax, (xv, xlab, logx) in zip(axes, [("gdp","GDP per capita, PPP (constant 2021 int$), 2019\u201323 avg", True),
                                       ("mys","Mean years of schooling, adults, 2019\u201323 avg", False)]):
    d = c.dropna(subset=[xv,"electdem"])
    X = np.log(d[xv]) if logx else d[xv]
    ax.scatter(X, d.electdem, s=17, c=NEUT, edgecolors="none", zorder=2)
    lo = lowess(d.electdem, X, frac=0.62, it=3, return_sorted=True)
    keep = (lo[:,0] >= np.percentile(X,3)) & (lo[:,0] <= np.percentile(X,97))   # avoid boundary overshoot
    lo = lo[keep]
    ax.plot(lo[:,0], lo[:,1], color=ORANGE, lw=2, zorder=3)
    # the frame must be final before any label is measured: place_label works in display space
    if logx:
        tk=[1000,3000,10000,30000,100000]; ax.set_xticks(np.log(tk)); ax.set_xticklabels([f"{v:,}" for v in tk])
    ax.set_xlabel(xlab); ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_ylim(-0.03,1.0); ax.set_xlim(*ax.get_xlim())
    boxes = []
    # Morocco is placed first and keeps its position; every other label moves around it
    xm = np.log(d.loc["MAR",xv]) if logx else d.loc["MAR",xv]; ym = d.loc["MAR","electdem"]
    ax.scatter([xm],[ym], s=115, c=BLUE, edgecolors="white", linewidths=1.6, zorder=6, marker="D")
    reserve_point(ax, (xm,ym), boxes, r=9.5)
    reserve(halo(ax.annotate("Morocco", xy=(xm,ym), xytext=(-12,-13), textcoords="offset points",
                             fontsize=9.6, fontweight="bold", color=BLUE, ha="right", zorder=8)), boxes, pad=2.5)
    reserve(ax.annotate("cross-country\ntrend", xy=(lo[int(len(lo)*0.80),0], lo[int(len(lo)*0.80),1]),
                        xytext=(6,-20), textcoords="offset points", color=ORANGE, fontsize=8,
                        fontweight="bold", zorder=5), boxes)
    for iso in sorted([i for i in LBLS if i in d.index], key=lambda i: -d.loc[i,"electdem"]):
        xi = np.log(d.loc[iso,xv]) if logx else d.loc[iso,xv]; yi = d.loc[iso,"electdem"]
        ax.scatter(xi, yi, s=19, c=INK2, edgecolors="none", zorder=4)
        halo(place_label(ax, (xi,yi), NAME.get(iso,iso), boxes,
                         fontsize=7.3, color=INK2, zorder=5), lw=2.2)
axes[0].set_ylabel("V-Dem electoral democracy index (0\u20131)")
axes[0].set_title("$\\bf{a.}$  Democracy and income", loc="left", fontweight="normal")
axes[1].set_title("$\\bf{b.}$  Democracy and schooling", loc="left", fontweight="normal")
fig.suptitle("$\\bf{Figure\\ 1.}$  Morocco is poorer in democracy than in either income or schooling",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.035)
note(axes[0], "Countries with population > 1 million. Sources: V-Dem v15 via Our World in Data; World Bank WDI; Barro-Lee v3 / UNDP.", y=-0.20)
save(fig,"F1_modernization_cloud")

# ============================================================ F2  the transition cloud
ts = t[(t.year>=1960)].dropna(subset=["gdppc_mad","mys"]).copy()
MG=K["MAR_gdppc_mad"][1]; MM=K["MAR_mys"][1]
fig, ax = plt.subplots(figsize=(8.6,6.0))
ax.axvline(np.log(ts.gdppc_mad.median()), color=GRID, lw=1.0, zorder=1)
ax.axhline(ts.mys.median(), color=GRID, lw=1.0, zorder=1)
ax.scatter(np.log(ts.gdppc_mad), ts.mys, s=30, c=NEUT, edgecolors="none", zorder=2)
show={"PRT":(1976,"Portugal 1976"),"ESP":(1978,"Spain 1978"),"KOR":(1988,"S. Korea 1988"),"TWN":(1996,"Taiwan 1996"),
      "POL":(1990,"Poland 1990"),"CHL":(1990,"Chile 1990"),"BRA":(1987,"Brazil 1987"),"IDN":(1999,"Indonesia 1999"),
      "TUN":(2012,"Tunisia 2012"),"SEN":(1990,"Senegal 1990"),"MLI":(1993,"Mali 1993"),"BEN":(1992,"Benin 1992"),
      "GHA":(1996,"Ghana 1996"),"TUR":(1990,"Türkiye 1990"),"MEX":(1996,"Mexico 1996"),"ZAF":(1995,"S. Africa 1995"),
      "MNG":(1991,"Mongolia 1991"),"PHL":(1988,"Philippines 1988")}
# preferred position for each label; place_label falls back to the standard ring if it collides
off={"PRT":(8,-4),"ESP":(8,-3),"KOR":(7,5),"TWN":(8,-12),"POL":(7,5),"CHL":(8,5),"BRA":(-7,5),"IDN":(7,5),
     "TUN":(8,6),"SEN":(7,-4),"MLI":(7,2),"BEN":(7,-10),"GHA":(7,5),"TUR":(7,-12),"MEX":(8,-13),"ZAF":(7,-13),
     "MNG":(7,5),"PHL":(7,5)}
ha_ ={"BRA":"right"}
tk=[500,1000,2000,5000,10000,20000,40000]; ax.set_xticks(np.log(tk)); ax.set_xticklabels([f"{v:,}" for v in tk])
ax.set_xlabel("GDP per capita in the year of transition (Maddison, 2011 int$, log scale)")
ax.set_ylabel("Mean years of schooling, adults, in the year of transition")
ax.grid(axis="y"); ax.set_axisbelow(True)
ax.set_xlim(*ax.get_xlim()); ax.set_ylim(*ax.get_ylim())

# --- Morocco first, so the cloud's labels are placed around it rather than over it
boxes=[]
# the national average AND the under-40 cohort at the same income (WCDE v3, 2025)
try:
    _w = pd.read_csv(os.path.join(CLEAN,"wcde.csv"))
    MY = float(_w[(_w.iso3=="MAR")&(_w.year==2025)&(_w.age=="20--39")].mys.iloc[0])
except Exception:
    MY = None
ax.scatter([np.log(MG)],[MM], s=230, marker="*", c=BLUE, edgecolors="white", linewidths=1.4, zorder=6)
reserve_point(ax, (np.log(MG), MM), boxes, r=10)
reserve(halo(ax.annotate("Morocco today, all adults\n$8,400 and 6.2 years of schooling",
                         xy=(np.log(MG),MM), xytext=(-20,-7), textcoords="offset points",
                         fontsize=9.0, fontweight="bold", color=BLUE, ha="right", va="center",
                         linespacing=1.5, zorder=7)), boxes, pad=2.5)
if MY:
    ax.annotate("", xy=(np.log(MG),MY), xytext=(np.log(MG),MM),
                arrowprops=dict(arrowstyle="->", color=AQUA, lw=1.6), zorder=6)
    reserve_span(ax, (np.log(MG),MM), (np.log(MG),MY), boxes, w=3.5)
    ax.scatter([np.log(MG)],[MY], s=230, marker="*", c=AQUA, edgecolors="white", linewidths=1.4, zorder=7)
    reserve_point(ax, (np.log(MG), MY), boxes, r=10)
    reserve(halo(ax.annotate(f"Moroccans aged 20–39: {MY:.1f} years,\nbetter schooled than 76 % of all\ncountries at their own transition",
                             xy=(np.log(MG),MY), xytext=(-22,6), textcoords="offset points",
                             fontsize=9.0, fontweight="bold", color=AQUA, ha="right", va="center",
                             linespacing=1.5, zorder=8)), boxes, pad=2.5)
# --- the two reference lines, labelled clear of the cloud
reserve(halo(ax.annotate(f"median income\n${ts.gdppc_mad.median():,.0f}", xy=(np.log(ts.gdppc_mad.median()),0.4),
                         xytext=(4,0), textcoords="offset points", fontsize=7.6, color=INK2, zorder=5)), boxes)
reserve(halo(ax.annotate(f"median schooling: {ts.mys.median():.1f} yrs", xy=(np.log(560), ts.mys.median()),
                         xytext=(0,5), textcoords="offset points", fontsize=7.6, color=INK2, zorder=5)), boxes)
# --- the benchmark transitions
for iso,(yr,lab) in show.items():
    r=ts[(ts.iso3==iso)&(ts.year==yr)]
    if not len(r): continue
    r=r.iloc[0]; hi = iso in ("ESP","PRT","KOR","TWN")
    ax.scatter(np.log(r.gdppc_mad), r.mys, s=44 if hi else 32, c=ORANGE if hi else INK2, edgecolors="none", zorder=4)
    cands = [(off[iso][0], off[iso][1], ha_.get(iso,"left"), "baseline")] + list(CANDIDATES)
    halo(place_label(ax, (np.log(r.gdppc_mad), r.mys), lab, boxes, cands=cands,
                     fontsize=7.8, color=ORANGE if hi else INK2,
                     fontweight="bold" if hi else "normal", zorder=5), lw=2.2)
ax.set_title(f"$\\bf{{Figure\\ 2.}}$  Morocco already exceeds the typical country at the moment it democratised —\n"
             f"and its under-40s sit where South Korea and Poland did.  {len(ts)} transitions, 1960–2025",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Each dot is one transition from autocracy to electoral democracy (V-Dem Regimes of the World). Highlighted: the four 'third wave' cases most often\n"
         "compared with Morocco. The second Moroccan marker holds income fixed and replaces the adult stock with the 20–39 cohort\n(Wittgenstein Centre v3.3, 2025). Sources: V-Dem v15; Maddison Project 2023; Barro-Lee v3 (ages 25–64) / UNDP.", y=-0.135)
save(fig,"F2_transition_cloud")
print("F1-F2 done")

# ============================================================ F3  where Morocco sits in the transition distribution
tsa = t[t.year>=1960]
panels=[("gdppc_mad","GDP per capita at transition (2011 int$)", K["MAR_gdppc_mad"][1], True,  "Morocco is RICHER than %.0f%% of them"),
        ("mys",      "Mean years of schooling at transition",    K["MAR_mys"][1],       False, "Morocco is MORE schooled than %.0f%% of them"),
        ("lu_mf",    "% of adults with NO schooling at transition", K["MAR_lu_mf"][1],  False, "Morocco has a LARGER unschooled mass than %.0f%% of them")]
fig, axes = plt.subplots(3,1, figsize=(7.8,7.4))
for ax,(v,xlab,mval,logx,msg) in zip(axes,panels):
    d = tsa[v].dropna(); X = np.log10(d) if logx else d
    xm = np.log10(mval) if logx else mval
    pct = (d<mval).mean()*100 if v!="lu_mf" else (d<mval).mean()*100
    bins = np.linspace(X.min(), max(X.max(),xm)*1.02, 26)
    ax.hist(X, bins=bins, color=NEUT, edgecolor="white", linewidth=0.7, zorder=2)
    ax.axvline(xm, color=BLUE, lw=2.2, zorder=4)
    ax.annotate(f"Morocco\n{mval:,.1f}" if not logx else f"Morocco\n${mval:,.0f}",
                xy=(xm, ax.get_ylim()[1]*0.96), xytext=(7,0), textcoords="offset points",
                fontsize=8.6, fontweight="bold", color=BLUE, va="top", zorder=5)
    if logx:
        tk=[500,1000,2000,5000,10000,20000,40000]; ax.set_xticks(np.log10(tk)); ax.set_xticklabels([f"{x:,}" for x in tk])
    ax.set_xlabel(xlab); ax.set_ylabel("transitions"); ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_title(msg % (pct if v!="lu_mf" else pct), loc="left", fontsize=9.6, fontweight="normal", color=INK, pad=4)
fig.suptitle("$\\bf{Figure\\ 3.}$  Morocco's income is unexceptional, its mean schooling is average —\nbut its unschooled adult population is in the top quintile",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.035)
fig.tight_layout(h_pad=2.2)
note(axes[2], f"Distribution across all {len(tsa)} democratic transitions, 1960–2025. Morocco: GDP 2022 (Maddison); mean schooling 2023 (UNDP);\nshare with no schooling 2015 (latest Barro-Lee; a linear extrapolation of the 2000–15 trend gives ~33% for 2024).", y=-0.42)
save(fig,"F3_percentiles")

# ============================================================ F4  quantity vs quality (dumbbell)
q = p[(p.year==2020)].dropna(subset=["eyrs","lays"])
sel=["MAR","TUN","DZA","EGY","JOR","TUR","KOR","VNM","IDN","CHN","THA","MYS","IND","BRA","MEX","CHL","ESP","PRT","SEN","GHA","ZAF","SGP","PHL","PER","MNG","JPN"]
q=q[q.iso3.isin(sel)].sort_values("lays")
fig, ax = plt.subplots(figsize=(8.3,7.6))
y=np.arange(len(q))
for i,(_,r) in enumerate(q.iterrows()):
    hl = r.iso3=="MAR"
    ax.plot([r.lays,r.eyrs],[i,i], color=ORANGE if hl else "#D8D3CB", lw=3.2 if hl else 2.4,
            solid_capstyle="round", zorder=2)
ax.scatter(q.eyrs, y, s=42, c="white", edgecolors=MUTED, linewidths=1.5, zorder=3, label="Expected years of school")
ax.scatter(q.lays, y, s=46, c=BLUE, edgecolors="white", linewidths=1.2, zorder=4, label="Learning-adjusted years of school")
mi=list(q.iso3).index("MAR")
ax.scatter([q.lays.iloc[mi]],[mi], s=90, c=BLUE, edgecolors="white", linewidths=1.5, zorder=5)
ax.set_yticks(y); ax.set_yticklabels([NAME.get(i,i) for i in q.iso3], fontsize=8.4)
for lbl,i in [(ax.get_yticklabels()[mi],mi)]: lbl.set_fontweight("bold"); lbl.set_color(BLUE)
ax.annotate(f"{q.eyrs.iloc[mi]-q.lays.iloc[mi]:.1f} years lost\nto weak learning",
            xy=((q.lays.iloc[mi]+q.eyrs.iloc[mi])/2, mi), xytext=(0,12), textcoords="offset points",
            ha="center", fontsize=8.2, fontweight="bold", color=ORANGE, zorder=6)
ax.set_xlabel("Years of school a child entering school today can expect"); ax.grid(axis="x"); ax.set_axisbelow(True)
ax.set_xlim(3.5,14.5); ax.legend(loc="lower right", ncol=1)
ax.set_title("$\\bf{Figure\\ 4.}$  Morocco's schooling problem is quality, not just years\nExpected vs learning-adjusted years of school, 2020",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Learning-adjusted years discount expected years by the harmonized learning outcome (HLO). Source: World Bank Human Capital Index 2020.", y=-0.085)
save(fig,"F4_learning_gap")

# ============================================================ F5  composition of adult schooling
cases=[("MAR",2015,"Morocco 2015"),("SEN",1990,"Senegal 1990 *"),("BEN",1992,"Benin 1992 *"),
       ("PRT",1976,"Portugal 1976 *"),("ESP",1978,"Spain 1978 *"),("TUR",1990,"Türkiye 1990 *"),
       ("BRA",1987,"Brazil 1987 *"),("IDN",1999,"Indonesia 1999 *"),("TUN",2012,"Tunisia 2012 *"),
       ("MEX",1996,"Mexico 1996 *"),("KOR",1988,"South Korea 1988 *"),("TWN",1996,"Taiwan 1996 *"),
       ("POL",1990,"Poland 1990 *"),("VNM",2015,"Vietnam 2015")]
rows=[]
for iso,yr,lab in cases:
    r=p[(p.iso3==iso)&(p.year==yr)]
    if not len(r): continue
    r=r.iloc[0]
    if pd.isna(r.lu_mf): continue
    rows.append(dict(lab=lab, none=r.lu_mf, prim=r.lp_mf, sec=r.ls_mf, ter=r.lh_mf))
C=pd.DataFrame(rows); C[["none","prim","sec","ter"]]=C[["none","prim","sec","ter"]].div(C[["none","prim","sec","ter"]].sum(axis=1),axis=0)*100
C=C.sort_values("none")
fig, ax = plt.subplots(figsize=(8.6,6.2))
y=np.arange(len(C)); left=np.zeros(len(C))
labs=["No schooling at all","Primary only","Secondary","Tertiary"]
for k,(col,cl,lb) in enumerate(zip(["none","prim","sec","ter"],ORD,labs)):
    ax.barh(y, C[col], left=left, height=0.62, color=cl, edgecolor="white", linewidth=1.6, label=lb, zorder=2)
    left=left+C[col].values
for i,(_,r) in enumerate(C.iterrows()):
    if r["none"] >= 7:
        ax.annotate(f"{r['none']:.0f}%", xy=(r["none"]/2, i), ha="center", va="center",
                    fontsize=8.2, color="white", fontweight="bold", zorder=4)
    else:
        ax.annotate(f"{r['none']:.1f}%", xy=(r["none"], i), xytext=(5,0), textcoords="offset points",
                    ha="left", va="center", fontsize=8.0, color="white", fontweight="bold", zorder=4)
ax.set_yticks(y); ax.set_yticklabels(C.lab, fontsize=8.6)
for i,l in enumerate(ax.get_yticklabels()):
    if C.lab.iloc[i].startswith("Morocco"): l.set_fontweight("bold"); l.set_color(BLUE)
ax.set_xlabel("Share of adults aged 25–64 (%)"); ax.set_xlim(0,100)
ax.legend(loc="upper center", bbox_to_anchor=(0.5,-0.10), ncol=4)
ax.grid(axis="x"); ax.set_axisbelow(True)
ax.set_title("$\\bf{Figure\\ 5.}$  The missing base: educational composition of the adult population\nMorocco today vs. countries in the year they democratised (*)",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Source: Barro-Lee v3 (2021 update), ages 25–64.", y=-0.20)
save(fig,"F5_composition")
print("F3-F5 done")

# ============================================================ F6  the democracy deficit
mena=["MAR","DZA","TUN","EGY","JOR","LBN","IRQ","IRN","SAU","KWT","OMN","QAT","ARE","BHR","YEM","LBY","SYR"]
d=xs.set_index("iso3").dropna(subset=["pred","electdem"])
fig, ax = plt.subplots(figsize=(7.9,6.2))
lim=[-0.02,1.0]
ax.plot(lim,lim,color=NEUT,lw=1.2,zorder=1)
DIAG = ("as democratic as income\nand schooling predict", (0.80,0.80), (2,-32))
oth=d[~d.index.isin(mena)]
ax.scatter(oth.pred, oth.electdem, s=18, c=NEUT, edgecolors="none", zorder=2)
mm=d[d.index.isin(mena) & (d.index!="MAR")]
ax.scatter(mm.pred, mm.electdem, s=36, c=ORANGE, edgecolors="white", linewidths=0.8, zorder=3)
ax.set_xlim(lim); ax.set_ylim(lim)          # final frame before any label is measured
# Morocco and its deficit arrow are placed first; the MENA labels are fitted around them
r=d.loc["MAR"]
boxes=[]
ax.scatter([r.pred],[r.electdem], s=150, c=BLUE, marker="D", edgecolors="white", linewidths=1.6, zorder=5)
reserve_point(ax, (r.pred, r.electdem), boxes, r=10)
reserve(halo(ax.annotate("Morocco", xy=(r.pred,r.electdem), xytext=(-10,-4), textcoords="offset points",
                         fontsize=9.6, fontweight="bold", color=BLUE, ha="right", zorder=6)), boxes, pad=2.5)
ax.annotate("", xy=(r.pred,r.pred), xytext=(r.pred,r.electdem),
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.4), zorder=4)
reserve_span(ax, (r.pred,r.pred), (r.pred,r.electdem), boxes, w=3.5)
reserve(halo(ax.annotate(f"democracy deficit\n{r.resid:+.2f}", xy=(r.pred,(r.pred+r.electdem)/2), xytext=(7,0),
                         textcoords="offset points", fontsize=8.2, color=BLUE, fontweight="bold",
                         va="center", zorder=6)), boxes, pad=2.5)
reserve(ax.annotate(DIAG[0], xy=DIAG[1], xytext=DIAG[2], textcoords="offset points",
                    fontsize=7.6, color=MUTED, ha="center", zorder=4), boxes)
for iso,rr in mm.iterrows():
    halo(place_label(ax, (rr.pred,rr.electdem), NAME.get(iso,iso), boxes,
                     fontsize=7.2, color=ORANGE, zorder=4), lw=2.2)
ax.set_xlabel("Predicted electoral democracy index (from log GDP per capita + mean years of schooling)")
ax.set_ylabel("Actual electoral democracy index, 2019–23")
ax.grid(True); ax.set_axisbelow(True)
ax.legend(handles=[Line2D([],[],marker="D",ls="",color=BLUE,ms=8,label="Morocco"),
                   Line2D([],[],marker="o",ls="",color=ORANGE,ms=6,label="Other MENA"),
                   Line2D([],[],marker="o",ls="",color=NEUT,ms=5,label="Rest of the world")], loc="upper left")
ax.set_title("$\\bf{Figure\\ 6.}$  Morocco is not held back by its human capital — it is held back by its politics\nActual vs predicted democracy, 151 countries",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, f"Predictions from OLS of the V-Dem electoral democracy index on log GDP pc and mean years of schooling (R²=0.22, N=151, population > 1m).\n"
         f"Mean residual: MENA {K['MENA_resid']:+.2f}, rest of world {K['nonMENA_resid']:+.2f}.", y=-0.11)
save(fig,"F6_democracy_deficit")

# ============================================================ F7  sequencing: schooling before or after democracy
fig, ax = plt.subplots(figsize=(8.6,5.6))
series=[("KOR","South Korea",ORANGE,1988),("VNM","Vietnam",AQUA,None),("ESP","Spain","#A8822E",1978),
        ("TUN","Tunisia","#9E6B76",2012),("MAR","Morocco",BLUE,None)]
for iso,lab,col,tyr in series:
    d=p[(p.iso3==iso)&(p.year>=1950)&(p.year<=2015)].dropna(subset=["yr_sch_mf"]).sort_values("year")
    ax.plot(d.year, d.yr_sch_mf, color=col, lw=2.4 if iso=="MAR" else 1.9, zorder=4 if iso=="MAR" else 3)
    dyl = {"TUN":7, "VNM":-9}.get(iso, -2)
    ax.annotate(lab, xy=(d.year.iloc[-1], d.yr_sch_mf.iloc[-1]), xytext=(5,dyl), textcoords="offset points",
                fontsize=8.6, fontweight="bold", color=col)
    if tyr:
        v=d[d.year==tyr]
        if len(v):
            ax.scatter([tyr],[v.yr_sch_mf.iloc[0]], s=70, marker="o", c="white", edgecolors=col, linewidths=2, zorder=5)
            ax.annotate(f"democratises\n{tyr}", xy=(tyr, v.yr_sch_mf.iloc[0]), xytext=(-6,10),
                        textcoords="offset points", fontsize=7.4, color=col, ha="right", fontweight="bold")
ax.set_xlim(1950,2026); ax.set_ylim(0,14)
ax.set_xlabel("Year"); ax.set_ylabel("Mean years of schooling, adults 25–64")
ax.grid(axis="y"); ax.set_axisbelow(True)
ax.legend(handles=[Line2D([],[],color=c,lw=2,label=l) for _,l,c,_ in series], loc="upper left", ncol=3)
ax.set_title("$\\bf{Figure\\ 7.}$  Sequencing: East Asia built mass schooling under authoritarianism, and only then democratised\nMorocco's adult stock in 2015 was where Korea's stood in 1968 and Spain's in 1973",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Open circles mark the year of transition to electoral democracy. Source: Barro-Lee v3 (2021 update); V-Dem v15.", y=-0.155)
save(fig,"F7_sequencing")

# ============================================================ F8  gender gap
g=p[(p.year==2015)].dropna(subset=["lu_f","lu_m"])
sel=["MAR","TUN","DZA","EGY","JOR","TUR","KOR","VNM","IDN","CHN","THA","IND","BRA","MEX","CHL","ESP","PRT","SEN","GHA","ZAF","PHL","MYS","TWN","PER"]
g=g[g.iso3.isin(sel)].sort_values("lu_f")
fig, ax = plt.subplots(figsize=(7.9,7.0))
y=np.arange(len(g))
for i,(_,r) in enumerate(g.iterrows()):
    hl=r.iso3=="MAR"
    ax.plot([r.lu_m,r.lu_f],[i,i], color=BLUE if hl else "#D8D3CB", lw=3.0 if hl else 2.2, solid_capstyle="round", zorder=2)
ax.scatter(g.lu_m, y, s=40, c=BLUE, edgecolors="white", linewidths=1.0, zorder=3, label="Men")
ax.scatter(g.lu_f, y, s=40, c=ORANGE, edgecolors="white", linewidths=1.0, zorder=3, label="Women")
mi=list(g.iso3).index("MAR")
ax.set_yticks(y); ax.set_yticklabels([NAME.get(i,i) for i in g.iso3], fontsize=8.4)
ax.get_yticklabels()[mi].set_fontweight("bold"); ax.get_yticklabels()[mi].set_color(BLUE)
ax.annotate(f"{g.lu_f.iloc[mi]:.0f}% of Moroccan women\naged 25–64 never went to school",
            xy=(g.lu_f.iloc[mi], mi), xytext=(12,0), textcoords="offset points", ha="left", va="center",
            fontsize=8.4, fontweight="bold", color=ORANGE, zorder=6)
ax.set_xlabel("Share of adults aged 25–64 with no schooling at all (%)")
ax.grid(axis="x"); ax.set_axisbelow(True); ax.legend(loc="lower right")
ax.set_title("$\\bf{Figure\\ 8.}$  The gap is largely a gap in women's education\nAdults with no schooling, by sex, 2015",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Source: Barro-Lee v3 (2021 update), ages 25–64.", y=-0.09)
save(fig,"F8_gender_gap")

# ============================================================ F9  education inequality
E=pd.read_csv(os.path.join(CLEAN,"edu_gini.csv")).sort_values("edu_gini")
fig, ax = plt.subplots(figsize=(7.6,6.4))
cols=[BLUE if i=="MAR" else "#CFCAC2" for i in E.iso3]   # subject in brand colour, the field in neutral
y=np.arange(len(E))
ax.barh(y, E.edu_gini, height=0.66, color=cols, edgecolor="white", linewidth=1.2, zorder=2)
ax.set_yticks(y); ax.set_yticklabels([NAME.get(i,i) for i in E.iso3], fontsize=8.4)
mi=list(E.iso3).index("MAR")
ax.get_yticklabels()[mi].set_fontweight("bold"); ax.get_yticklabels()[mi].set_color(BLUE)
for i,(_,r) in enumerate(E.iterrows()):
    ax.annotate(f"{r.edu_gini:.2f}", xy=(r.edu_gini,i), xytext=(4,0), textcoords="offset points",
                va="center", fontsize=7.8, color=BLUE if r.iso3=="MAR" else INK2,
                fontweight="bold" if r.iso3=="MAR" else "normal")
ax.set_xlabel("Education Gini coefficient (0 = everyone equally schooled, 1 = maximal inequality)")
ax.set_xlim(0,0.85); ax.grid(axis="x"); ax.set_axisbelow(True)
ax.set_title("$\\bf{Figure\\ 9.}$  Morocco's human capital is not just low — it is extraordinarily unequal\nEducation Gini, adults 25–64, 2015",
             loc="left", fontweight="normal", fontsize=11.5, pad=12)
note(ax, "Education Gini computed on the Barro-Lee attainment distribution following Thomas, Wang & Fan (2001).", y=-0.095)
save(fig,"F9_education_gini")
print("F6-F9 done")

# ============================================================ F10  Morocco's own trajectory (small multiples, one measure each)
fig, axes = plt.subplots(2,1, figsize=(8.2,6.2), sharex=True)
d=p[(p.iso3=="MAR")&(p.year>=1950)&(p.year<=2015)].dropna(subset=["yr_sch_mf"]).sort_values("year")
axes[0].plot(d.year, d.yr_sch_mf, color=BLUE, lw=2.4, zorder=3)
axes[0].fill_between(d.year, 0, d.yr_sch_mf, color=BLUE, alpha=0.08, zorder=2)
axes[0].set_ylabel("Mean years of schooling\nadults 25–64"); axes[0].set_ylim(0,7)
axes[0].annotate(f"0.3 yrs", xy=(1950, d.yr_sch_mf.iloc[0]), xytext=(4,8), textcoords="offset points",
                 fontsize=8, color=BLUE, fontweight="bold")
axes[0].annotate(f"5.1 yrs  (×17 in 65 years)", xy=(2015, d.yr_sch_mf.iloc[-1]), xytext=(-4,6),
                 textcoords="offset points", fontsize=8.6, color=BLUE, fontweight="bold", ha="right")
axes[0].set_title("$\\bf{a.}$  Human capital: transformed", loc="left", fontweight="normal")

e=p[(p.iso3=="MAR")&(p.year>=1950)].dropna(subset=["electdem"]).sort_values("year")
axes[1].plot(e.year, e.electdem, color=ORANGE, lw=2.4, zorder=3)
axes[1].fill_between(e.year, 0, e.electdem, color=ORANGE, alpha=0.08, zorder=2)
axes[1].set_ylabel("V-Dem electoral\ndemocracy index (0–1)"); axes[1].set_ylim(0,1.0)
axes[1].axhline(0.5, color=GRID, lw=1.0, zorder=1)
axes[1].annotate("threshold usually crossed at a democratic transition", xy=(1955,0.5), xytext=(0,5),
                 textcoords="offset points", fontsize=7.4, color=MUTED)
for yr,lab,dy in [(1962,"first\nconstitution",13),(2011,"2011 constitutional\nreform",-14)]:
    v=e[e.year==yr]
    if len(v):
        axes[1].scatter([yr],[v.electdem.iloc[0]], s=48, c="white", edgecolors=ORANGE, linewidths=1.8, zorder=5)
        axes[1].annotate(lab, xy=(yr, v.electdem.iloc[0]), xytext=(0,dy), textcoords="offset points",
                         fontsize=7.6, color=ORANGE, ha="center",
                         va="bottom" if dy>0 else "top", fontweight="bold")
axes[1].annotate(f"0.26 in 2025 — the same band as in 2005", xy=(2025, e.electdem.iloc[-1]),
                 xytext=(-4,10), textcoords="offset points", fontsize=8.6, color=ORANGE, fontweight="bold", ha="right")
axes[1].set_title("$\\bf{b.}$  Political regime: unchanged", loc="left", fontweight="normal")
axes[1].set_xlabel("Year"); axes[1].set_xlim(1950,2027)
for a in axes: a.grid(axis="y"); a.set_axisbelow(True)
fig.suptitle("$\\bf{Figure\\ 10.}$  Morocco multiplied its schooling seventeenfold without moving its regime",
             x=0.005, ha="left", fontsize=12, fontweight="normal", y=1.01)
fig.tight_layout(h_pad=2.0)
note(axes[1], "V-Dem's Regimes of the World has coded Morocco a CLOSED autocracy in every year 1955–2025, because the effective chief executive\n"
              "is not chosen through multiparty elections. Sources: Barro-Lee v3; V-Dem v15.", y=-0.30)
save(fig,"F10_morocco_trajectory")
