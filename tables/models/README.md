# Tables — models

**Estimates, not measurements.** Everything here depends on a specification. These are fitted hazards,
counterfactuals, projections, a residual read as a shortfall, and replications
of causal claims in the literature. They are exploratory: read them as what the
data look like under one set of assumptions, not as findings on the same footing
as the measured quantities in `../facts/`. The monarchy hazard in particular is
fitted on a cell with 621 country-years and no events at all, so its coefficient
is not identified; the underlying count is in `tables/facts/T22a_risk_set`.

| table | why it is here |
|---|---|
| `T20_which_margin` | regression horse race |
| `T21_barro_replication` | replication of Barro (1999) |
| `T22_hazard` | fitted hazard model |
| `T22c_gap_robustness` | hazard model under alternative specifications |
| `T23_morocco_hazard` | model-implied hazard for one country |
| `T23b_hazard_decomposition` | decomposition of a fitted hazard |
| `T24_expectation_model` | model-implied expectation |
| `T26_counterfactuals` | index recomputed under assumed component values |
| `T27_campante_chor` | replication of Campante and Chor |
| `T30_morocco_regressions` | survey regressions |
| `T31_afro_comparative` | fitted gradients across 39 countries |
| `T32_poststratified_projection` | survey gradients projected to 2060 |
| `T5_crosssection` | OLS used to predict a democracy level |
| `T5b_mena_deficit` | mean residuals by region |
| `T7_panel_fe` | within-country fixed-effects panel |

The split is defined in [`code/tiers.py`](../../code/tiers.py); moving a name between the two dicts moves the file on the next run.
