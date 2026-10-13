# Tables — facts

**Measured quantities.** Everything here is a quantity read off the data: a share, a count, a mean, a
percentile, a distribution, a published index, or an association described as
what it is. Someone who rejects the interpretation in the notes can still use
these numbers.

| table | why it is here |
|---|---|
| `T10_cohorts` | measured cohort means |
| `T11_education_gini` | index computed from the distribution |
| `T12_after_transition` | observed outcomes before and after transition |
| `T12b_by_tercile` | the same, split by tercile |
| `T13_years_behind` | a difference in years |
| `T14_generational_gap` | difference between two cohort means, ranked |
| `T15_birth_cohort_timing` | the year each cohort crossed a threshold |
| `T16_historical_twins` | nearest neighbours on observed values |
| `T17_gender_cohort` | attainment by sex and cohort |
| `T18_demographic_metabolism` | arithmetic on an age structure already alive |
| `T19_royal_democratisations` | the observed list of cases |
| `T1_morocco_factsheet` | measured quantities with their sources |
| `T22a_risk_set` | counts of country-years at risk, by regime type: the 0-of-621 fact itself |
| `T25_components` | V-Dem's own published component scores |
| `T28_educated_unemployment` | ratio of two published unemployment rates |
| `T29_morocco_two_electorates` | survey cells, weighted |
| `T2_transition_distribution` | percentiles of an observed distribution |
| `T33_two_populations` | census shares, urban against rural |
| `T34_four_corners` | census shares by sex and place |
| `T35_turnout_every_election` | recorded turnout at each election |
| `T36_turnout_gradient` | a slope across 1,538 communes, with region fixed effects, described as a gradient |
| `T37_schooling_deciles` | turnout by decile of schooling |
| `T38_who_is_elected` | the attainment of those elected |
| `T39_divergence_2014_2024` | two census vintages, differenced |
| `T3_benchmark_transitions` | observed values at named transitions |
| `T40_four_corners_2024` | census shares by sex and place, 2024 |
| `T41_turnout_on_both_censuses` | the same gradient on both census vintages |
| `T4_education_profile` | attainment shares |
| `T6_quality_of_democracy` | published V-Dem indices |
| `T8_source_contrast` | one quantity across providers |
| `T9_benchmark_robustness` | the same percentile on a second dataset |

The split is defined in [`code/tiers.py`](../../code/tiers.py); moving a name between the two dicts moves the file on the next run.
