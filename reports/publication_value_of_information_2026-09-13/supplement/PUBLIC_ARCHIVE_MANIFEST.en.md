# Public archive manifest

## Purpose and status

This manifest defines the evidence and code that should accompany the article *When Does a Better Representation Pay? Survival Effects of Resource-Age Information in Artificial Foraging Under Temporal Toxicity*. It is a release plan, not evidence that a public deposit already exists. The archive DOI, landing-page URL, and final release commit or tag remain blank until the author deposits the package and verifies the downloaded copy.

The machine-readable inventory is `publication_release_inventory.json`. Its flat companion file, `publication_release_checksums.sha256`, permits standard SHA-256 verification. Both are generated and checked by `scripts/build_publication_release_inventory.py`.

## Release bundles

### 1. Confirmatory raw data — CC BY 4.0

- 450 E6 raw JSON dumps: 15 arms × 30 registered seeds.
- 150 T2-RB raw JSON dumps: 3 arms × 50 registered seeds.
- Expected total: 600 files.

These files preserve the generated metadata, effective parameter values, outcomes, telemetry, failure status, and Git provenance used by the validators and analyses. They were produced from commit `3f1af32f9e37655ed9bee5462526921eff226c8a`, frozen by annotated tag `prereg-resource-age-2026-09-14`.

### 2. Derived evidence — CC BY 4.0

This bundle contains the validated E6 and T2-RB summaries, analysis JSON, source-data tables, all five publication figures in vector PDF and preview PNG, the figure manifest, the confirmatory README, and the original `confirmatory/checksums.sha256`.

The original checksum file has a deliberately narrower historical scope: 600 raw dumps plus 16 E6/T2-RB derived artifacts. It has 616 entries and does not cover Figures 1–3, E1–E4 source tables, or later supplements. The release-level inventory fixes that gap while preserving the original manifest unchanged as an audit record.

### 3. Manuscript and methods — CC BY 4.0

This bundle contains the manuscript, ODD model description, references, AI-use log, report README, parameter tables and their machine-readable provenance, state-variable catalogue, code-version audit, reproduction protocol, deterministic reference signatures, internal verification record, and this public-archive manifest.

### 4. Frozen preregistration — CC BY 4.0

This bundle contains the frozen E6 and T2-RB confirmatory specifications, the corresponding clean-worktree smoke specifications, and the preregistration hash manifest.

### 5. Code and tests — MIT

This bundle contains the focal agent, environment, metabolism, and simulation modules; the experiment driver and runner; validation, analysis, figure, parameter, checksum, inventory, and reproduction scripts; and the regression tests needed to audit those pathways. `requirements.txt` records the runtime dependency statement.

## Deliberate exclusions

The release excludes exploratory E6 pilot and pilot-rerun directories, failed or superseded calibration outputs, PID and log files, temporary directories, unrelated experiments and reports, third-party papers under `papers/`, local application PDFs, the draft cover letter, formatted submission drafts, and submission-administration checklists. These files do not support the article's reported quantitative claims or cannot be redistributed under the repository's research-data licence.

The independent-reproduction protocol and internal deterministic check are included. A second person's signed execution record must be added only after that person actually completes the protocol. Internal repeatability must not be relabeled as independent reproduction.

## Build and local verification

From the repository root, with all 600 raw dumps restored at their recorded paths:

```powershell
python scripts\build_publication_release_inventory.py --write
python scripts\build_publication_release_inventory.py --verify
python scripts\build_publication_release_archives.py --write
python scripts\build_publication_release_archives.py --verify
```

The build first verifies every entry in the original 616-entry confirmatory checksum file and enforces the registered raw-file counts. It then hashes every release file, writes deterministic JSON and flat SHA-256 inventories, and excludes both generated inventory outputs from self-reference. The current local release contains 695 files. Verification checks the selected scope, file sizes, hashes, duplicate paths, and agreement between the JSON and flat checksum forms.

The archive builder creates five deterministically ordered ZIP files under `output/publication_release_2026-09-14/`, copies the two release-control files, and writes a deposit README plus package-level JSON and SHA-256 records. Its verifier decompresses and hashes every member, checks ZIP CRCs, compares every member against the release inventory, and verifies all package-level artifacts. The generated upload directory is intentionally not committed to Git.

## Deposit and download-back gate

Before citing the archive in the manuscript:

1. Tag the final release commit after manuscript and disclosure approval.
2. Create the public deposit with the five bundles above, both licences, author and title metadata, and version information.
3. Record the archive DOI, landing-page URL, and final release commit or tag in `publication_release_inventory.json`, this document, the manuscript Data and Code Availability statement, and the cover letter.
4. Download the deposited files into a clean directory.
5. Verify `publication_release_checksums.sha256` against the downloaded content and run the inventory verifier from the matching code release.
6. Open every PDF and a sample of JSON/CSV files from the downloaded copy before marking the archive gate complete.

Until these steps are completed, the manuscript must say that the archive is pending and must not display a placeholder as if it were a live DOI.
