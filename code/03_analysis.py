"""
03_analysis.py -- Tables and key statistics for the Morocco democratization gap analysis.
Writes markdown + LaTeX tables to ../tables and a JSON of headline numbers to ../data/clean.
"""
import os, json
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE  = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(HERE,"..","data","clean"); TAB = os.path.join(HERE,"..","tables")
os.makedirs(TAB, exist_ok=True)
p = pd.read_csv(os.path.join(CLEAN,"panel.csv"))
t = pd.read_csv(os.path.join(CLEAN,"transitions.csv"))
K = {}

def out(name, df, caption, floatfmt="%.2f"):
    df.to_csv(os.path.join(TAB, name+".csv"), index=False)
    with open(os.path.join(TAB, name+".md"),"w") as f:
        f.write(f"**{caption}**\n\n" + df.to_markdown(index=False, floatfmt=".2f") + "\n")
    with open(os.path.join(TAB, name+".tex"),"w") as f:
        f.write(df.to_latex(index=False, float_format=lambda x: floatfmt % x,
                            caption=caption, label="tab:"+name, escape=True))
    print(f"\n### {caption}\n"); print(df.to_string(index=False))

last = lambda iso,v: (lambda s: (int(s.iloc[-1].year), float(s.iloc[-1][v])) if len(s) else (None,np.nan))(
    p[(p.iso3==iso)][["year",v]].dropna())

# =========================================================== T1  Morocco fact sheet
rows=[]
LBL = {"gdppc_ppp21":"GDP per capita, PPP (constant 2021 int$)","gdppc_mad":"GDP per capita (Maddison, 2011 int$)",
 "mys":"Mean years of schooling, adults","yr_sch_mf":"Mean years of schooling, 25-64 (Barro-Lee v3)",
 "yr_sch_f":"  of which: women, 25-64","yr_sch_m":"  of which: men, 25-64",
 "lu_mf":"Share of adults 25-64 with NO schooling (%)","lu_f":"  of which: women (%)","lu_m":"  of which: men (%)",
 "lhc_mf":"Share of adults 25-64 completing tertiary (%)","lit_adult":"Adult literacy rate, 15+ (%)",
 "lit_youth":"Youth literacy rate, 15-24 (%)","enr_sec":"Gross enrolment, secondary (%)","enr_ter":"Gross enrolment, tertiary (%)",
 "eyrs":"Expected years of school (HCI)","lays":"Learning-adjusted years of school (HCI)",
 "hlo":"Harmonized test score (HLO, 300-625)","hci":"Human Capital Index (0-1)",
 "electdem":"V-Dem electoral democracy index (0-1)","libdem":"V-Dem liberal democracy index (0-1)",
 "flfp":"Female labour force participation, 15+ (%)"}
for v,l in LBL.items():
    y,val = last("MAR",v)
    if y: rows.append({"Indicator":l,"Year":y,"Morocco":val})
t1 = pd.DataFrame(rows); out("T1_morocco_factsheet", t1, "Table 1. Morocco: income, human capital and political regime, latest available")
for v in LBL: K["MAR_"+v] = last("MAR",v)

# =========================================================== T2  Conditions at transition
ts = t[t.year>=1960].copy()
MG = last("MAR","gdppc_mad")[1]; MM = last("MAR","mys")[1]
MGp = last("MAR","gdppc_ppp21")[1]
g  = ts.dropna(subset=["gdppc_mad"]); ms = ts.dropna(subset=["mys"]); nl = ts.dropna(subset=["lu_mf"])
def dist(s, label, mval):
    q = s.quantile([.1,.25,.5,.75,.9])
    return {"Variable":label,"N":len(s),"p10":q[.1],"p25":q[.25],"Median":q[.5],"p75":q[.75],"p90":q[.9],
            "Morocco today":mval,"Morocco percentile":(s<mval).mean()*100}
t2 = pd.DataFrame([
    dist(g.gdppc_mad,  "GDP pc at transition (2011 int$)", MG),
    dist(ms.mys,       "Mean years of schooling at transition", MM),
    dist(nl.lu_mf,     "% adults with no schooling at transition", last("MAR","lu_mf")[1]),
])
out("T2_transition_distribution", t2, "Table 2. Conditions at the moment of democratic transition, 1960-2025 (V-Dem Regimes of the World), and Morocco's position today")
K["pct_transitions_poorer"]   = float((g.gdppc_mad < MG).mean()*100)
K["pct_transitions_lesseduc"] = float((ms.mys < MM).mean()*100)
K["n_transitions"] = int(len(ts)); K["med_gdp_trans"]=float(g.gdppc_mad.median()); K["med_mys_trans"]=float(ms.mys.median())

# =========================================================== T3  Benchmark transitions
bench = [("PRT",1976,"Portugal"),("ESP",1978,"Spain"),("BRA",1987,"Brazil"),("KOR",1988,"South Korea"),
         ("PHL",1988,"Philippines"),("CHL",1990,"Chile"),("POL",1990,"Poland"),("TWN",1996,"Taiwan"),
         ("MEX",1996,"Mexico"),("IDN",1999,"Indonesia"),("TUN",2012,"Tunisia"),("TUR",1990,"Turkey"),
         ("GHA",1996,"Ghana"),("SEN",1990,"Senegal"),("ZAF",1995,"South Africa"),("MNG",1991,"Mongolia"),
         ("PER",2001,"Peru"),("ROU",1990,"Romania")]
rows=[]
for iso,yr,nm in bench:
    r = p[(p.iso3==iso)&(p.year==yr)]
    if not len(r): continue
    r=r.iloc[0]
    e10 = p[(p.iso3==iso)&(p.year==yr+10)].electdem
    now = p[(p.iso3==iso)].dropna(subset=["electdem"]).iloc[-1]
    rows.append({"Country":nm,"Transition year":yr,"GDP pc (2011$)":r.gdppc_mad,"Mean yrs school":r.mys,
                 "% no schooling":r.lu_mf,"Elect. dem. at T":r.electdem,
                 "Elect. dem. T+10":float(e10.iloc[0]) if len(e10) else np.nan,
                 "Elect. dem. 2024":float(now.electdem)})
mr = p[p.iso3=="MAR"]
rows.append({"Country":"MOROCCO (today)","Transition year":2023,"GDP pc (2011$)":MG,"Mean yrs school":MM,
             "% no schooling":last("MAR","lu_mf")[1],"Elect. dem. at T":last("MAR","electdem")[1],
             "Elect. dem. T+10":np.nan,"Elect. dem. 2024":last("MAR","electdem")[1]})
t3 = pd.DataFrame(rows).sort_values("Transition year")
out("T3_benchmark_transitions", t3, "Table 3. Income and education at the moment of transition: eighteen democratisations compared with Morocco today")

# =========================================================== T4  Education profile
prof = ["MAR","TUN","DZA","EGY","JOR","TUR","KOR","TWN","VNM","IDN","CHN","THA","MYS","IND","BRA","MEX","CHL","ESP","PRT","SEN","GHA","ZAF","SGP","PHL","PER","MNG"]
bl15 = p[(p.year==2015)&p.iso3.isin(prof)][["iso3","yr_sch_mf","yr_sch_f","yr_sch_m","lu_mf","lu_f","lhc_mf"]]
hci20= p[(p.year==2020)&p.iso3.isin(prof)][["iso3","eyrs","lays","hlo","hci"]]
dem  = p[(p.year>=2019)&(p.year<=2023)&p.iso3.isin(prof)].groupby("iso3").agg(
        country=("country","first"), electdem=("electdem","mean"), gdp=("gdppc_ppp21","mean")).reset_index()
t4 = (dem.merge(bl15,on="iso3",how="left").merge(hci20,on="iso3",how="left"))
t4["gender gap (yrs)"] = t4.yr_sch_m - t4.yr_sch_f
t4 = t4.rename(columns={"country":"Country","gdp":"GDP pc PPP","yr_sch_mf":"Yrs school 25-64",
      "lu_mf":"% no schooling","lu_f":"% no schooling, women","lhc_mf":"% tertiary complete",
      "hlo":"HLO score","lays":"Learn-adj. yrs","eyrs":"Expected yrs","electdem":"Elect. dem. index"})
t4 = t4[["Country","GDP pc PPP","Yrs school 25-64","% no schooling","% no schooling, women","gender gap (yrs)",
         "% tertiary complete","Expected yrs","Learn-adj. yrs","HLO score","Elect. dem. index"]].sort_values("Yrs school 25-64")
out("T4_education_profile", t4, "Table 4. The human-capital profile: schooling stock (2015), learning quality (2020) and democracy (2019-23)")

# =========================================================== T5  Cross-section: democracy ~ income + schooling
c = p[(p.year>=2019)&(p.year<=2023)].groupby("iso3").agg(
    country=("country","first"), electdem=("electdem","mean"), libdem=("libdem","mean"),
    gdp=("gdppc_ppp21","mean"), mys=("mys","mean"), hlo=("hlo","mean"), lays=("lays","mean"),
    resrents=("resrents","mean"), pop=("pop","mean"), corrupt=("corrupt","mean"),
    rolaw=("rolaw","mean")).dropna(subset=["electdem","gdp","mys"])
c = c[c["pop"]>1e6].copy(); c["lgdp"]=np.log(c.gdp)
specs = [["lgdp"],["mys"],["lgdp","mys"],["lgdp","mys","resrents"],["lgdp","lays"]]
rows=[]
for S in specs:
    cc=c.dropna(subset=S); r=sm.OLS(cc.electdem, sm.add_constant(cc[S])).fit(cov_type="HC1")
    d={"Specification":" + ".join(S),"N":len(cc),"R2":r.rsquared}
    for k in ["lgdp","mys","lays","resrents"]:
        d[k] = f"{r.params[k]:+.4f} ({r.tvalues[k]:+.1f})" if k in r.params else ""
    rows.append(d)
t5 = pd.DataFrame(rows)[["Specification","lgdp","mys","lays","resrents","N","R2"]]
t5.columns = ["Specification","log GDP pc","Mean yrs school","Learn-adj. yrs","Resource rents","N","R2"]
out("T5_crosssection", t5, "Table 5. Cross-country OLS: V-Dem electoral democracy index on income and schooling, 2019-23 averages (HC1 t-stats)")

cc=c.dropna(subset=["lgdp","mys"]); r=sm.OLS(cc.electdem, sm.add_constant(cc[["lgdp","mys"]])).fit(cov_type="HC1")
cc["pred"]=r.fittedvalues; cc["resid"]=r.resid
K["MAR_actual"]=float(cc.loc["MAR","electdem"]); K["MAR_pred"]=float(cc.loc["MAR","pred"]); K["MAR_resid"]=float(cc.loc["MAR","resid"])
K["MAR_resid_rank"]=int((cc.resid<cc.loc["MAR","resid"]).sum())+1; K["N_xsec"]=len(cc)
mena=["MAR","DZA","TUN","EGY","JOR","LBN","IRQ","IRN","SAU","KWT","OMN","QAT","ARE","BHR","YEM","LBY","SYR"]
K["MENA_resid"]=float(cc[cc.index.isin(mena)].resid.mean()); K["nonMENA_resid"]=float(cc[~cc.index.isin(mena)].resid.mean())
t5b = cc[cc.index.isin(mena)][["country","electdem","pred","resid","gdp","mys"]].sort_values("resid")
t5b.columns=["Country","Actual elect. dem.","Predicted","Gap (actual-predicted)","GDP pc PPP","Mean yrs school"]
out("T5b_mena_deficit", t5b.reset_index(drop=True), "Table 5b. The Arab democracy deficit: actual vs predicted electoral democracy given income and schooling")
cc.reset_index().to_csv(os.path.join(CLEAN,"crosssection.csv"), index=False)

# =========================================================== T6  Where education bites: quality of democracy
dems = c[c.index.isin(p[(p.year==2023)&(p.regime>=2)].iso3)].copy()
rows=[]
for y in ["libdem","rolaw","corrupt"]:
    for S in [["lgdp"],["mys"],["lgdp","mys"]]:
        dd = dems.dropna(subset=S+[y])
        r = sm.OLS(dd[y], sm.add_constant(dd[S])).fit(cov_type="HC1")
        rows.append({"Outcome":{"libdem":"Liberal democracy index","rolaw":"Rule of law",
                                "corrupt":"Political corruption (higher=worse)"}[y],
                     "Regressors":" + ".join(S),
                     "log GDP pc": f"{r.params['lgdp']:+.4f} ({r.tvalues['lgdp']:+.1f})" if "lgdp" in r.params else "",
                     "Mean yrs school": f"{r.params['mys']:+.4f} ({r.tvalues['mys']:+.1f})" if "mys" in r.params else "",
                     "N":len(dd),"R2":r.rsquared})
t6 = pd.DataFrame(rows)
out("T6_quality_of_democracy", t6, "Table 6. Among electoral democracies only: what predicts the QUALITY of democracy (2019-23)")

# =========================================================== T7  Within-country panel (AJRY-style)
pn = p[(p.year>=1960)&(p.year<=2015)][["iso3","year","electdem","gdppc_mad","mys"]].dropna()
pn = pn[pn.year % 5 == 0].copy()
pn["lgdp"]=np.log(pn.gdppc_mad)
pn = pn.sort_values(["iso3","year"])
pn["L_electdem"]=pn.groupby("iso3").electdem.shift(1)
pn["L_lgdp"]=pn.groupby("iso3").lgdp.shift(1); pn["L_mys"]=pn.groupby("iso3").mys.shift(1)
pn = pn.dropna()
rows=[]
for lab, fe in [("Pooled OLS (no FE)", False), ("Country + period fixed effects", True)]:
    X = pn[["L_electdem","L_lgdp","L_mys"]].copy()
    if fe:
        X = pd.concat([X, pd.get_dummies(pn.iso3, prefix="c", drop_first=True, dtype=float),
                          pd.get_dummies(pn.year, prefix="t", drop_first=True, dtype=float)], axis=1)
    r = sm.OLS(pn.electdem, sm.add_constant(X)).fit(cov_type="cluster", cov_kwds={"groups":pn.iso3})
    rows.append({"Specification":lab,
        "Lagged democracy": f"{r.params['L_electdem']:+.3f} ({r.tvalues['L_electdem']:+.1f})",
        "Lagged log GDP pc": f"{r.params['L_lgdp']:+.4f} ({r.tvalues['L_lgdp']:+.1f})",
        "Lagged yrs school": f"{r.params['L_mys']:+.4f} ({r.tvalues['L_mys']:+.1f})",
        "N":len(pn),"Countries":pn.iso3.nunique()})
t7 = pd.DataFrame(rows)
out("T7_panel_fe", t7, "Table 7. Five-year panel, 1960-2015: does income or schooling RAISE democracy within a country? (clustered t-stats)")

json.dump(K, open(os.path.join(CLEAN,"key_numbers.json"),"w"), indent=1, default=str)
print("\n\nKEY NUMBERS:"); print(json.dumps(K, indent=1, default=str))
