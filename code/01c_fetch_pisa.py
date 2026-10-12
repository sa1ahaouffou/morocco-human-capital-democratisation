import os, json, time, ssl, certifi, urllib.request
import pandas as pd
RAW = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","data","raw"))
CTX = ssl.create_default_context(cafile=certifi.where())
def wb(code, source):
    rows, page = [], 1
    while True:
        url=(f"https://api.worldbank.org/v2/country/all/indicator/{code}"
             f"?format=json&per_page=20000&page={page}&source={source}&date=1960:2026")
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (research)"})
        with urllib.request.urlopen(req, timeout=180, context=CTX) as r: js=json.loads(r.read().decode())
        if not isinstance(js,list) or len(js)<2 or js[1] is None: break
        for d in js[1]:
            if d.get("value") is None: continue
            rows.append({"iso3":d.get("countryiso3code"),"country":d["country"]["value"],
                         "year":int(d["date"]),"indicator":code,"value":d["value"]})
        if page>=js[0]["pages"]: break
        page+=1
    return pd.DataFrame(rows)
out=[]
for c in ["LO.PISA.MAT","LO.PISA.REA","LO.PISA.SCI","LO.PISA.MAT.LO","LO.TIMSS.MAT4"]:
    try:
        d=wb(c,12); print(f"  {c:16s} {len(d):6d} obs"); out.append(d)
    except Exception as e: print(f"  {c:16s} FAILED {e}")
    time.sleep(0.3)
pd.concat(out, ignore_index=True).to_csv(os.path.join(RAW,"pisa_long.csv"), index=False)
print("saved pisa_long.csv")
