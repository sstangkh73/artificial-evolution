# Confirmatory evidence package

This directory contains the validated batch summaries, frozen primary analyses,
prespecified secondary summaries, figure source data, and publication figures for
the E6 and T2-RB confirmatory studies completed on 2026-09-14.

Both batches were generated from clean detached commit
`3f1af32f9e37655ed9bee5462526921eff226c8a`, identified by annotated tag
`prereg-resource-age-2026-09-14`. The embedded provenance records 450/450 E6
runs and 150/150 T2-RB runs with no failures or reused cells. The validators mark
both batches as confirmatory eligible.

The frozen narrative preregistration retains one stale checklist line saying the
JSON spec was still a draft. Its status header, both JSON specs, the hash
manifest, the tagged runner input, and the embedded run provenance all record
`PREREGISTERED_CONFIRMATORY_FROZEN`. The stale line is preserved rather than
silently editing the archived preregistration after results were known.

## Directory map

- `e6/E6_runs.json`: 450-row batch summary with embedded frozen spec and provenance
- `e6/E6_validation.json`: complete-design and provenance validation
- `e6/E6_analysis.json`: preregistered primary seed-level slope analysis
- `e6/E6_secondary_and_mechanism.json`: prespecified level summaries and mechanism gates, plus explicitly post hoc sensitivity
- `t2rb/T2RB_runs.json`: 150-row batch summary
- `t2rb/T2RB_validation.json`: complete-design and provenance validation
- `t2rb/T2RB_analysis.json`: preregistered primary and direct-replication contrasts
- `source_data/`: one row per independent seed-level observation used in the figures
- `figures/`: 300-dpi PNG and vector PDF outputs
- `checksums.sha256`: SHA-256 inventory for these artifacts and all 600 raw dumps

The 600 raw dumps are stored outside this Git package under
`data/confirmatory_resource_age_2026-09-14/` (218.99 MiB). Archive those files
with this directory and verify the hashes before publication.

## Regenerate analysis artifacts

Run from the repository root after checking out the preregistered code or a
documented later analysis revision:

```powershell
python scripts\validate_e_series_batch.py --runs reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_runs.json --out reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_validation.json
python scripts\analyze_e6_representation_payoff.py --runs reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_runs.json --out reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_analysis.json
python scripts\summarize_resource_age_confirmatory.py --e6-runs reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_runs.json --out reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_secondary_and_mechanism.json
python scripts\validate_e_series_batch.py --runs reports\publication_value_of_information_2026-09-13\confirmatory\t2rb\T2RB_runs.json --out reports\publication_value_of_information_2026-09-13\confirmatory\t2rb\T2RB_validation.json
python scripts\analyze_t2rb_replication.py --runs reports\publication_value_of_information_2026-09-13\confirmatory\t2rb\T2RB_runs.json --out reports\publication_value_of_information_2026-09-13\confirmatory\t2rb\T2RB_analysis.json
python scripts\plot_resource_age_confirmatory.py --e6-runs reports\publication_value_of_information_2026-09-13\confirmatory\e6\E6_runs.json --t2-runs reports\publication_value_of_information_2026-09-13\confirmatory\t2rb\T2RB_runs.json --out-dir reports\publication_value_of_information_2026-09-13\confirmatory
python scripts\build_confirmatory_checksums.py --root . --out reports\publication_value_of_information_2026-09-13\confirmatory\checksums.sha256 --refresh-existing
```

The checksum builder excludes its output file, so rerunning it does not create a
self-referential entry.
