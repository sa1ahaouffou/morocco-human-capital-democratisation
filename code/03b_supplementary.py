"""
03b_supplementary.py -- Results cited in the notes that are not in 03_analysis.py:
education Gini (Figure 9), democratic survival, post-transition democracy level, and the
"years behind" comparison. Previously computed ad hoc; now part of the pipeline.
"""
import os, json
import numpy as np, pandas as pd, statsmodels.api as sm

HERE=os.path.dirname(os.path.abspath(__file__))
CLEAN=os.path.join(HERE,"..","data","clean"); TAB=os.path.join(HERE,"..","tables")
p=pd.read_csv(os.path.join(CLEAN,"panel.csv"), low_memory=False)
t=pd.read_csv(os.path.join(CLEAN,"transitions.csv"))
K={}

def out(name, df, cap):
    df.to_csv(os.path.join(TAB,name+".csv"), index=False)
    open(os.path.join(TAB,name+".md"),"w").write(f"**{cap}**\n\n"+df.to_markdown(index=False, floatfmt=".3f")+"\n")
    open(os.path.join(TAB,name+".tex"),"w").write(df.to_latex(index=False, float_format=lambda x:"%.3f"%x,
                                                            caption=cap, label="tab:"+name, escape=True))
    print(f"\n### {cap}\n"); print(df.to_string(index=False))

# ---- 1. Education Gini, Thomas-Wang-Fan (2001) direct method on Barro-Lee shares, 2015
DUR = np.array([0,3,6,9,12,14,16], float)   # none, pri-inc, pri-comp, sec-inc, sec-comp, ter-inc, ter-comp
SEL = ["MAR","TUN","DZA","EGY","JOR","TUR","KOR","TWN","VNM","IDN","CHN","BRA","MEX","CHL",
       "ESP","PRT","IND","SEN","GHA","THA","MYS","PHL","ZAF","PER","MNG"]
rows=[]
for _,r in p[(p.year==2015)&p.iso3.isin(SEL)].iterrows():
    sh=np.array([r.lu_mf, r.lp_mf-r.lpc_mf, r.lpc_mf, r.ls_mf-r.lsc_mf, r.lsc_mf,
                 r.lh_mf-r.lhc_mf, r.lhc_mf], float)/100
    if np.isnan(sh).any(): continue
    sh=sh/sh.sum(); mu=(sh*DUR).sum()
    G=sum(abs(DUR[i]-DUR[j])*sh[i]*sh[j] for i in range(7) for j in range(7))/(2*mu)
    rows.append(dict(iso3=r.iso3, country=r.country, mean_yrs_implied=mu, edu_gini=G, no_school=r.lu_mf))
E=pd.DataFrame(rows).sort_values("edu_gini", ascending=False)
E.to_csv(os.path.join(CLEAN,"edu_gini.csv"), index=False)
out("T11_education_gini", E.drop(columns="iso3"), "Table 11. Education Gini coefficient, adults 25-64, 2015 (Thomas-Wang-Fan method on Barro-Lee v3)")
K["MAR_edu_gini"]=float(E.set_index("iso3").loc["MAR","edu_gini"])

# ---- 2. Survival and post-transition democracy level
ts=t[t.year>=1960].copy()
lvl=[]
for _,r in ts.iterrows():
    w=p[(p.iso3==r.iso3)&(p.year>r.year)&(p.year<=r.year+10)]
    lvl.append(dict(iso3=r.iso3, year=r.year, mys=r.mys, lu=r.lu_mf, gdp=r.gdppc_mad, surv10=r.surv10,
                    e10=w.electdem.mean() if len(w)>=8 else np.nan,
                    lib10=w.libdem.mean() if len(w)>=8 else np.nan))
L=pd.DataFrame(lvl); L["lgdp"]=np.log(L.gdp)

res=[]
for y,lab in [("surv10","Survived 10 years (logit)"),("e10","Electoral democracy, mean T+1..T+10 (OLS)"),
              ("lib10","Liberal democracy, mean T+1..T+10 (OLS)")]:
    for X in (["mys"],["lgdp"],["mys","lgdp"],["lu"]):
        d=L.dropna(subset=X+[y])
        if y=="surv10":
            m=sm.Logit(d[y], sm.add_constant(d[X])).fit(disp=0); fit=m.prsquared
        else:
            m=sm.OLS(d[y], sm.add_constant(d[X])).fit(cov_type="HC1"); fit=m.rsquared
        res.append({"Outcome":lab, "Regressors":" + ".join(X),
                    **{k:(f"{m.params[k]:+.4f} (p={m.pvalues[k]:.3f})" if k in m.params else "") for k in ["mys","lgdp","lu"]},
                    "N":len(d), "Fit (R2 / pseudo-R2)":fit})
R=pd.DataFrame(res).rename(columns={"mys":"Mean yrs school at T","lgdp":"log GDP pc at T","lu":"% no schooling at T"})
out("T12_after_transition", R, "Table 12. What schooling at the moment of transition predicts: survival vs democracy level (transitions 1960-2025)")

d=L.dropna(subset=["mys","surv10","e10"]).copy()
d["tercile"]=pd.qcut(d.mys,3,labels=["low","mid","high"])
T=d.groupby("tercile",observed=True).agg(n=("surv10","size"), mean_yrs=("mys","mean"),
        survived_10y=("surv10","mean"), elect_dem_T10=("e10","mean"), lib_dem_T10=("lib10","mean")).reset_index()
out("T12b_by_tercile", T, "Table 12b. Post-transition outcomes by schooling tercile at transition")
m=sm.Logit(L.dropna(subset=["mys","surv10"]).surv10, sm.add_constant(L.dropna(subset=["mys","surv10"])[["mys"]])).fit(disp=0)
K["surv10_rate"]=float(L.surv10.mean()); K["surv10_mys_p"]=float(m.pvalues["mys"])

# ---- 3. How many years behind is Morocco's 2015 stock?
mar=float(p[(p.iso3=="MAR")&(p.year==2015)].yr_sch_mf.iloc[0])
yb=[]
for iso in ["KOR","ESP","TWN","PRT","VNM","TUN"]:
    s=p[(p.iso3==iso)&(~p.bl_interpolated)].dropna(subset=["yr_sch_mf"]).sort_values("year")
    s_all=p[(p.iso3==iso)].dropna(subset=["yr_sch_mf"]).sort_values("year")
    hit=s_all[s_all.yr_sch_mf>=mar]
    y=int(hit.year.iloc[0]) if len(hit) else None
    yb.append(dict(country=s_all.country.iloc[0], year_reached=y, years_behind=2015-y if y else None))
out("T13_years_behind", pd.DataFrame(yb), f"Table 13. Year each country's adult schooling stock first reached Morocco's 2015 level ({mar:.2f} yrs, Barro-Lee 25-64)")

old=json.load(open(os.path.join(CLEAN,"key_numbers.json"))); old.update(K)
json.dump(old, open(os.path.join(CLEAN,"key_numbers.json"),"w"), indent=1, default=str)
