# Sources and licences

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
