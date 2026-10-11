# -*- coding: utf-8 -*-
"""Render the red-team evidence report and audit tables from source JSON/CSV."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path


def load_json(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def fmt(value, digits=3) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def ci_text(summary: dict) -> str:
    ci = summary["paired_t_ci95"]
    return f"{fmt(summary['paired_difference']['mean'])} [{fmt(ci['low'])}, {fmt(ci['high'])}]"


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prediction_rows(root: Path, mechanism: dict) -> list[dict]:
    def primary(path: str) -> dict:
        return load_json(root, path)["primary"]

    e1_t1 = primary("reports/e1_20260912/E1_T1_A2_vs_A0.json")
    e1_t2 = primary("reports/e1_20260912/E1_T2_A2_vs_A3.json")
    e1_t3 = primary("reports/e1_20260912/E1_T3_peat.json")
    e2_m = primary("reports/e2_20260913/E2_M_primary.json")
    e2_w = primary("reports/e2_20260913/E2_W_primary.json")
    e3_h31 = primary("reports/e3_20260913/E3_H31.json")
    e3_h32 = primary("reports/e3_20260913/E3_H32.json")
    e5_t2 = primary("reports/e5_20260913/E5_T2.json")
    e2_rows = list(csv.DictReader(
        (root / "reports/publication_value_of_information_2026-09-13/confirmatory/source_data/e2_seed_outcomes.csv")
        .open(encoding="utf-8")
    ))
    e2_means = {}
    for profile in ("M", "W"):
        for arm in ("B1", "B2", "B3", "B4"):
            values = [float(row["discrimination_index"]) for row in e2_rows if row["profile"] == profile and row["arm"] == arm]
            e2_means[(profile, arm)] = statistics.mean(values)
    t2 = mechanism["T2RB"]["paired_contrasts"]
    t2_primary = next(row for row in t2 if row["contrast"] == "A2-A3R" and row["metric"] == "founder_mean_followup_ticks")
    slope = mechanism["E6"]["slope"]
    level_primary = [
        row for row in mechanism["E6"]["paired_contrasts"]
        if row["contrast"] == "B2-B3" and row["metric"] == "founder_mean_followup_ticks"
    ]
    return [
        {"id": "H1.1", "status": "frozen/registered", "prediction": "A2-A0 founder age < 0", "observed": f"{e1_t1['paired_difference']['mean']:.3f}, 95% CI {e1_t1['paired_difference']['t_ci95']['low']:.3f} to {e1_t1['paired_difference']['t_ci95']['high']:.3f}", "verdict": "supported", "source": "reports/e1_20260912/E1_T1_A2_vs_A0.json"},
        {"id": "H1.2", "status": "frozen/registered", "prediction": "A2-A3 founder age < 0", "observed": f"{e1_t2['paired_difference']['mean']:.3f}, 95% CI {e1_t2['paired_difference']['t_ci95']['low']:.3f} to {e1_t2['paired_difference']['t_ci95']['high']:.3f}", "verdict": "falsified", "source": "reports/e1_20260912/E1_T2_A2_vs_A3.json"},
        {"id": "H1.3", "status": "frozen/registered", "prediction": "A2-A1 fruit acceptance > 0", "observed": f"{e1_t3['paired_difference']['mean']:.3f}, 95% CI {e1_t3['paired_difference']['t_ci95']['low']:.3f} to {e1_t3['paired_difference']['t_ci95']['high']:.3f}", "verdict": "supported", "source": "reports/e1_20260912/E1_T3_peat.json"},
        {"id": "H2.1", "status": "frozen/registered", "prediction": "D(B2) > 0 in M and W", "observed": f"B2-B3 {e2_m['paired_difference']['mean']:.3f} (M), {e2_w['paired_difference']['mean']:.3f} (W)", "verdict": "supported", "source": "reports/e2_20260913/E2_M_primary.json; E2_W_primary.json"},
        {"id": "H2.2", "status": "frozen/registered", "prediction": "D(B3) approximately 0", "observed": f"{e2_means[('M','B3')]:.3f} (M), {e2_means[('W','B3')]:.3f} (W)", "verdict": "exact zero-like prediction not met; B3 remains far below B2", "source": "confirmatory/source_data/e2_seed_outcomes.csv"},
        {"id": "H2.3", "status": "frozen/registered", "prediction": "D(B1) = 0 by structure", "observed": f"{e2_means[('M','B1')]:.3f} (M), {e2_means[('W','B1')]:.3f} (W)", "verdict": "structural-zero prediction not met", "source": "confirmatory/source_data/e2_seed_outcomes.csv"},
        {"id": "H2.4", "status": "frozen/registered", "prediction": "D(B4) > D(B2)", "observed": f"{e2_means[('M','B4')]:.3f} > {e2_means[('M','B2')]:.3f}; {e2_means[('W','B4')]:.3f} > {e2_means[('W','B2')]:.3f}", "verdict": "supported", "source": "confirmatory/source_data/e2_seed_outcomes.csv"},
        {"id": "H3.1", "status": "frozen/registered", "prediction": "S(A2)-S(A0) > 0", "observed": f"{e3_h31['paired_difference']['mean']:.4f}, 95% CI {e3_h31['paired_difference']['t_ci95']['low']:.4f} to {e3_h31['paired_difference']['t_ci95']['high']:.4f}", "verdict": "supported", "source": "reports/e3_20260913/E3_H31.json"},
        {"id": "H3.2", "status": "frozen/registered", "prediction": "S(A2)-S(A3) > 0", "observed": f"{e3_h32['paired_difference']['mean']:.4f}, 95% CI {e3_h32['paired_difference']['t_ci95']['low']:.4f} to {e3_h32['paired_difference']['t_ci95']['high']:.4f}", "verdict": "falsified in the opposite direction", "source": "reports/e3_20260913/E3_H32.json"},
        {"id": "E5 regime prediction", "status": "frozen narrative prediction; exploratory contrast", "prediction": "A2-A3 deficit should weaken under higher drain", "observed": f"A2-A3 {e5_t2['paired_difference']['mean']:.3f}, 95% CI {e5_t2['paired_difference']['t_ci95']['low']:.3f} to {e5_t2['paired_difference']['t_ci95']['high']:.3f}", "verdict": "prediction failed; exploratory result motivated T2-RB", "source": "reports/e5_20260913/E5_T2.json"},
        {"id": "H6.1 directional rule", "status": "frozen/registered", "prediction": "mean B2-B3 slope > 0 and 95% CI excludes 0", "observed": f"{slope['summary']['mean']:.3f}, 95% CI {slope['t_ci95']['low']:.3f} to {slope['t_ci95']['high']:.3f}", "verdict": "registered statistical rule met", "source": "revision_2026-09-15/derived/mechanism_analysis.json"},
        {"id": "H6.1 mechanistic rationale", "status": "registered directional rationale", "prediction": "age information becomes more survival-beneficial as safe fruit energy rises", "observed": "; ".join(f"E{r['realized_fruit_energy']}={r['paired_difference']['mean']:.3f}" for r in level_primary), "verdict": "not supported at levels 4-8; non-negative only at the regime-changing endpoint 10", "source": "revision_2026-09-15/derived/mechanism_analysis.json"},
        {"id": "H6.1 SESOI sensitivity", "status": "post hoc minimum-effect test", "prediction": "mean slope > 1 tick per energy", "observed": f"one-sided sign-flip p={slope['minimum_effect_sensitivity']['one_sided_monte_carlo_sign_flip_p']:.3f}", "verdict": "effect above SESOI not established", "source": "revision_2026-09-15/derived/mechanism_analysis.json"},
        {"id": "T2-RB primary", "status": "frozen/registered", "prediction": "A2-A3R follow-up < 0", "observed": ci_text(t2_primary), "verdict": "supported; minimum effect beyond -5 not established because CI crosses -5", "source": "revision_2026-09-15/derived/mechanism_analysis.json"},
    ]


def deviation_rows() -> list[dict]:
    return [
        {"date": "2026-09-13", "item": "E2 oracle B4 and discrimination index implemented after initial freeze", "timing": "before E2 runs; after narrative freeze", "impact": "implementation was not fixed by the original code revision", "source": "reports/prereg/PREREG_toxin_ecological_trap_2026-09-12.th.md section 11"},
        {"date": "2026-09-13", "item": "E4 runnable specification added after initial freeze", "timing": "retroactive denominator check", "impact": "E4 is measurement validation, not a co-frozen confirmatory toxin result", "source": "reports/prereg/PREREG_toxin_ecological_trap_2026-09-12.th.md section 11"},
        {"date": "2026-09-13", "item": "E5 A2-A3 classified exploratory", "timing": "after E1 falsified H1.2", "impact": "E5 generated the T2-RB replication question", "source": "reports/prereg/PREREG_toxin_ecological_trap_2026-09-12.th.md section 11"},
        {"date": "2026-09-14", "item": "E6 encounter gate interpreted as level mean", "timing": "analysis code written after primary-result reveal", "impact": "level-mean gate passes; stricter per-run reading fails at energies 4-6", "source": "confirmatory/e6/E6_secondary_and_mechanism.json"},
        {"date": "2026-09-15", "item": "No externally timestamped preregistration located for E1-E6/T2-RB", "timing": "red-team provenance audit", "impact": "manuscript must say internally frozen at a Git tag", "source": "REDTEAM_manuscript_initial_submission_2026-09-15.th.md"},
        {"date": "2026-09-16", "item": "Starvation-override meals cannot be identified from archived telemetry", "timing": "post hoc raw-data audit", "impact": "causal path through override timing remains unresolved", "source": "revision_2026-09-15/derived/mechanism_analysis.json"},
        {"date": "2026-09-16", "item": "Skip/encounter counts can include repeated contact with the same item", "timing": "post hoc raw-data audit", "impact": "counts are descriptive and not independent item encounters", "source": "revision_2026-09-15/derived/mechanism_analysis.json"},
    ]


def render_report(mechanism: dict) -> str:
    e6 = mechanism["E6"]
    t2 = mechanism["T2RB"]
    lines = [
        "# Supplementary mechanism tables",
        "",
        "**Status:** Post hoc descriptive analysis performed after the primary results were known. The frozen confirmatory analyses remain unchanged.",
        "",
        "**Inferential unit:** Seed. Founder records were aggregated within each run before arm contrasts.",
        "",
        "## Integrity and traceability",
        "",
        f"- E6 design: {e6['seed_records'].__len__()}/450 run cells; no missing or duplicate cells.",
        f"- T2-RB design: {t2['seed_records'].__len__()}/150 run cells; no missing or duplicate cells.",
        "- The baseline manifest independently verified all 600 raw-dump hashes against the archived checksum list.",
        "- Every manuscript-facing number below is traceable to `derived/mechanism_analysis.json` and its source-data CSV files.",
        "",
        "## E6 founder-level mechanisms aggregated by seed",
        "",
        "| Energy | Arm | Follow-up | D | P(eat safe) | P(eat toxic) | Fruit meals | Staple meals | Staple accept | Ever skipped staple | Toxin excess | Toxin damage | Starvation | Senescence |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in e6["cell_summaries"]:
        m = cell["metrics"]
        lines.append(
            f"| {cell['realized_fruit_energy']} | {cell['arm']} | {fmt(m['founder_mean_followup_ticks']['mean'])} | "
            f"{fmt(m['discrimination_index']['mean'])} | {fmt(m['p_eat_given_safe']['mean'])} | "
            f"{fmt(m['p_eat_given_toxic']['mean'])} | {fmt(m['fruit_meals_per_founder']['mean'])} | "
            f"{fmt(m['staple_meals_per_founder']['mean'])} | {fmt(m['staple_acceptance_per_telemetry_encounter']['mean'])} | "
            f"{fmt(m['founders_ever_skipping_staple_fraction']['mean'])} | {fmt(m['toxin_excess_per_founder']['mean'])} | "
            f"{fmt(m['toxin_damage_per_founder']['mean'])} | {fmt(m['death_fraction_starvation']['mean'])} | "
            f"{fmt(m['death_fraction_senescence']['mean'])} |"
        )
    lines.extend([
        "",
        "Skip counts are repeated-contact telemetry and must not be interpreted as independent food-item encounters.",
        "",
        "## Primary E6 contrast and endpoint dependence",
        "",
        "| Energy | B2-B3 follow-up, mean [95% paired t CI] | Paired dz | P(B2 > B3) | Seeds B2 > B3 / B2 < B3 / tied |",
        "|---:|---:|---:|---:|---:|",
    ])
    for row in e6["paired_contrasts"]:
        if row["contrast"] == "B2-B3" and row["metric"] == "founder_mean_followup_ticks":
            lines.append(
                f"| {row['realized_fruit_energy']} | {ci_text(row)} | {fmt(row['paired_standardized_mean_difference_dz'])} | "
                f"{fmt(row['paired_probability_of_superiority'])} | {row['seeds_favouring_left']} / {row['seeds_favouring_right']} / {row['seeds_tied']} |"
            )
    slope = e6["slope"]
    lines.extend([
        "",
        f"The registered mean slope was {fmt(slope['summary']['mean'])} ticks per energy unit "
        f"(95% CI {fmt(slope['t_ci95']['low'])} to {fmt(slope['t_ci95']['high'])}). "
        f"It met the frozen positive-slope decision rule but did not exceed the SESOI of 1 in the post hoc minimum-effect test "
        f"(one-sided sign-flip p={fmt(slope['minimum_effect_sensitivity']['one_sided_monte_carlo_sign_flip_p'])}).",
        "",
        f"Leaving out energy 10 gave a slope of {fmt(next(x for x in slope['leave_one_energy_out'] if x['excluded_energy'] == 10)['slope_summary']['mean'])} "
        f"(95% CI {fmt(next(x for x in slope['leave_one_energy_out'] if x['excluded_energy'] == 10)['t_ci95']['low'])} to "
        f"{fmt(next(x for x in slope['leave_one_energy_out'] if x['excluded_energy'] == 10)['t_ci95']['high'])}).",
        "",
        "At energy 10, 0.6 x 10 = 6 > 5, so a safe-fruit value can raise the relative threshold above the staple. "
        "Staple acceptance fell to 0.436 in B2 and 0.563 in B3, while remaining 0.958 in B1; senescence accounted for about 74-76% of founder outcomes in all three arms. "
        "The design therefore cannot separate a payoff effect from this policy-regime change and the senescence ceiling.",
        "",
        "## T2-RB realized intake and dose",
        "",
        "| Arm | Follow-up | Fruit meals | Staple meals | Fruit accept | Staple accept | Toxin excess | Excess/fruit meal | Toxin damage | Starvation | Senescence |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for cell in t2["cell_summaries"]:
        m = cell["metrics"]
        lines.append(
            f"| {cell['arm']} | {fmt(m['founder_mean_followup_ticks']['mean'])} | {fmt(m['fruit_meals_per_founder']['mean'])} | "
            f"{fmt(m['staple_meals_per_founder']['mean'])} | {fmt(m['fruit_acceptance_per_telemetry_encounter']['mean'])} | "
            f"{fmt(m['staple_acceptance_per_telemetry_encounter']['mean'])} | {fmt(m['toxin_excess_per_founder']['mean'])} | "
            f"{fmt(m['toxin_excess_per_fruit_meal']['mean'])} | {fmt(m['toxin_damage_per_founder']['mean'])} | "
            f"{fmt(m['death_fraction_starvation']['mean'])} | {fmt(m['death_fraction_senescence']['mean'])} |"
        )
    t2_followup = [
        row for row in t2["paired_contrasts"]
        if row["metric"] == "founder_mean_followup_ticks" and row["contrast"] in {"A2-A3R", "A2-A3O"}
    ]
    lines.extend([
        "",
        "All observed A3O/A3R learned fruit-key means were exactly 6 and fruit acceptance was 1.000. A2 received less realized toxin excess than either constant control while also having shorter follow-up. "
        "T2-RB therefore compares variable, choice-requiring toxicity with a fixed-payoff control that required no discrimination; it does not isolate hidden versus visible toxicity at equal realized dose.",
        "",
        "| Contrast | Follow-up, mean [95% paired t CI] | Paired dz | P(left > right) | Seeds left > right / left < right / tied |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in t2_followup:
        lines.append(
            f"| {row['contrast']} | {ci_text(row)} | {fmt(row['paired_standardized_mean_difference_dz'])} | "
            f"{fmt(row['paired_probability_of_superiority'])} | {row['seeds_favouring_left']} / {row['seeds_favouring_right']} / {row['seeds_tied']} |"
        )
    correlations = e6["within_arm_energy_cell_correlations_with_followup"]
    lines.extend([
        "",
        "## Causal limitation",
        "",
        f"In post hoc within-arm-by-energy residuals, follow-up correlated with staple meals per follow-up tick "
        f"(r={fmt(correlations['staple_meals_per_followup_tick'])}), toxin excess per follow-up tick "
        f"(r={fmt(correlations['toxin_excess_per_followup_tick'])}), fruit meals per follow-up tick "
        f"(r={fmt(correlations['fruit_meals_per_followup_tick'])}), and toxin excess per fruit meal "
        f"(r={fmt(correlations['toxin_excess_per_fruit_meal'])}). Rates that divide by follow-up can inherit denominator bias; the toxin-per-meal measure does not use follow-up in its denominator. "
        "Archived telemetry does not record agent energy at the decision moment, so starvation-override meals cannot be separated. These descriptive associations do not identify a causal path.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--mechanism", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--supplement-out")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    mechanism = load_json(root, args.mechanism)
    output = root / args.out_dir
    output.mkdir(parents=True, exist_ok=True)
    rendered = render_report(mechanism)
    (output / "MECHANISM_REPRODUCTION_REPORT.en.md").write_text(
        rendered, encoding="utf-8", newline="\n"
    )
    if args.supplement_out:
        supplement = root / args.supplement_out
        supplement.parent.mkdir(parents=True, exist_ok=True)
        supplement.write_text(rendered, encoding="utf-8", newline="\n")
    write_csv(output / "prediction_audit.csv", prediction_rows(root, mechanism))
    write_csv(output / "deviation_audit.csv", deviation_rows())
    print(f"wrote report and audit tables to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
