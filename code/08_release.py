"""
08_release.py -- Build the shareable data package in release/:
curated CSVs, one Excel workbook, CODEBOOK.md, SOURCES_AND_LICENSES.md, README.md.
"""
import os, shutil
import numpy as np, pandas as pd

# Fixed so that rebuilding the package reproduces it byte for byte; bump it when the
# contents change, not when the build happens to be re-run.
RELEASE_DATE = "September 2026"

HERE=os.path.dirname(os.path.abspath(__file__))
CLEAN=os.path.join(HERE,"..","data","clean"); REL=os.path.join(HERE,"..","release")
shutil.rmtree(REL, ignore_errors=True); os.makedirs(os.path.join(REL,"data"))

# ------------------------------------------------------------------ variable dictionary
# new_name: (old_name, label, unit, source, decimals)
V = {
 "iso3":("iso3","ISO 3166 alpha-3 code (OWID_* = historical polity)","code","—",None),
 "country":("country","Country name","text","V-Dem > World Bank > ISO",None),
 "year":("year","Year","year","—",None),
 "historical_state":("historical_state","Polity no longer exists (USSR, GDR, Yugoslavia…)","bool","OWID",None),
 "vdem_regime_row":("regime","Regimes of the World: 0 closed autocracy, 1 electoral autocracy, 2 electoral democracy, 3 liberal democracy","0–3","V-Dem v15 via OWID",0),
 "vdem_electoral_dem":("electdem","Electoral democracy index (v2x_polyarchy)","0–1","V-Dem v15 via OWID",3),
 "vdem_liberal_dem":("libdem","Liberal democracy index","0–1","V-Dem v15 via OWID",3),
 "vdem_participatory_dem":("partdem","Participatory democracy index","0–1","V-Dem v15 via OWID",3),
 "vdem_civil_liberties":("civlib","Civil liberties index","0–1","V-Dem v15 via OWID",3),
 "vdem_rule_of_law":("rolaw","Rule of law index","0–1","V-Dem v15 via OWID",3),
 "vdem_freedom_expression":("freeexpr","Freedom of expression index","0–1","V-Dem v15 via OWID",3),
 "vdem_political_corruption":("corrupt","Political corruption index (higher = more corrupt)","0–1","V-Dem v15 via OWID",3),
 "gdppc_maddison_2011usd":("gdppc_mad","GDP per capita","2011 int$","Maddison Project 2023 via OWID",0),
 "gdppc_ppp_2021usd":("gdppc_ppp21","GDP per capita, PPP","constant 2021 int$","WDI NY.GDP.PCAP.PP.KD",0),
 "gdppc_const_2015usd":("gdppc_usd15","GDP per capita","constant 2015 US$","WDI NY.GDP.PCAP.KD",0),
 "population":("pop","Population","persons","WDI SP.POP.TOTL",0),
 "bl_mys_2564":("yr_sch_mf","Mean years of schooling, ages 25–64","years","Barro-Lee v3",2),
 "bl_mys_2564_female":("yr_sch_f","Mean years of schooling, women 25–64","years","Barro-Lee v3",2),
 "bl_mys_2564_male":("yr_sch_m","Mean years of schooling, men 25–64","years","Barro-Lee v3",2),
 "bl_noschool_2564":("lu_mf","Share with no schooling, 25–64","% of age group","Barro-Lee v3",2),
 "bl_noschool_2564_female":("lu_f","Share with no schooling, women 25–64","%","Barro-Lee v3",2),
 "bl_noschool_2564_male":("lu_m","Share with no schooling, men 25–64","%","Barro-Lee v3",2),
 "bl_primary_2564":("lp_mf","Highest level attained = primary (complete or not), 25–64","%","Barro-Lee v3",2),
 "bl_primary_complete_2564":("lpc_mf","Primary completed as highest level, 25–64","%","Barro-Lee v3",2),
 "bl_secondary_2564":("ls_mf","Highest level attained = secondary, 25–64","%","Barro-Lee v3",2),
 "bl_secondary_complete_2564":("lsc_mf","Secondary completed as highest level, 25–64","%","Barro-Lee v3",2),
 "bl_tertiary_2564":("lh_mf","Highest level attained = tertiary, 25–64","%","Barro-Lee v3",2),
 "bl_tertiary_complete_2564":("lhc_mf","Tertiary completed, 25–64","%","Barro-Lee v3",2),
 "bl_interpolated":("bl_interpolated","TRUE if Barro-Lee values are linear interpolations between 5-year observations","bool","constructed",None),
 "undp_mys_25plus":("mys_undp","Mean years of schooling, 25+","years","UNDP HDR via OWID",2),
 "mys_best":("mys","Mean years of schooling used in the analysis: Barro-Lee 25–64 where available, else UNDP 25+","years","constructed",2),
 "mys_best_source":("mys_source","Which series mys_best comes from","text","constructed",None),
 "literacy_adult_15plus":("lit_adult","Adult literacy rate, 15+","%","WDI SE.ADT.LITR.ZS",1),
 "literacy_youth_1524":("lit_youth","Youth literacy rate, 15–24","%","WDI SE.ADT.1524.LT.ZS",1),
 "literacy_longrun":("lit_longrun","Literacy rate, long-run series","%","OWID (multiple sources)",1),
 "enrol_primary_gross":("enr_pri","Gross enrolment ratio, primary","%","WDI SE.PRM.ENRR",1),
 "enrol_secondary_gross":("enr_sec","Gross enrolment ratio, secondary","%","WDI SE.SEC.ENRR",1),
 "enrol_secondary_net":("enr_sec_net","Net enrolment rate, secondary","%","WDI SE.SEC.NENR",1),
 "enrol_tertiary_gross":("enr_ter","Gross enrolment ratio, tertiary","%","WDI SE.TER.ENRR",1),
 "attain_primary_25plus":("att_pri","At least completed primary, 25+ (cumulative)","%","WDI SE.PRM.CUAT.ZS",1),
 "attain_lowersec_25plus":("att_losec","At least completed lower secondary, 25+","%","WDI SE.SEC.CUAT.LO.ZS",1),
 "attain_uppersec_25plus":("att_upsec","At least completed upper secondary, 25+","%","WDI SE.SEC.CUAT.UP.ZS",1),
 "attain_bachelor_25plus":("att_ba","At least bachelor's, 25+","%","WDI SE.TER.CUAT.BA.ZS",1),
 "learning_poverty":("learnpov","Learning poverty (share of 10-year-olds unable to read a simple text)","%","WDI SE.LPV.PRIM",1),
 "hci":("hci","Human Capital Index","0–1","World Bank HCI (source 63)",3),
 "hlo":("hlo","Harmonized learning outcome (test score)","300–625","World Bank HCI HD.HCI.HLOS",1),
 "hlo_female":("hlo_f","Harmonized learning outcome, girls","300–625","World Bank HCI",1),
 "hlo_male":("hlo_m","Harmonized learning outcome, boys","300–625","World Bank HCI",1),
 "expected_yrs_school":("eyrs","Expected years of school","years","World Bank HCI HD.HCI.EYRS",2),
 "learning_adj_yrs_school":("lays","Learning-adjusted years of school","years","World Bank HCI HD.HCI.LAYS",2),
 "pisa_math":("pisa_mat","PISA mean score, mathematics","score","WB EdStats LO.PISA.MAT (to 2018)",1),
 "pisa_reading":("pisa_rea","PISA mean score, reading","score","WB EdStats LO.PISA.REA (to 2018)",1),
 "pisa_science":("pisa_sci","PISA mean score, science","score","WB EdStats LO.PISA.SCI (to 2018)",1),
 "timss_math_grade4":("timss_mat4","TIMSS mean score, grade-4 mathematics","score","WB EdStats LO.TIMSS.MAT4",1),
 "female_lfp_15plus":("flfp","Female labour force participation, 15+ (modelled ILO)","%","WDI SL.TLF.CACT.FE.ZS",1),
 "resource_rents_gdp":("resrents","Total natural resource rents","% of GDP","WDI NY.GDP.TOTL.RT.ZS",2),
 "gini_income":("gini","Gini index of income/consumption","0–100","WDI SI.POV.GINI",1),
}

def curate(df, keys):
    out = pd.DataFrame({k: df[V[k][0]] for k in keys if V[k][0] in df})
    for k in out:
        d = V[k][4]
        if d is not None and pd.api.types.is_numeric_dtype(out[k]):
            out[k] = out[k].round(d)
            if d == 0: out[k] = out[k].astype("Int64")
    return out

p = pd.read_csv(os.path.join(CLEAN,"panel.csv"), low_memory=False)
panel = curate(p, list(V))
data_cols = [c for c in panel if c not in ("iso3","country","year","historical_state","bl_interpolated","mys_best_source")]
panel = panel[panel[data_cols].notna().any(axis=1)]            # drop all-empty rows
panel = panel.sort_values(["iso3","year"]).reset_index(drop=True)

# ------------------------------------------------------------------ other tables
t = pd.read_csv(os.path.join(CLEAN,"transitions.csv"))
trans = pd.DataFrame({"iso3":t.iso3,"country":t.country,"transition_year":t.year,
    "survived_5y":t.surv5,"survived_10y":t.surv10,
    "gdppc_maddison_2011usd":t.gdppc_mad.round(0),"mys_best":t.mys.round(2),
    "bl_noschool_2564":t.lu_mf.round(2),"bl_mys_2564_female":t.yr_sch_f.round(2),
    "bl_mys_2564_male":t.yr_sch_m.round(2),"literacy_longrun":t.lit_longrun.round(1)})
tw = pd.read_csv(os.path.join(CLEAN,"transitions_wcde.csv"))[["iso3","year","w_noed","w_mys"]]
tw.columns=["iso3","transition_year","wcde_noschool_25plus","wcde_mys_25plus"]
trans = trans.merge(tw.round(2), on=["iso3","transition_year"], how="left").sort_values(["transition_year","iso3"])

x = pd.read_csv(os.path.join(CLEAN,"crosssection.csv"))
xs = pd.DataFrame({"iso3":x.iso3,"country":x.country,"vdem_electoral_dem":x.electdem.round(3),
    "vdem_liberal_dem":x.libdem.round(3),"gdppc_ppp_2021usd":x.gdp.round(0),"mys_best":x.mys.round(2),
    "hlo":x.hlo.round(1),"learning_adj_yrs_school":x.lays.round(2),"resource_rents_gdp":x.resrents.round(2),
    "predicted_electoral_dem":x.pred.round(3),"democracy_gap":x.resid.round(3)}).sort_values("democracy_gap")

w = pd.read_csv(os.path.join(CLEAN,"wcde.csv"))
w = w[w.year.between(1950,2025)].copy()
w["country"] = w.iso3.map(p.drop_duplicates("iso3").set_index("iso3").country).fillna(w["name"])
w["status"] = np.where(w.year<=2020, "reconstruction/estimate", "projection (SSP2)")
wc = pd.DataFrame({"iso3":w.iso3,"country":w.country,"year":w.year,"age_group":w.age.str.replace("--","–"),
    "wcde_noschool":w.noed.round(2),"wcde_mys":w.mys.round(2),"status":w.status}).sort_values(["iso3","year","age_group"])

m = pd.read_csv(os.path.join(CLEAN,"morocco_by_source.csv"))
SRC = {"Barro-Lee v3":("Barro & Lee (2013), v3 2021 update","https://barrolee.github.io/BarroLeeDataSet/"),
       "UNESCO UIS":("UIS indicator MYS.1T8.AG25T99, Feb-2026 release; latest Moroccan observation","https://api.uis.unesco.org/api/public/documentation"),
       "UNDP HDR":("UNDP Human Development Report, via Our World in Data","https://ourworldindata.org/grapher/average-years-of-schooling"),
       "HCP, RGPH census":("HCP, RGPH 2024 principal results (17 Dec 2024)","https://www.hcp.ma/downloads/RGPH-2024_t22752.html"),
       "Wittgenstein v3":("Wittgenstein Centre WCDE v3.3, SSP2 (K.C. et al. 2024)","https://dataexplorer.wittgensteincentre.org/wcde-v3/")}
m["citation"]=m.Source.map(lambda s:SRC[s][0]); m["url"]=m.Source.map(lambda s:SRC[s][1])
m = m.round(2)

g = pd.read_csv(os.path.join(CLEAN,"edu_gini.csv")).round(3)

TABLES = {"panel_country_year":panel, "democratic_transitions":trans, "crosssection_2019_2023":xs,
          "wcde_attainment_by_age":wc, "morocco_schooling_by_source":m, "education_gini_2015":g}
for n,df in TABLES.items():
    df.to_csv(os.path.join(REL,"data",f"{n}.csv"), index=False)

# ------------------------------------------------------------------ codebook
cb=[]
for k,(old,label,unit,src,dec) in V.items():
    if k not in panel: continue
    cols=[k]+[c for c in ("year","iso3") if c!=k]
    s=panel[cols].dropna(subset=[k])
    cov=f"{int(s.year.min())}–{int(s.year.max())}" if len(s) else "—"
    cb.append({"variable":k,"label":label,"unit":unit,"source":src,"years":cov,
               "units_covered":s.iso3.nunique(),"non_missing":len(s)})
CB=pd.DataFrame(cb)
EXTRA = pd.DataFrame([
 ("democratic_transitions","transition_year","First year of V-Dem RoW ≥ 2 after a year < 2","year","constructed from V-Dem"),
 ("democratic_transitions","survived_5y / survived_10y","1 if RoW stayed ≥ 2 for 5 / 10 following years; blank if not yet observable","0/1","constructed"),
 ("democratic_transitions","wcde_noschool_25plus / wcde_mys_25plus","Same measures from Wittgenstein Centre, nearest 5-year point","% / years","WCDE v3.3"),
 ("crosssection_2019_2023","predicted_electoral_dem","Fitted value from OLS of electoral democracy on log GDP pc + mys_best (151 countries, pop > 1m)","0–1","constructed"),
 ("crosssection_2019_2023","democracy_gap","Actual minus predicted electoral democracy","index points","constructed"),
 ("wcde_attainment_by_age","status","≤2020 reconstruction/estimate; 2025 projection under SSP2","text","WCDE v3.3"),
 ("education_gini_2015","edu_gini","Education Gini, Thomas-Wang-Fan direct method, durations 0/3/6/9/12/14/16","0–1","constructed from Barro-Lee v3"),
], columns=["table","variable","definition","unit","source"])

with open(os.path.join(REL,"CODEBOOK.md"),"w") as f:
    f.write("# Codebook\n\nAll files are UTF-8 CSV, one row per unit of observation, blank = missing.\n\n")
    f.write("## panel_country_year.csv\nOne row per country-year, 1900–2026. "
            f"{panel.iso3.nunique()} units ({panel[panel.historical_state].iso3.nunique()} historical polities), "
            f"{len(panel):,} rows. Regional and income-group aggregates are excluded.\n\n")
    f.write(CB.to_markdown(index=False)+"\n\n")
    f.write("## Other tables\n\n"+EXTRA.to_markdown(index=False)+"\n\n")
    f.write("## Handling notes\n\n"
      "- **Interpolation.** Barro-Lee is observed every five years. Annual values in between are linear "
      "interpolations and are flagged `bl_interpolated = TRUE`. Filter on it for observed-only work.\n"
      "- **Spliced series.** `mys_best` joins Barro-Lee (ages 25–64) with UNDP (ages 25+). The two differ in "
      "definition; `mys_best_source` records which applies to each row.\n"
      "- **Harmonised codes.** Barro-Lee's legacy codes ROM (Moldova) and SER (Serbia) are recoded to MDA "
      "and SRB; V-Dem's Kosovo (OWID_KOS) to the World Bank's XKX.\n"
      "- **PISA** columns come from World Bank EdStats and stop in 2018; Morocco's PISA 2022 scores "
      "(365 / 339 / 365) are cited in the notes from the OECD, not stored here.\n")

# ------------------------------------------------------------------ sources & licences
with open(os.path.join(REL,"SOURCES_AND_LICENSES.md"),"w") as f:
    f.write("""# Sources and licences

This package contains **derived variables**, not redistributed provider files. The raw
files are downloaded by `code/01_fetch.py` from the providers below.

**Licence of this package: CC BY-SA 4.0.** It includes variables derived from V-Dem,
which is published under CC BY-SA 4.0; its ShareAlike clause requires derivative
datasets to carry the same licence. Cite this package *and* each original source.

| Source | Used for | Terms | Cite as |
|---|---|---|---|
| V-Dem v15 (via Our World in Data) | democracy indices, regime type | **CC BY-SA 4.0** (verified) | Coppedge et al., V-Dem Dataset v15; Lührmann, Tannenberg & Lindberg (2018) for RoW |
| Barro-Lee v3 (2021 update) | attainment 1950–2015 | No explicit licence stated; citation required | Barro & Lee (2013), *JDE* 104: 184–198 |
| Wittgenstein Centre WCDE v3.3 | attainment by age 1950–2025 | **No licence declared** by the provider (its Zenodo record carries no licence metadata); citation required | K.C. et al. (2024), IIASA WP-24-003 |
| World Bank WDI, EdStats, HCI | income, enrolment, literacy, learning | **CC BY 4.0** (verified, World Bank Data Catalog) | World Bank, *World Development Indicators* (July 2026) |
| Maddison Project 2023 (via OWID) | long-run GDP per capita | **CC BY 4.0** (verified) | Bolt & van Zanden (2024), Maddison Project Database 2023 |
| UNDP HDR (via OWID) | mean years of schooling 25+ | see provider terms | UNDP, *Human Development Report* |
| UNESCO UIS | Morocco cross-check only | see provider terms | UIS, February 2026 data release |
| HCP, RGPH 2024 | Morocco census figures | public statistics | Haut-Commissariat au Plan (2024) |

Licences marked "verified" were checked against the provider's own terms on 2026-10-01.
"see provider terms" means the licence was not re-verified for this release; check it
before redistributing the *raw* files. Our World in Data's own processing is CC BY 4.0 and
is attributed as "processed by Our World in Data"; the underlying providers' terms still apply.

**Two sources used by the extended analysis (`code/09`–`14`) are deliberately absent from
this package.** Afrobarometer Round 9 respondent-level data are copyrighted and may not be
redistributed: `code/12_afrobarometer.py` downloads them from afrobarometer.org, and only
weighted aggregates appear in the tables. Cite them as "Afrobarometer Data, 39 countries,
Round 9, 2021–2023, available at http://www.afrobarometer.org". V-Dem v16 (used directly
rather than via OWID) is likewise fetched by `code/09_fetch_extended.py`; cite
https://doi.org/10.23696/vdemds26.
""")

# ------------------------------------------------------------------ README
with open(os.path.join(REL,"README.md"),"w") as f:
    f.write(f"""# Morocco: human capital and democratisation — data package

Compiled {RELEASE_DATE} by A. Salaheddine. Rebuild end to end with `code/01_fetch.py` → `code/08_release.py`.

| File | Rows | Unit |
|---|---|---|
""" + "\n".join(f"| `data/{n}.csv` | {len(df):,} | " + {
        "panel_country_year":"country-year, 1900–2026",
        "democratic_transitions":"one democratic transition (V-Dem RoW)",
        "crosssection_2019_2023":"country, 2019–23 averages",
        "wcde_attainment_by_age":"country-year-age group, 1950–2025",
        "morocco_schooling_by_source":"source × year, Morocco",
        "education_gini_2015":"country, 2015"}[n] + " |" for n,df in TABLES.items()) + """
| `Morocco_democratisation_data.xlsx` | — | all tables + codebook + sources, one workbook |

Read `CODEBOOK.md` before use — in particular the interpolation flag and the spliced
schooling series. Licence and citations: `SOURCES_AND_LICENSES.md`.
""")

# the same source/licence table as SOURCES_AND_LICENSES.md, for the Sources sheet of the workbook
SOURCES_TBL = pd.DataFrame([
 ("V-Dem v15 (via Our World in Data)","democracy indices, regime type","CC BY-SA 4.0 (verified)","Coppedge et al., V-Dem Dataset v15; Lührmann, Tannenberg & Lindberg (2018) for RoW"),
 ("Barro-Lee v3 (2021 update)","attainment 1950–2015","No explicit licence stated; citation required","Barro & Lee (2013), JDE 104: 184–198"),
 ("Wittgenstein Centre WCDE v3.3","attainment by age 1950–2025","No licence declared by the provider; citation required","K.C. et al. (2024), IIASA WP-24-003"),
 ("World Bank WDI, EdStats, HCI","income, enrolment, literacy, learning","CC BY 4.0 (verified, World Bank Data Catalog)","World Bank, World Development Indicators (July 2026)"),
 ("Maddison Project 2023 (via OWID)","long-run GDP per capita","CC BY 4.0 (verified)","Bolt & van Zanden (2024), Maddison Project Database 2023"),
 ("UNDP HDR (via OWID)","mean years of schooling 25+","see provider terms","UNDP, Human Development Report"),
 ("UNESCO UIS","Morocco cross-check only","see provider terms","UIS, February 2026 data release"),
 ("HCP, RGPH 2024","Morocco census figures","public statistics","Haut-Commissariat au Plan (2024)"),
 ("This package","—","CC BY-SA 4.0, required by V-Dem's ShareAlike clause","Salaheddine, A. (2026). Morocco: human capital and democratisation — data package"),
], columns=["Source","Used for","Terms","Cite as"])

# ------------------------------------------------------------------ Excel workbook
from openpyxl.styles import Font, PatternFill, Alignment
import tempfile, openpyxl
xl = os.path.join(REL,"Morocco_democratisation_data.xlsx")
xl_tmp = os.path.join(tempfile.mkdtemp(), "wb.xlsx")   # write outside synced folders, then move
with pd.ExcelWriter(xl_tmp, engine="openpyxl") as wr:
    pd.DataFrame({"Morocco: human capital and democratisation — data package":[
        "Sheets: Codebook, Sources, then one sheet per table.",
        "Blank cells are missing values.",
        "Barro-Lee annual values between 5-year observations are interpolated (bl_interpolated = TRUE).",
        "mys_best splices Barro-Lee 25–64 with UNDP 25+; see mys_best_source.",
        "Licence: CC BY-SA 4.0 (inherits from V-Dem). Cite each original source."]}).to_excel(wr, sheet_name="README", index=False)
    CB.to_excel(wr, sheet_name="Codebook", index=False)
    EXTRA.to_excel(wr, sheet_name="Codebook_other_tables", index=False)
    SOURCES_TBL.to_excel(wr, sheet_name="Sources", index=False)
    pd.read_csv(os.path.join(REL,"data","morocco_schooling_by_source.csv")).to_excel(wr, sheet_name="Morocco_by_source", index=False)
    for n,df in TABLES.items():
        if n!="morocco_schooling_by_source": df.to_excel(wr, sheet_name=n[:31], index=False)
    for ws in wr.book.worksheets:
        ws.freeze_panes="A2"
        for c in ws[1]:
            c.font=Font(bold=True,color="FFFFFF"); c.fill=PatternFill("solid",fgColor="2A78D6")
            c.alignment=Alignment(wrap_text=True,vertical="top")
        for col in ws.columns:
            w_=max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:300])
            ws.column_dimensions[col[0].column_letter].width=min(max(9,w_+2),60)

openpyxl.load_workbook(xl_tmp, read_only=True).close()   # raises if the file is not a valid workbook
shutil.move(xl_tmp, xl)
assert os.path.getsize(xl) > 100_000, "workbook suspiciously small"

for root,_,fs in os.walk(REL):
    for fn in sorted(fs):
        fp=os.path.join(root,fn); print(f"  {os.path.relpath(fp,REL):48s} {os.path.getsize(fp)/1024:8.0f} KB")
