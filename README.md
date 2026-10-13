# Morocco: human capital and democratisation — an empirical gap analysis

Tests whether Morocco's income and education levels constitute a binding constraint on a
full democratic transition, benchmarked against every democratic transition since 1960.

## To share the data
`release/` is the shareable package: 6 curated CSVs, one Excel workbook, `CODEBOOK.md`,
`SOURCES_AND_LICENSES.md`. Licence **CC BY-SA 4.0** (inherited from V-Dem).
Code is MIT; see `LICENSE`. Two inputs are deliberately not redistributed: the
Afrobarometer respondent-level file (copyrighted) and the raw provider files generally —
the fetch scripts download them, and `CHECKSUMS.sha256` identifies the exact vintage used.

## How this repository is organised
Every figure and table sits in one of two folders, and the split is the point of the
structure rather than a filing convenience:

| | |
|---|---|
| `figures/facts/`, `tables/facts/` | **Measured quantities** — a share, a count, a mean, a percentile, a distribution, a published index, an association described as what it is. 26 figures, 31 tables. |
| `figures/models/`, `tables/models/` | **Estimates from a fitted model** — hazards, counterfactuals, projections, a residual read as a shortfall, replications of causal claims. Exploratory. 7 figures, 15 tables. |

Nothing has been deleted and nothing is hidden. The separation exists so the descriptive
results can be read and cited on their own, without the model-based ones being quoted as
though they rested on the same evidence. Each folder carries a `README.md` listing what is
in it and why; the classification itself, with a one-line reason per output, is
[`code/tiers.py`](code/tiers.py) — move a name between its two dicts and the file moves on
the next run.

## Read this first
- `notes/extended_analysis.pdf` — **the full paper**, 36 p.: cohorts, hazard models,
  V-Dem component arithmetic, Afrobarometer micro-evidence.
- `notes/note_de_synthese_FR.pdf` — **note de synthèse (français)**, 7 p.
- `notes/synthesis_note_EN.pdf` — **synthesis note (English)**, 7 p.
  (Markdown sources sit beside them; rebuild with `07_make_pdf.py` and `14_make_pdf_extended.py`.)
- `notes/gap_analysis.md` — the first technical write-up: findings, tables, literature, caveats.

## Reproduce
```bash
pip install -r requirements.txt
cd code
# --- the first analysis (notes/gap_analysis.md and the two synthesis notes)
python3 01_fetch.py            # ALL raw data: WB WDI/EdStats, Barro-Lee v3, V-Dem/Maddison/UNDP via OWID,
                               #   Wittgenstein Centre, ISO/M49 map, WB country metadata (validated)
python3 01b_fetch_hci.py       # World Bank Human Capital Index (HLO, LAYS)
python3 01c_fetch_pisa.py      # PISA / TIMSS via EdStats
python3 02_build.py            # -> data/clean/panel.csv, transitions.csv
python3 03_analysis.py         # -> tables T1–T7, key_numbers.json
python3 03b_supplementary.py   # -> tables T11–T13 (education Gini, survival, years behind)
python3 05_vintage.py          # -> source reconciliation, WCDE benchmark (T8–T10 inputs)
python3 04_figures.py          # -> figures F1–F10
python3 06_figures_vintage.py  # -> figures F11–F12
python3 07_make_pdf.py         # -> notes/note_de_synthese_FR.pdf, synthesis_note_EN.pdf
python3 08_release.py          # -> release/  (shareable package)
# --- the extended analysis (notes/extended_analysis.pdf)
python3 09_fetch_extended.py   # WCDE epop/bprop/bmys SSP1–3, V-Dem v16, Afrobarometer R9, WDI labour series
python3 10_cohorts.py          # -> data/clean/ext/, tables T14–T19
python3 11_models.py           # -> T20–T24 (margins, Barro, hazard, expectation model)
python3 11b_components.py      # -> T25–T28 (V-Dem components, counterfactuals, Campante-Chor)
python3 12_afrobarometer.py    # -> T29–T32 (survey gradients, post-stratification)
python3 13_figures_extended.py # -> figures F13–F28
python3 14_make_pdf_extended.py# -> notes/extended_analysis.pdf
# --- the urban/rural check, on Moroccan commune data
python3 16_fetch_tafra.py      # Tafra open data: RGPH 2014 by commune, communal and legislative results
python3 17_urban_rural.py      # -> data/clean/ext/commune_panel.csv.gz, tables T33–T38
python3 18_figures_urban_rural.py  # -> figures F29–F32
# --- optional
python3 15_checksums.py        # verify data/raw/ against CHECKSUMS.sha256
python3 tiers.py               # how many outputs are facts, how many are models
python3 tiers.py --write-indexes   # regenerate the README label in each output folder
```
Dependencies are pinned in `requirements.txt`: `pandas numpy matplotlib statsmodels scipy
certifi tabulate jinja2 pyreadr pyreadstat openpyxl`, plus `pandoc` and a TeX distribution
with `xelatex` for the PDFs. `pyreadr` reads the Wittgenstein `.rds` files and `pyreadstat`
the Afrobarometer `.sav`.
(This Python build ships without root certificates; the fetch scripts point urllib at
`certifi`.)

**Two portability notes.** The two PDF steps need the fonts Charter, Helvetica Neue and
Menlo, which ship with macOS; elsewhere install them or change the font variables in
`07_make_pdf.py` / `14_make_pdf_extended.py`, or `xelatex` stops on a missing font. Nothing
else depends on them — figures fall back to DejaVu Sans, which changes their look but no
number. Second, the World Bank API calls pass an explicit `date=1960:2026` range; without
it the API returns only its own default year window, which it narrowed in 2026 (adult
literacy came back as 176 observations instead of 2,804). Do not remove it.

## Outputs
**Figures** (PDF for LaTeX, PNG for slides)

| | |
|---|---|
| `F1_modernization_cloud` | Democracy vs income and vs schooling, Morocco located |
| `F2_transition_cloud` | Income × schooling at 115 democratic transitions vs Morocco today |
| `F3_percentiles` | Morocco's percentile in the transition distribution, three variables |
| `F4_learning_gap` | Expected vs learning-adjusted years of school |
| `F5_composition` | Adult attainment composition, Morocco vs countries at their transition |
| `F6_democracy_deficit` | Actual vs predicted democracy; the Arab deficit |
| `F7_sequencing` | Schooling paths 1950–2015 with transition years marked |
| `F8_gender_gap` | Adults with no schooling, by sex |
| `F9_education_gini` | Education Gini (Thomas-Wang-Fan) |
| `F10_morocco_trajectory` | Morocco's schooling vs its regime, 1950–2025 |
| `F11_source_reconciliation` | Barro-Lee vs Wittgenstein vs UIS vs UNDP vs HCP census |
| `F12_two_electorates` | Morocco's cohorts placed in the transition distribution |
| `F13`–`F18` | Generational gap, education pyramids, birth cohorts, statistical twins, gender × age, demographic metabolism |
| `F19`–`F24` | Cohort trajectories, margin horse race, hazard model, expectation model, V-Dem components, counterfactual waterfall |
| `F25`–`F28` | Campante-Chor graduate squeeze, royal reference class, Afrobarometer Morocco, 39-country comparison |
| `F29`–`F32` | Urban and rural education structures, turnout against schooling across 1,538 communes, the turnout gap at every election since 2002, schooling deciles and the schooling of those elected |
| `F33` | The same census tables on both vintages, 2014 against 2024 |

**Tables** (`.csv`, `.md`, `.tex`) — T1 Morocco fact sheet · T2 transition distribution ·
T3 benchmark transitions · T4 human-capital profile · T5/T5b cross-section and MENA deficit ·
T6 quality of democracy · T7 within-country panel · T8 source contrast ·
T9 benchmark robustness · T10 cohorts · T11 education Gini ·
T12 post-transition outcomes · T13 years behind · T14–T19 cohort structure (generational gap,
birth cohorts, statistical twins, gender, metabolism, royal democratisations) ·
T20–T24 models (margins, Barro 1999, hazard, Morocco's structural hazard, expectation) ·
T25–T28 institutional anatomy (V-Dem components, counterfactuals, Campante-Chor, educated
unemployment) · T29–T32 Afrobarometer (cells, regressions, 39-country gradients,
post-stratified projection) · T33–T38 the urban/rural divergence (two education structures,
the four corners of the structure, turnout at every election since 2002, the commune-level
turnout gradient, schooling deciles, who gets elected) · T39–T41 the 2014/2024 census
comparison.

`F33` and `T39`–`T41` are the RGPH 2024 results. They are in the repository but the two
scripts that built them are not: they ran from a scratch directory and were never saved, so
these four outputs cannot currently be reproduced from this code. Restoring them is the open
item; the raw HCP input they were built from is listed in `CHECKSUMS.sha256`.

## Data vintages
WDI (2026-07) · WB Human Capital Index 2020 · Barro-Lee v3 (2021 update, ends 2015) ·
**Wittgenstein Centre WCDE v3.3 (SSP1–3, 1950–2100)** · UNESCO UIS (Feb-2026 release) ·
V-Dem v15 via Our World in Data for scripts 01–08, **V-Dem v16 directly for 09–14** ·
Afrobarometer Round 9 (fieldwork 2021–23, release updated June 2025) · Maddison Project 2023 ·
OECD PISA 2022 · UNDP HDR · HCP *RGPH 2024* · **Tafra open data (CC BY 4.0): RGPH 2014 by commune,
communal elections 2015 and 2021, legislative elections 2002–2021**.

Verified reproducible on 2026-10-01 from code alone, with every raw byte re-downloaded:
all 18 scripts ran clean and 251 of 254 files came back identical to the published ones.

## Headline result
Morocco is richer than 68 % and better schooled than 46 % of all countries at the moment
they democratised, and sits 0.17 points *below* the democracy level its own income and
schooling predict. Its unschooled adult population is larger than 72 % of theirs — but that
is a legacy stock: Moroccans aged 20–39 have 9.1 years of schooling and 10 % unschooled,
better schooled than three-quarters of all democratising *countries* and level with Korea
1988. Compared like for like, against the 20–39-year-olds of those countries rather than
their national averages, the same cohort sits at the 59th percentile while the 40–64 cohort
sits at the 41st — a 4.2-year generational gap, the 5th largest of 200 countries. The
binding constraint is institutional, not educational: no ruling monarchy has democratised
directly in 621 observed country-years, and on V-Dem's own aggregation arithmetic, the components where
Morocco scores low are the executive ones rather than the participation ones (that
recomposition, and the 0.425 its income and schooling predict, are in `models/`, not
`facts/`). The education gap bears on the *quality* of a transition, not
its feasibility. Results verified on two independent attainment datasets (r = 0.96).
