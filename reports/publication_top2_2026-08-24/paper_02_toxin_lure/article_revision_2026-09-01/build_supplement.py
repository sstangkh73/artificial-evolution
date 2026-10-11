from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACKAGE = HERE / "supplementary_material"
SOURCE_DATA = ROOT / "reports" / "publication_top2_2026-08-24" / "source_data"
RAW_RUNS = ROOT / "data" / "multiseed"
FROZEN_TOXIN = HERE.parent / "revision_2026-09-01" / "supplementary_material"
ANALYSIS = ROOT / "scripts" / "prepare_top_two_publication_stats.py"
ZIP_PATH = HERE / "Injun_Artificial_Ecology_Article_Supplement.zip"
GENERATED_DIRS = (
    PACKAGE / "source_data",
    PACKAGE / "study_1_raw_runs",
    PACKAGE / "analysis",
    PACKAGE / "study_2_frozen",
)


def copy_inputs() -> None:
    # Rebuild generated content from a clean state so stale test caches or files
    # from an earlier package cannot leak into a submission archive.
    for directory in GENERATED_DIRS:
        if directory.exists():
            shutil.rmtree(directory)

    (PACKAGE / "source_data").mkdir(parents=True, exist_ok=True)
    (PACKAGE / "study_1_raw_runs").mkdir(parents=True, exist_ok=True)
    (PACKAGE / "analysis").mkdir(parents=True, exist_ok=True)

    for path in sorted(SOURCE_DATA.iterdir()):
        if path.is_file():
            shutil.copy2(path, PACKAGE / "source_data" / path.name)
    for pattern in ("A_*.json", "B_*.json"):
        for path in sorted(RAW_RUNS.glob(pattern)):
            shutil.copy2(path, PACKAGE / "study_1_raw_runs" / path.name)
    shutil.copy2(ANALYSIS, PACKAGE / "analysis" / ANALYSIS.name)
    shutil.copytree(
        FROZEN_TOXIN,
        PACKAGE / "study_2_frozen",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest() -> None:
    manifest = PACKAGE / "SHA256SUMS.txt"
    lines = []
    for path in sorted(PACKAGE.rglob("*")):
        if path.is_file() and path != manifest:
            lines.append(f"{sha256(path)}  {path.relative_to(PACKAGE).as_posix()}")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_zip() -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, Path("supplementary_material") / path.relative_to(PACKAGE))


if __name__ == "__main__":
    copy_inputs()
    write_manifest()
    write_zip()
    print(ZIP_PATH)
