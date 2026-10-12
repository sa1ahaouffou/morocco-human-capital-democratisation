"""
16_fetch_tafra.py -- Moroccan electoral and census microdata from Tafra (Rabat).

Tafra is a Moroccan research association that has digitised and standardised the results the
Ministry of the Interior and the Chamber of Representatives publish only as scanned tables.
Its files carry the one thing the international datasets cannot supply for this project:
*within-country* variation, at the level of the 1,538 communes, on both education and voting.

Licence: CC BY 4.0 (stated on the 'notes' sheet of every file). Required citation, e.g.
  "Recensement Général de la Population et de l'Habitat 2014", Association Tafra, Rabat, 2019.
The resource URLs below are the ones linked from https://tafra.ma/donnees/ (read 2026-10-03);
the files live on openAFRICA, whose HTML pages sit behind a bot challenge while these direct
download links do not.

Writes to data/raw/tafra/. Nothing here is redistributed: see .gitignore.
"""
import os, ssl, time
import urllib.request
import certifi
import pandas as pd

SSLCTX = ssl.create_default_context(cafile=certifi.where())
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.abspath(os.path.join(HERE, "..", "data", "raw", "tafra"))
os.makedirs(RAW, exist_ok=True)

BASE = "https://open.africa/dataset/{}/resource/{}/download/{}"
FILES = {
    # --- the ones this analysis uses
    "recensement-general-2014.xlsx":
        ("8653d496-dec3-46a0-a20d-53b4bbf72024", "4212c133-33a7-492b-b819-fb26a68d89ea"),
    "communes-elections-2015-1-0.xlsx":
        ("cecd6468-53f8-4fdb-8269-f1a51c029ac3", "6d21d289-41d2-4f62-8719-e2a4b3aae055"),
    "communes-elections-2021-1-0.xlsx":
        ("cb034784-1331-466c-a02f-713dfad58ef3", "19d637a4-0198-44b2-a3e2-2d7bbda3a7b2"),
    "parlement-elections-2002-1-0.xlsx":
        ("863697f2-bffa-4607-afe7-2c38d6b78adf", "19018416-2921-4abf-87a2-463160892f07"),
    "parlement-elections-2007-1-0.xlsx":
        ("1f48eeec-ff94-46a2-ae8e-ed56b66dd529", "0ec47fad-4f8a-4753-b107-82b0cc76d94c"),
    "parlement-elections-2011-1-0.xlsx":
        ("cb7a294b-9569-4647-b35e-3b1cb6c8028e", "59229632-d062-4e1a-afff-b344b6afdae7"),
    "parlement-elections-2016-1-1.xlsx":
        ("6bf3208e-7e01-456f-9ed8-ff8977e49585", "6c4000e1-5359-43fd-b941-399af34ee54a"),
    "parlement-elections-2021-1-0.xlsx":
        ("595d69a4-c7fc-4e9d-beeb-5d7fc9ec78e5", "cf341829-cd2c-4baa-b679-2b2ee1c1e333"),
    "communes-ipm-2004-2014-1-0.xlsx":       # multidimensional poverty, for robustness
        ("705c2742-2559-406e-a370-6839c688a55f", "7a917de5-c726-46ce-8ee4-7efb506149d8"),
    "communes-idlm-2014-1-0.xlsx":           # local development index
        ("94e9bec6-9480-4341-9228-063891cd8dad", "1cc0829b-218f-4455-bee3-abbd97c60411"),
    # --- the rest of the Tafra catalogue, kept so the raw folder is the whole source
    "communes-elections-2015-circonscription-1-0.xlsx":
        ("78d4690a-a93a-4260-9421-a630a2c3f026", "c647d0a2-f703-473e-a4ba-29dc36140e19"),
    "communes-elections-2021-circonscription-1-0.xlsx":
        ("3e22cbfb-c333-4450-9ad9-6610353b4ad4", "88f9eb1c-256f-4648-be3b-98a1646ab655"),
    "communes-elus-2015-1-0.xlsx":
        ("07a04224-c0ad-4861-9705-0518f5d49dbd", "7ae81ece-1b3d-4cdc-ac49-acd6ba37f6ea"),
    "communes-elus-2021-1-1.xlsx":
        ("3600ddc0-7a66-47be-9adf-cdbaa5ff4ec5", "d333e552-1608-421d-86d1-41455274e764"),
    "regions-elections-2015-1-0.xlsx":
        ("f70d0f66-9904-4023-9d5f-ae2106a5bf78", "74dbefd7-a849-4d39-9cef-6260ee796329"),
    "regions-elus-2015-1-0.xlsx":
        ("e86b7f78-c8b1-4f07-97ab-d20c488038a3", "64bb01cd-610e-4eb5-a95a-9be9a50e8635"),
    "regions-elus-2021-1-0.xlsx":
        ("1511cdd1-1f9a-4edf-be28-2b8184929046", "107f7a63-138a-48ba-ad1f-44c87fc93773"),
    "parlement-elus-tafra-1-6-0.xlsx":
        ("5d84fa5f-144e-4a93-9dc8-de25a4267561", "7a0830a0-c4d0-4929-8028-a41b6822be6d"),
}


def get(fname, ds, res):
    dest = os.path.join(RAW, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  cached  {fname}")
        return
    url = BASE.format(ds, res, fname)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (academic research)"})
    with urllib.request.urlopen(req, timeout=180, context=SSLCTX) as r:
        blob = r.read()
    if blob[:2] != b"PK":                      # an HTML challenge page rather than a workbook
        raise RuntimeError(f"{fname}: not an xlsx (starts {blob[:16]!r})")
    with open(dest, "wb") as f:
        f.write(blob)
    print(f"  fetched {fname}  ({len(blob)/1e6:.2f} MB)")


print(f"Tafra open data -> {RAW}")
for fname, (ds, res) in FILES.items():
    get(fname, ds, res)
    time.sleep(0.5)

# the licence and citation travel with the data
notes = pd.read_excel(os.path.join(RAW, "recensement-general-2014.xlsx"), sheet_name="notes")
lic = " ".join(str(x) for x in notes.iloc[:, 0].tolist() if isinstance(x, str))
assert "CC BY 4.0" in lic, "Tafra licence text changed - re-read it before redistributing anything"
print("\n  licence check: CC BY 4.0 confirmed on the census file's notes sheet")
print(f"  {len(FILES)} files, {sum(os.path.getsize(os.path.join(RAW, f)) for f in FILES)/1e6:.0f} MB")
