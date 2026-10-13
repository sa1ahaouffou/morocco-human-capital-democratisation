# Figures — facts

**Measured quantities.** Everything here is a quantity read off the data: a share, a count, a mean, a
percentile, a distribution, a published index, or an association described as
what it is. Someone who rejects the interpretation in the notes can still use
these numbers.

| figure | why it is here |
|---|---|
| `F10_morocco_trajectory` | two observed series on one time axis |
| `F11_source_reconciliation` | the same quantity as five providers report it |
| `F12_two_electorates` | cohort means placed in the observed transition distribution |
| `F13_generational_gap` | difference between two measured cohort means |
| `F14_education_pyramids` | attainment by age and sex |
| `F15_birth_cohorts` | attainment by year of birth |
| `F16_historical_twins` | nearest neighbours on observed values |
| `F17_gender_age` | attainment by sex and age |
| `F18_demographic_metabolism` | arithmetic on an age structure already alive, under all three scenarios |
| `F19_cohort_trajectories` | published cohort series |
| `F1_modernization_cloud` | published indicators, plotted; the trend line is a smoother, not a model |
| `F23_component_anatomy` | V-Dem's own published component scores |
| `F26_royal_reference_class` | the observed set of monarchies and their attributes |
| `F27_afro_two_electorates` | survey cross-tabulation |
| `F29_two_populations` | census shares, urban against rural |
| `F2_transition_cloud` | observed income and schooling at 115 transitions |
| `F30_turnout_schooling` | turnout against schooling across 1,538 communes; the slope is described, not interpreted |
| `F31_turnout_every_election` | the urban-rural turnout gap at each election |
| `F32_deciles_and_elected` | turnout by schooling decile, and the schooling of those elected |
| `F33_census_2014_2024` | the same census tables, two vintages |
| `F3_percentiles` | Morocco's rank in an observed distribution |
| `F4_learning_gap` | two World Bank indicators, differenced |
| `F5_composition` | attainment shares as published |
| `F7_sequencing` | schooling series with transition years marked |
| `F8_gender_gap` | share with no schooling, by sex |
| `F9_education_gini` | an index computed from the attainment distribution |

The split is defined in [`code/tiers.py`](../../code/tiers.py); moving a name between the two dicts moves the file on the next run.
