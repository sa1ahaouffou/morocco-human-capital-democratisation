# Figures — models

**Estimates, not measurements.** Everything here depends on a specification. These are fitted hazards,
counterfactuals, projections, a residual read as a shortfall, and replications
of causal claims in the literature. They are exploratory: read them as what the
data look like under one set of assumptions, not as findings on the same footing
as the measured quantities in `../facts/`. The monarchy hazard in particular is
fitted on a cell with 621 country-years and no events at all, so its coefficient
is not identified; the underlying count is in `tables/facts/T22a_risk_set`.

| figure | why it is here |
|---|---|
| `F20_which_margin` | regression horse race between attainment margins |
| `F21_hazard` | fitted transition hazard |
| `F22_structural_expectation` | model-implied expectation |
| `F24_waterfall` | counterfactual recomposition of the index |
| `F25_schooling_opportunity` | replication of Campante and Chor |
| `F28_afro_comparative` | fitted gradients across 39 countries |
| `F6_democracy_deficit` | residual from a two-variable OLS (R2 = 0.22) read as a shortfall |

The split is defined in [`code/tiers.py`](../../code/tiers.py); moving a name between the two dicts moves the file on the next run.
