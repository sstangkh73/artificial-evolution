# Figure and source-data manifest

All manuscript figures are available as 300-dpi PNG and vector PDF. Plotted points are seed-level values. Error bars are descriptive 95% t intervals; registered inference remains in the experiment analysis JSON files and manuscript text.

| Manuscript figure | Files | Source data | Generator |
|---|---|---|---|
| Figure 1: hidden toxicity | `figures/figure_1_hidden_toxicity.{png,pdf}` | `source_data/e1_seed_outcomes.csv` | `scripts/plot_publication_core_studies.py` |
| Figure 2: information rescue | `figures/figure_2_information_rescue.{png,pdf}` | `source_data/e2_seed_outcomes.csv` | `scripts/plot_publication_core_studies.py` |
| Figure 3: selection and denominator | `figures/figure_3_selection_and_denominator.{png,pdf}` | `source_data/e3_seed_selection.csv`; `source_data/e4_seed_behavior.csv` | `scripts/plot_publication_core_studies.py` |
| Figure 4: energy gradient | `figures/figure_e6_energy_gradient.{png,pdf}` | `source_data/e6_seed_by_energy.csv`; `source_data/e6_energy_summary.csv` | `scripts/plot_resource_age_confirmatory.py` |
| Figure 5: R-B replication | `figures/figure_t2rb_replication.{png,pdf}` | `source_data/t2rb_seed_contrasts.csv`; `source_data/t2rb_contrast_summary.csv` | `scripts/plot_resource_age_confirmatory.py` |

## Generation commands

Run from the repository root:

```powershell
python scripts/plot_publication_core_studies.py --out-dir reports/publication_value_of_information_2026-09-13/confirmatory
python scripts/plot_resource_age_confirmatory.py --e6-runs reports/publication_value_of_information_2026-09-13/confirmatory/e6/E6_runs.json --t2-runs reports/publication_value_of_information_2026-09-13/confirmatory/t2rb/T2RB_runs.json --out-dir reports/publication_value_of_information_2026-09-13/confirmatory
```

The Figure 3 exporter reads the archived E4 per-run dumps because `E4_runs.json` does not contain the per-agent age-bin encounter buckets. It verifies for every run that telemetry `seen = ate + skipped` and that telemetry `ate` equals the raw-meal total. This is why the figure uses 26,945.3 mean telemetry-deduplicated encounters rather than the slightly larger count of low-level skip calls.
