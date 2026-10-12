"""
15_checksums.py -- Record, or verify, the exact raw files the published results were built on.

The providers keep revising their series, and the World Bank API has already changed what it
returns by default (see the note in 01_fetch.py). Re-downloading therefore does not guarantee
the same bytes. This writes a manifest of every file in data/raw/ so that anyone rebuilding
can tell whether they hold the same vintage.

    python3 code/15_checksums.py            # verify data/raw/ against CHECKSUMS.sha256
    python3 code/15_checksums.py --write     # (re)create the manifest

Verifying exits 1 if anything is missing or has changed, so it can gate a rebuild.
"""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "data", "raw")
# at the repo root, not inside data/raw/, because that folder is not committed
MANIFEST = os.path.join(ROOT, "CHECKSUMS.sha256")

# where each file comes from, so a mismatch can be chased to its provider
PROVENANCE = {
    "wdi_long":       "World Bank WDI API (01_fetch.py)",
    "edstats_long":   "World Bank EdStats API, Barro-Lee v2.2 mirror (01_fetch.py)",
    "BL_v3":          "Barro-Lee v3, 2021 update (01_fetch.py)",
    "owid_":          "Our World in Data (01_fetch.py)",
    "vdem_electdem":  "V-Dem via Our World in Data (01_fetch.py)",
    "vdem_libdem":    "V-Dem via Our World in Data (01_fetch.py)",
    "vdem_regime":    "V-Dem Regimes of the World via Our World in Data (01_fetch.py)",
    "maddison":       "Maddison Project Database 2023 via OWID (01_fetch.py)",
    "wcde_":          "Wittgenstein Centre WCDE v3.3 (01_fetch.py, 09_fetch_extended.py)",
    "iso_m49":        "UN M49 / ISO country codes (01_fetch.py)",
    "wb_country_meta": "World Bank country metadata (01_fetch.py)",
    "hci_long":       "World Bank Human Capital Index (01b_fetch_hci.py)",
    "pisa_long":      "PISA/TIMSS via World Bank EdStats (01c_fetch_pisa.py)",
    "vdem_v16":       "V-Dem v16 full dataset (09_fetch_extended.py)",
    "afrobarometer":  "Afrobarometer Round 9 — NOT redistributable (09_fetch_extended.py)",
    "wdi_extra":      "World Bank WDI, labour series (09_fetch_extended.py)",
    "recensement-general-2014": "RGPH 2014 by commune, compiled by Tafra, CC BY 4.0 (16_fetch_tafra.py)",
    "communes-":      "Moroccan communal elections, Tafra, CC BY 4.0 (16_fetch_tafra.py)",
    "parlement-":     "Moroccan legislative elections, Tafra, CC BY 4.0 (16_fetch_tafra.py)",
    "regions-":       "Moroccan regional elections, Tafra, CC BY 4.0 (16_fetch_tafra.py)",
}

def provenance(rel):
    base = os.path.basename(rel)
    for k, v in PROVENANCE.items():
        if base.startswith(k) or k in base:
            return v
    return "?"

def walk():
    for dirpath, _, files in os.walk(RAW):
        for f in sorted(files):
            if f.startswith(".") or f == os.path.basename(MANIFEST):
                continue
            p = os.path.join(dirpath, f)
            yield os.path.relpath(p, RAW), p

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def write():
    rows = [(rel, digest(p), os.path.getsize(p)) for rel, p in walk()]
    with open(MANIFEST, "w") as f:
        f.write("# sha256 of every raw input the published results were built on.\n"
                "# Verify with: python3 code/15_checksums.py\n"
                "# sha256  size_bytes  path  (provider)\n")
        for rel, h, n in rows:
            f.write(f"{h}  {n:>12}  {rel}    ({provenance(rel)})\n")
    print(f"  wrote {os.path.relpath(MANIFEST, ROOT)}  ({len(rows)} files, "
          f"{sum(n for _, _, n in rows)/1e6:.0f} MB)")

def verify():
    if not os.path.exists(MANIFEST):
        sys.exit(f"no manifest at {MANIFEST}; run with --write first")
    want = {}
    for line in open(MANIFEST):
        if line.startswith("#") or not line.strip():
            continue
        h, n, rest = line.split(None, 2)
        want[rest.split("    (")[0].strip()] = (h, int(n))
    have = dict(walk())
    bad, missing = [], []
    for rel, (h, n) in sorted(want.items()):
        if rel not in have:
            missing.append(rel); continue
        d = digest(have[rel])
        if d != h:
            bad.append(f"{rel}: expected {h[:12]}… ({n} bytes), got {d[:12]}… "
                       f"({os.path.getsize(have[rel])} bytes) — {provenance(rel)}")
    extra = sorted(set(have) - set(want))
    print(f"  {len(want) - len(bad) - len(missing)}/{len(want)} raw files match the manifest")
    for x in missing: print(f"  MISSING  {x}")
    for x in bad:     print(f"  CHANGED  {x}")
    for x in extra:   print(f"  extra (not in manifest)  {x}")
    if bad or missing:
        sys.exit(1)

if __name__ == "__main__":
    write() if "--write" in sys.argv else verify()
