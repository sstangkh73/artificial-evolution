# Independent Reproduction Protocol

## Purpose

This protocol lets a person who did not produce the confirmatory data test the executable pipeline without rerunning the full 600-run study. It runs all 18 frozen confirmatory arm configurations for one reserved, non-confirmatory seed per design and compares every stable output field with a deterministic expected signature.

Passing this protocol is evidence that the released code, environment, arm construction, telemetry, and outcome extraction reproduce the archived smoke result. It is not a new inferential replicate and its outcomes must not be added to E6 or T2-RB.

## Required release contents

- a versioned repository checkout containing the frozen tag `prereg-resource-age-2026-09-14`;
- Python 3.14.3, the version recorded for the original batches;
- the two `*_SMOKE_spec.json` files under `reports/prereg`;
- `scripts/run_e_series.py` and `scripts/verify_reproduction_smoke.py`;
- `supplement/reproduction_smoke_expected.json`.

The verifier accepts a later documentation/release commit only when Git confirms that its focal simulation files are identical to frozen revision `3f1af32f9e37655ed9bee5462526921eff226c8a`.

## Procedure

Start from a fresh clone or extracted release in a new directory. Do not copy prior smoke outputs into it.

```powershell
git status --short
git tag --verify prereg-resource-age-2026-09-14
python --version
python -m unittest discover -s tests -v
python scripts\run_e_series.py --spec reports\prereg\E6_representation_payoff_SMOKE_spec.json --work-dir reproduction\data\e6 --out-dir reproduction\reports\e6 --jobs 1
python scripts\run_e_series.py --spec reports\prereg\T2_RB_replication_SMOKE_spec.json --work-dir reproduction\data\t2rb --out-dir reproduction\reports\t2rb --jobs 1
python scripts\verify_reproduction_smoke.py --e6-runs reproduction\reports\e6\E6SMOKE_runs.json --t2-runs reproduction\reports\t2rb\T2RBSMOKE_runs.json --out reproduction\reproduction_verification.json
```

Use `--jobs 1` for the reference check so process scheduling and Windows sandbox permissions do not create avoidable differences. Do not use `--resume` or `--allow-dirty`. The smoke specs are explicitly labeled non-confirmatory and do not need `--allow-draft`.

## Pass criteria

The final command must exit 0 and write `"status": "PASS"`. It checks:

- clean, unchanged Git revision throughout each batch;
- focal simulation code identical to the frozen revision;
- 15 E6 rows and 3 T2-RB rows, with the reserved seeds and a 200-tick requested horizon;
- no failures and no reused dumps;
- the complete normalized row signature, including flags, realized food energies, endpoints, encounters, discrimination, damage, and survival fields.

Only the machine-dependent dump paths and wall-clock seconds are excluded from the signature.

## Reproducer record

The independent reproducer should add the following information to `reproduction_verification.json` or a signed companion note:

- name or persistent identifier;
- affiliation, if any;
- date and time zone;
- operating system and Python version;
- repository release URL/DOI and commit;
- exact commands used;
- whether any package or command change was necessary;
- the verifier output and SHA-256 hash of that output.

Until another person completes and signs this record, the project may state that two internal clean-worktree runs were deterministic, but must not state that independent reproduction has been completed.
