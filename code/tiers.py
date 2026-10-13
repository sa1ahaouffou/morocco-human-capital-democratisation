"""
tiers.py -- Which tier every figure and table belongs to, and why.

Two tiers, applied to `figures/` and `tables/` alike:

  facts/   A quantity measured in the data: a share, a count, a mean, a percentile, a
           distribution, a published index read off its source, or an association
           described as what it is. Someone who disagrees with the interpretation can
           still use the number.

  models/  An estimate whose purpose is inference: a fitted hazard, a counterfactual, a
           projection, a residual read as a shortfall, or a replication of a causal claim
           in the literature. These depend on a specification, and several of them rest on
           thin data -- the monarchy hazard is fitted on a cell with 621 country-years and
           no events at all.

Nothing is deleted by the split and nothing is hidden. It exists so that the descriptive
results can be read, cited and published on their own, without the model-based ones being
quoted as if they carried the same weight. Moving a name from one dict to the other moves
the output on the next run; the reason attached to each is the argument for where it sits,
and is meant to be argued with.
"""
import os
import sys

FACTS, MODELS = "facts", "models"

FIGURES = {
    "F1_modernization_cloud":     (FACTS,  "published indicators, plotted; the trend line is a smoother, not a model"),
    "F2_transition_cloud":        (FACTS,  "observed income and schooling at 115 transitions"),
    "F3_percentiles":             (FACTS,  "Morocco's rank in an observed distribution"),
    "F4_learning_gap":            (FACTS,  "two World Bank indicators, differenced"),
    "F5_composition":             (FACTS,  "attainment shares as published"),
    "F6_democracy_deficit":       (MODELS, "residual from a two-variable OLS (R2 = 0.22) read as a shortfall"),
    "F7_sequencing":              (FACTS,  "schooling series with transition years marked"),
    "F8_gender_gap":              (FACTS,  "share with no schooling, by sex"),
    "F9_education_gini":          (FACTS,  "an index computed from the attainment distribution"),
    "F10_morocco_trajectory":     (FACTS,  "two observed series on one time axis"),
    "F11_source_reconciliation":  (FACTS,  "the same quantity as five providers report it"),
    "F12_two_electorates":        (FACTS,  "cohort means placed in the observed transition distribution"),
    "F13_generational_gap":       (FACTS,  "difference between two measured cohort means"),
    "F14_education_pyramids":     (FACTS,  "attainment by age and sex"),
    "F15_birth_cohorts":          (FACTS,  "attainment by year of birth"),
    "F16_historical_twins":       (FACTS,  "nearest neighbours on observed values"),
    "F17_gender_age":             (FACTS,  "attainment by sex and age"),
    "F18_demographic_metabolism": (FACTS,  "arithmetic on an age structure already alive, under all three scenarios"),
    "F19_cohort_trajectories":    (FACTS,  "published cohort series"),
    "F20_which_margin":           (MODELS, "regression horse race between attainment margins"),
    "F21_hazard":                 (MODELS, "fitted transition hazard"),
    "F22_structural_expectation": (MODELS, "model-implied expectation"),
    "F23_component_anatomy":      (FACTS,  "V-Dem's own published component scores"),
    "F24_waterfall":              (MODELS, "counterfactual recomposition of the index"),
    "F25_schooling_opportunity":  (MODELS, "replication of Campante and Chor"),
    "F26_royal_reference_class":  (FACTS,  "the observed set of monarchies and their attributes"),
    "F27_afro_two_electorates":   (FACTS,  "survey cross-tabulation"),
    "F28_afro_comparative":       (MODELS, "fitted gradients across 39 countries"),
    "F29_two_populations":        (FACTS,  "census shares, urban against rural"),
    "F30_turnout_schooling":      (FACTS,  "turnout against schooling across 1,538 communes; the slope is described, not interpreted"),
    "F31_turnout_every_election": (FACTS,  "the urban-rural turnout gap at each election"),
    "F32_deciles_and_elected":    (FACTS,  "turnout by schooling decile, and the schooling of those elected"),
    "F33_census_2014_2024":       (FACTS,  "the same census tables, two vintages"),
}

TABLES = {
    "T1_morocco_factsheet":          (FACTS,  "measured quantities with their sources"),
    "T2_transition_distribution":    (FACTS,  "percentiles of an observed distribution"),
    "T3_benchmark_transitions":      (FACTS,  "observed values at named transitions"),
    "T4_education_profile":          (FACTS,  "attainment shares"),
    "T5_crosssection":               (MODELS, "OLS used to predict a democracy level"),
    "T5b_mena_deficit":              (MODELS, "mean residuals by region"),
    "T6_quality_of_democracy":       (FACTS,  "published V-Dem indices"),
    "T7_panel_fe":                   (MODELS, "within-country fixed-effects panel"),
    "T8_source_contrast":            (FACTS,  "one quantity across providers"),
    "T9_benchmark_robustness":       (FACTS,  "the same percentile on a second dataset"),
    "T10_cohorts":                   (FACTS,  "measured cohort means"),
    "T11_education_gini":            (FACTS,  "index computed from the distribution"),
    "T12_after_transition":          (FACTS,  "observed outcomes before and after transition"),
    "T12b_by_tercile":               (FACTS,  "the same, split by tercile"),
    "T13_years_behind":              (FACTS,  "a difference in years"),
    "T14_generational_gap":          (FACTS,  "difference between two cohort means, ranked"),
    "T15_birth_cohort_timing":       (FACTS,  "the year each cohort crossed a threshold"),
    "T16_historical_twins":          (FACTS,  "nearest neighbours on observed values"),
    "T17_gender_cohort":             (FACTS,  "attainment by sex and cohort"),
    "T18_demographic_metabolism":    (FACTS,  "arithmetic on an age structure already alive"),
    "T19_royal_democratisations":    (FACTS,  "the observed list of cases"),
    "T20_which_margin":              (MODELS, "regression horse race"),
    "T21_barro_replication":         (MODELS, "replication of Barro (1999)"),
    "T22_hazard":                    (MODELS, "fitted hazard model"),
    "T22a_risk_set":                 (FACTS,  "counts of country-years at risk, by regime type: the 0-of-621 fact itself"),
    "T22c_gap_robustness":           (MODELS, "hazard model under alternative specifications"),
    "T23_morocco_hazard":            (MODELS, "model-implied hazard for one country"),
    "T23b_hazard_decomposition":     (MODELS, "decomposition of a fitted hazard"),
    "T24_expectation_model":         (MODELS, "model-implied expectation"),
    "T25_components":                (FACTS,  "V-Dem's own published component scores"),
    "T26_counterfactuals":           (MODELS, "index recomputed under assumed component values"),
    "T27_campante_chor":             (MODELS, "replication of Campante and Chor"),
    "T28_educated_unemployment":     (FACTS,  "ratio of two published unemployment rates"),
    "T29_morocco_two_electorates":   (FACTS,  "survey cells, weighted"),
    "T30_morocco_regressions":       (MODELS, "survey regressions"),
    "T31_afro_comparative":          (MODELS, "fitted gradients across 39 countries"),
    "T32_poststratified_projection": (MODELS, "survey gradients projected to 2060"),
    "T33_two_populations":           (FACTS,  "census shares, urban against rural"),
    "T34_four_corners":              (FACTS,  "census shares by sex and place"),
    "T35_turnout_every_election":    (FACTS,  "recorded turnout at each election"),
    "T36_turnout_gradient":          (FACTS,  "a slope across 1,538 communes, with region fixed effects, described as a gradient"),
    "T37_schooling_deciles":         (FACTS,  "turnout by decile of schooling"),
    "T38_who_is_elected":            (FACTS,  "the attainment of those elected"),
    "T39_divergence_2014_2024":      (FACTS,  "two census vintages, differenced"),
    "T40_four_corners_2024":         (FACTS,  "census shares by sex and place, 2024"),
    "T41_turnout_on_both_censuses":  (FACTS,  "the same gradient on both census vintages"),
}


def tier(name):
    """facts or models, by output name. Unknown names go to facts and say so loudly."""
    for d in (FIGURES, TABLES):
        if name in d:
            return d[name][0]
    print(f"  !! {name} is not classified in tiers.py -- filing under {FACTS}")
    return FACTS


def tier_dir(base, name):
    """The directory this output belongs in, created if need be."""
    p = os.path.join(base, tier(name))
    os.makedirs(p, exist_ok=True)
    return p


def summary():
    for label, d in (("figures", FIGURES), ("tables", TABLES)):
        n = sum(1 for v in d.values() if v[0] == MODELS)
        print(f"  {label}: {len(d) - n} facts, {n} models")




def tpath(base, name, ext):
    """Full path to one output, tier included: tpath(TAB, "T17_gender_cohort", "csv")."""
    return os.path.join(tier_dir(base, name), f"{name}.{ext}")


# --------------------------------------------------------------- the labels on GitHub
HEAD = {
    FACTS: ("Measured quantities",
            "Everything here is a quantity read off the data: a share, a count, a mean, a\n"
            "percentile, a distribution, a published index, or an association described as\n"
            "what it is. Someone who rejects the interpretation in the notes can still use\n"
            "these numbers."),
    MODELS: ("Estimates, not measurements",
             "Everything here depends on a specification. These are fitted hazards,\n"
             "counterfactuals, projections, a residual read as a shortfall, and replications\n"
             "of causal claims in the literature. They are exploratory: read them as what the\n"
             "data look like under one set of assumptions, not as findings on the same footing\n"
             "as the measured quantities in `../facts/`. The monarchy hazard in particular is\n"
             "fitted on a cell with 621 country-years and no events at all, so its coefficient\n"
             "is not identified; the underlying count is in `tables/facts/T22a_risk_set`."),
}


def write_indexes(root):
    """Write the README that labels each folder, from the classification above."""
    for base, d, kind in (("figures", FIGURES, "figure"), ("tables", TABLES, "table")):
        for t in (FACTS, MODELS):
            title, blurb = HEAD[t]
            rows = sorted((k, v[1]) for k, v in d.items() if v[0] == t)
            out = [f"# {base.capitalize()} — {t}", "", f"**{title}.** {blurb}", "",
                   f"| {kind} | why it is here |", "|---|---|"]
            out += [f"| `{k}` | {why} |" for k, why in rows]
            out += ["", f"The split is defined in [`code/tiers.py`](../../code/tiers.py); "
                        f"moving a name between the two dicts moves the file on the next run.", ""]
            p = os.path.join(root, base, t, "README.md")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write("\n".join(out))
        n = sum(1 for v in d.values() if v[0] == MODELS)
        open(os.path.join(root, base, "README.md"), "w").write(
            f"# {base.capitalize()}\n\n"
            f"- [`facts/`](facts/) — {len(d) - n} {kind}s that report a measured quantity.\n"
            f"- [`models/`](models/) — {n} {kind}s that report an estimate from a fitted model.\n\n"
            f"Nothing has been removed: the split only separates what is measured from what is\n"
            f"assumed, so the first can be cited without carrying the second. The classification,\n"
            f"with a one-line reason for each file, is in [`code/tiers.py`](../code/tiers.py).\n")
    print(f"  wrote 6 README.md labels under figures/ and tables/")


if __name__ == "__main__":
    summary()
    if "--write-indexes" in sys.argv:
        write_indexes(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
